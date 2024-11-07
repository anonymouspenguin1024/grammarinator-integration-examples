# Copyright (c) 2024 Renata Hodovan, Akos Kiss.
#
# Licensed under the BSD 3-Clause License
# <LICENSE.rst or https://opensource.org/licenses/BSD-3-Clause>.
# This file may not be copied, modified, or distributed except
# according to those terms.

import json
import os

from math import inf
from os.path import abspath, dirname, exists, expanduser
from uuid import uuid4

from inators.imp import import_object
from fuzzinator.fuzzer import Fuzzer
from grammarinator.runtime import DefaultModel, RuleSize
from grammarinator.tool import DefaultGeneratorFactory, DefaultPopulation, GeneratorTool


def as_bool(s):
    if isinstance(s, bool):
        return s
    return s in [1, '1', 'True', 'true']


def import_list(lst):
    return [import_object(item) for item in lst]


class GrammarinatorAPI(Fuzzer):
    """
    Custom subclass of Fuzzinator's Fuzzer class which utilizes Grammarinator to produce new
    tests either by generating from scratch, or by mutating a single individual of the population,
    or by recombining two of them.
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

        cooldown = float(cooldown)
        if cooldown <= 0.0 or cooldown > 1.0:
            raise ValueError(f'Cooldown value {cooldown!r} not in range (0.0, 1.0]')

        self.generator_tool = GeneratorTool(generator_factory=DefaultGeneratorFactory(generator,
                                                                                      model_class=import_object(model) if model else DefaultModel,
                                                                                      cooldown=cooldown,
                                                                                      weights=weights,
                                                                                      listener_classes=import_list(listeners or [])),
                                            rule=rule, out_format=out_format,
                                            limit=RuleSize(float(max_depth), float(max_tokens)),
                                            population=DefaultPopulation(population, 'grtp') if population else None,
                                            generate=as_bool(enable_generation), mutate=as_bool(enable_mutation), recombine=as_bool(enable_recombination), keep_trees=False,
                                            transformers=import_list(transformers or []), serializer=import_object(serializer) if serializer else None,
                                            cleanup=False, encoding=encoding, errors=encoding_errors)

    def __call__(self, *, index):
        return self.generator_tool.create_test(index=index)
