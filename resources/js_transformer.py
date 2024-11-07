# Copyright (c) 2024 Renata Hodovan, Akos Kiss.
#
# Licensed under the BSD 3-Clause License
# <LICENSE.rst or https://opensource.org/licenses/BSD-3-Clause>.
# This file may not be copied, modified, or distributed except
# according to those terms.

from grammarinator.runtime import ParentRule, UnlexerRule


def remove_asserts(node):
    """
    Simple transformer to replace ``assert`` function calls to
    ``print`` in the JavaScript population items to avoid continuous
    crashes.
    """
    if isinstance(node, ParentRule):
        for child in node.children:
            remove_asserts(child)
    elif isinstance(node, UnlexerRule) and node.src == 'assert':
        node.src = 'print'
    return node
