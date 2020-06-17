# -*- coding: utf-8 -*-

# AwesomeTTS text-to-speech add-on for Anki
# Copyright (C) 2010-Present  Anki AwesomeTTS Development Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Helpful type conversions
"""

import json
import re

from PyQt5.QtCore import Qt

__all__ = ['compact_json', 'deserialized_dict', 'lax_bool',
           'normalized_ascii', 'nullable_key', 'nullable_int',
           'substitution_compiled', 'substitution_json', 'substitution_list']


def compact_json(obj):
    """Given an object, return a minimal JSON-encoded string."""

    return json.dumps(obj, separators=compact_json.SEPARATORS)

compact_json.SEPARATORS = (',', ':')


def deserialized_dict(json_str):
    """
    Given a JSON string, returns a dict. If the input is invalid or
    does not have an object at the top-level, returns an empty dict.
    """

    if isinstance(json_str, dict):
        return json_str

    try:
        obj = json.loads(json_str)
    except Exception:
        return {}

    return obj if isinstance(obj, dict) else {}


def lax_bool(value):
    """
    Like bool(), but correctly returns False for '0', 'false', and
    similar strings.
    """

    if isinstance(value, str):
        value = value.strip().strip('-0').lower()
        return value not in lax_bool.FALSE_STRINGS

    return bool(value)

lax_bool.FALSE_STRINGS = ['', 'false', 'no', 'off', 'unset']


def normalized_ascii(value):
    """
    Returns a plain ASCII string containing only lowercase
    alphanumeric characters from the given value.
    """
    value = value.encode('ascii', 'ignore').decode()

    # TODO: .isalnum() could be used here, but it is not equivalent
    return ''.join(char.lower()
                   for char in value
                   if char.isalpha() or char.isdigit())


def nullable_key(value):
    """
    Returns an instance of PyQt5.QtCore.Qt.Key for the given value, if
    possible. If the incoming value cannot be represented as a key,
    returns None.
    """

    if isinstance(value, Qt.Key):
        return value

    value = nullable_int(value)
    return Qt.Key(value) if value else None


def nullable_int(value):
    """
    Returns an integer for the given value, if possible. If the incoming
    value cannot be represented as an integer, returns None.
    """

    try:
        return int(value)
    except Exception:
        return None


def substitution_compiled(rule):
    """
    Given a substitution rule, returns a compiled matcher object using
    re.compile(). Because advanced substitutions execute after all
    whitespace is collapsed, neither re.DOTALL nor re.MULTILINE need to
    be supported here.
    """

    assert rule['input'], "Input pattern may not be empty"
    return re.compile(
        pattern=rule['input'] if rule['regex'] else re.escape(rule['input']),
        flags=sum(
            value
            for key, value in substitution_compiled.FLAGS
            if rule[key]
        ),
    )

substitution_compiled.FLAGS = [('ignore_case', re.IGNORECASE),
                               ('unicode', re.UNICODE)]


def substitution_json(rules):
    """
    Given a list of substitution rules, filters out the compiled member
    from each rule and returns the list serialized as JSON.
    """

    return (
        compact_json([
            {
                key: value
                for key, value
                in item.items()
                if key != 'compiled'
            }
            for item in rules
        ])
        if rules and isinstance(rules, list)
        else '[]'
    )


def substitution_list(json_str):
    """
    Given a JSON string, returns a list of valid substitution rules with
    each rule's 'compiled' member instantiated.
    """

    try:
        candidates = json.loads(json_str)
        if not isinstance(candidates, list):
            raise ValueError

    except Exception:
        return []

    rules = []

    for candidate in candidates:
        if not ('replace' in candidate and
                isinstance(candidate['replace'], str)):
            continue

        for key, default in substitution_list.DEFAULTS:
            if key not in candidate:
                candidate[key] = default

        try:
            candidate['compiled'] = substitution_compiled(candidate)
        except Exception:  # sre_constants.error, pylint:disable=broad-except
            continue

        rules.append(candidate)

    return rules

substitution_list.DEFAULTS = [('regex', False), ('ignore_case', True),
                              ('unicode', True)]
