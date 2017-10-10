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
Service implementation for the Collins Dictionary
"""

import re

from .base import Service
from .common import Trait

__all__ = ['Collins']


BASE_PATTERN = r'data-src-mp3="(?:https://www.collinsdictionary.com)(/sounds/[\w/]+/%s\w*\.mp3)"'
RE_ANY_SPANISH = re.compile(BASE_PATTERN % r'es_')

MAPPINGS = [
    ('en', "English", 'english', [re.compile(BASE_PATTERN % r'\d+')]),
    ('fr', "French", 'french-english', [re.compile(BASE_PATTERN % r'fr_')]),
    ('de', "German", 'german-english', [re.compile(BASE_PATTERN % r'de_')]),
    ('es-419', "Spanish, prefer Americas", 'spanish-english',
     [re.compile(BASE_PATTERN % r'es_419_'), RE_ANY_SPANISH]),
    ('es-es', "Spanish, prefer European", 'spanish-english',
     [re.compile(BASE_PATTERN % r'es_es_'), RE_ANY_SPANISH]),
    ('it', "Italian", 'italian-english', [re.compile(BASE_PATTERN % r'it_')]),
    ('zh', "Chinese", 'chinese-english', [re.compile(BASE_PATTERN % r'zh_')]),
]

LANG_TO_DICTCODE = {lang: dictcode for lang, _, dictcode, _ in MAPPINGS}
LANG_TO_REGEXPS = {lang: regexps for lang, _, _, regexps in MAPPINGS}
DEFAULT_LANG = 'en'

RE_NONWORD = re.compile(r'\W+', re.UNICODE)
DEFINITE_ARTICLES = ['das', 'der', 'die', 'el', 'gli', 'i', 'il', 'l', 'la',
                     'las', 'le', 'les', 'lo', 'los', 'the']

TEXT_SPACE_LIMIT = 1
TEXT_LENGTH_LIMIT = 75
COLLINS_WEBSITE = 'http://www.collinsdictionary.com'
SEARCH_FORM = COLLINS_WEBSITE + '/search/'
RE_MP3_URL = re.compile(r'<a[^>]+class="[^>"]*hwd_sound[^>"]*"[^>]+'
                        r'data-src-mp3="(/[^>"]+)"[^>]*>')
REQUIRE_MP3 = dict(mime='audio/mpeg', size=256)


class Collins(Service):
    """Provides a Service-compliant implementation for Collins."""

    __slots__ = []

    NAME = "Collins"

    TRAITS = [Trait.INTERNET, Trait.DICTIONARY]

    def desc(self):
        """Returns a short, static description."""

        return "Collins Dictionary (%d languages); single words and " \
            "two-word phrases only with fuzzy matching" % len(MAPPINGS)

    def options(self):
        """Provides access to voice only."""

        voice_lookup = dict([(self.normalize(desc), lang)
                             for lang, desc, _, _ in MAPPINGS] +
                            [(self.normalize(lang), lang)
                             for lang, _, _, _ in MAPPINGS])

        return [
            dict(
                key='voice',
                label="Voice",
                values=[(lang, desc) for lang, desc, _, _ in MAPPINGS],
                transform=lambda value: voice_lookup.get(self.normalize(value),
                                                         value),
                default=DEFAULT_LANG,
            ),
        ]

    def modify(self, text):
        """
        Remove punctuation and return as lowercase.

        If the input is multiple words and the first word is a definite
        article, drop it.
        """

        text = RE_NONWORD.sub('_', text).replace('_', ' ').strip().lower()

        tokenized = text.split(' ', 1)
        if len(tokenized) == 2:
            first, rest = tokenized
            if first in DEFINITE_ARTICLES:
                return rest

        return text

    def run(self, text, options, path):
        """Find audio filename and then download it."""

        if text.count(' ') > TEXT_SPACE_LIMIT:
            raise IOError("The Collins Dictionary does not support phrases")
        elif len(text) > TEXT_LENGTH_LIMIT:
            raise IOError("The Collins Dictionary only supports short input")

        voice = options['voice']

        payload = self.net_stream(
            (SEARCH_FORM, dict(q=text, dictCode=LANG_TO_DICTCODE[voice])),
            method='GET',
        ).decode()

        for regexp in LANG_TO_REGEXPS[voice]:
            self._logger.debug("Collins: trying pattern %s", regexp.pattern)

            match = regexp.search(payload)
            if match:
                self.net_download(path,
                                  COLLINS_WEBSITE + match.group(1),
                                  require=REQUIRE_MP3)
                break

        else:
            raise IOError("Cannot find any recorded audio in Collins "
                          "dictionary for this input.")
