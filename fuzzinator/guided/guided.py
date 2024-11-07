# Copyright (c) 2024 Renata Hodovan, Akos Kiss.
#
# Licensed under the BSD 3-Clause License
# <LICENSE.rst or https://opensource.org/licenses/BSD-3-Clause>.
# This file may not be copied, modified, or distributed except
# according to those terms.

import glob
import json
import os
import subprocess

from math import inf
from os.path import abspath, dirname, exists, expanduser
from tempfile import TemporaryDirectory
from uuid import uuid4

from fuzzinator.call.call_decorator import CallDecorator
from fuzzinator.fuzzer import Fuzzer
from grammarinator.runtime import DefaultModel, RuleSize
from grammarinator.tool import DefaultGeneratorFactory, DefaultIndividual, DefaultPopulation, GeneratorTool
from inators.imp import import_object


def as_bool(s):
    if isinstance(s, bool):
        return s
    return s in [1, '1', 'True', 'true']


def import_list(lst):
    return [import_object(item) for item in lst]


class GuidedGrammarinatorAPI(Fuzzer):
    """
    Custom subclass of Fuzzinator's Fuzzer class which utilizes Grammarinator to produce new
    tests either by generating from scratch, or by mutating a single individual of the population,
    or by recombining two of them. It implements the feedback API of Fuzzinator to build a bridge
    between test execution and test generation, which can be used for guidance.
    """

    def __init__(self, *, generator=None, model=None, cooldown=1.0, weights=None, listeners=None,
                 rule=None, out_format=None,
                 max_depth=inf, max_tokens=inf,
                 population=None, enable_generation=True, enable_mutation=True, enable_recombination=True,
                 transformers=None, serializer=None,
                 encoding='utf-8', encoding_errors='strict', **kwargs):
        generator = import_object(generator)

        out_format = expanduser(out_format).format(uid=uuid4().hex)
        if out_format:
            os.makedirs(abspath(dirname(out_format)), exist_ok=True)

        if weights:
            if not exists(weights):
                raise ValueError('Custom weights should point to an existing JSON file.')

            with open(weights, 'r') as f:
                weights = {}
                for rule, alts in json.load(f).items():
                    for alternation_idx, alternatives in alts.items():
                        for alternative_idx, w in alternatives.items():
                            weights[(rule, int(alternation_idx), int(alternative_idx))] = w
                weights = weights
        else:
            weights = {}

        if population:
            population = expanduser(population)
            os.makedirs(population, exist_ok=True)
            self._population = CustomPopulation(abspath(population), 'grtp')
        else:
            self._population = None

        cooldown = float(cooldown)
        if cooldown <= 0.0 or cooldown > 1.0:
            raise ValueError(f'Cooldown value {cooldown!r} not in range (0.0, 1.0]')

        self.generator_tool = CustomGeneratorTool(generator_factory=DefaultGeneratorFactory(generator,
                                                                                            model_class=import_object(model) if model else DefaultModel,
                                                                                            cooldown=cooldown,
                                                                                            weights=weights,
                                                                                            listener_classes=import_list(listeners or [])),
                                                  rule=rule, out_format=out_format,
                                                  limit=RuleSize(float(max_depth), float(max_tokens)),
                                                  population=self._population,
                                                  generate=as_bool(enable_generation), mutate=as_bool(enable_mutation), recombine=as_bool(enable_recombination), keep_trees=False,
                                                  transformers=import_list(transformers or []), serializer=import_object(serializer) if serializer else None,
                                                  cleanup=False, encoding=encoding, errors=encoding_errors)

    def __call__(self, *, index):
        return self.generator_tool.create_test(index=index)

    def feedback(self, data):
        """
        Feedback API implementation for Fuzzinator. It creates
        connection between the SUT and the fuzzer by providing all the
        information collected by Fuzzinator during test execution to
        this method.

        :param dict data: Information collected during the last test execution.
        """
        if self._population is not None:
            self._population.update(data, self.generator_tool.current_root)


class CustomGeneratorTool(GeneratorTool):
    """
    Custom GeneratorTool subclass to save the newly created tree to access
    it later, e.g., to add to the population if it turned to be interesting.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_root = None

    def _create_tree(self, creators, individual1, individual2):
        self.current_root = super()._create_tree(creators, individual1, individual2)
        return self.current_root


class CustomPopulation(DefaultPopulation):
    """
    Class demonstrates a custom population implementation, that saves only
    those individuals that covered previously uncovered edges.
    """
    def __init__(self, directory, extension, codec=None):
        """
        :param str directory: Path to the population directory.
        :param str extension: Extension of the saved trees (without '.').
        :param ~grammarinator.tool.TreeCodec codec: Codec used to save trees into files.
        """
        super().__init__(directory, extension, codec)
        self.coverage = set()

    def update(self, test_data, root):
        """
        Save the last test if it covered new edges.

        :param dict test_data: Test execution data provided by Fuzzinator.
        :param Rule root: Root of the tree representation of the executed test.
        """
        # Use `pop()` to get coverage data from test_data to avoid saving it to
        # the issue database in case of finding a new issue.
        cov_diff = test_data.pop('coverage') - self.coverage
        if cov_diff:
            self.coverage.update(cov_diff)
            self.add_individual(root)
            print(f'NEW: {len(cov_diff)}, COV: {len(self.coverage)}, CORP: {len(self._files)}')


class ClangCoverageDecorator(CallDecorator):
    """
    Fuzzinator decorator to execute the SUT with ASAN coverage enabled and
    process the output .sancov file to get coverage data.
    DISCLAIMER: This is a **very** simple and slow way of measuring
    coverage. There are much more efficient solutions to do it, the
    current implementation is only for presentation purposes.
    """

    def call(self, cls, obj, *, test, **kwargs):
        try:
            with TemporaryDirectory() as cov_dir:
                obj.env['ASAN_OPTIONS'] = ':'.join(obj.env.get('ASAN_OPTIONS', '').split(':') + ['coverage=1', 'coverage_dir={coverage_dir}'.format(coverage_dir=cov_dir)])
                issue = super(cls, obj).__call__(test=test, **kwargs)
                if issue is None:
                    return None

                issue['coverage'] = {bit for fn in glob.glob(os.path.join(cov_dir, '*.*'))
                                     for bit in subprocess.check_output(['sancov', '-print', fn]).decode('utf-8').splitlines()}
                return issue
        except Exception as e:
            print('Exception in ClangCoverageDecorator', e)
