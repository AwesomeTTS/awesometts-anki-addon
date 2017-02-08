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
Service implementation for Wiktionary single word pronunciations
"""

import re

from .base import Service
from .common import Trait

__all__ = ['Wiktionary']


RE_NONWORD = re.compile(r'\W+', re.UNICODE)
DEFINITE_ARTICLES = ['das', 'der', 'die', 'el', 'gli', 'i', 'il', 'l', 'la',
                     'las', 'le', 'les', 'lo', 'los', 'the']

TEXT_SPACE_LIMIT = 1
TEXT_LENGTH_LIMIT = 75


class Wiktionary(Service):
    """
    Provides a Service-compliant implementation for Wiktionary
    """

    __slots__ = [
    ]

    NAME = "Wiktionary"

    TRAITS = [Trait.INTERNET]

    # In order of size as of Nov 6 2016
    _LANGUAGE_CODES = {
        'en': 'English', 'mg': 'Malagasy', 'fr': 'French',
        'sh': 'Serbo-Croatian', 'es': 'Spanish', 'zh': 'Chinese',
        'ru': 'Russian', 'lt': 'Lithuanian', 'de': 'German',
        'nl': 'Dutch', 'sv': 'Swedish', 'pl': 'Polish',
        'ku': 'Kurdish', 'el': 'Greek', 'it': 'Italian',
        'ta': 'Tamil', 'tr': 'Turkish', 'hu': 'Hungarian',
        'fi': 'Finnish', 'ko': 'Korean', 'io': 'Ido',
        'kn': 'Kannada', 'vi': 'Vietnamese', 'ca': 'Catalan',
        'pt': 'Portuguese', 'chr': 'Cherokee', 'sr': 'Serbian',
        'hi': 'Hindi', 'ja': 'Japanese', 'hy': 'Armenian',
        'ro': 'Romanian', 'no': 'Norwegian', 'th': 'Thai',
        'ml': 'Malayalam', 'id': 'Indonesian', 'et': 'Estonian',
        'uz': 'Uzbek', 'li': 'Limburgish', 'my': 'Burmese',
        'or': 'Oriya', 'te': 'Telugu',
    }

    def __init__(self, *args, **kwargs):
        if self.IS_MACOSX:
            raise EnvironmentError(
                "Wiktionary cannot be used on Mac OS X due to mplayer "
                "crashes while converting the audio. If you are able to fix "
                "this, please send a pull request."
            )

        super(Wiktionary, self).__init__(*args, **kwargs)

    def desc(self):
        """
        Returns a short, static description.
        """

        return "Wiktionary single word translations"

    def options(self):
        """
        Provides access to different language versions of Wiktionary.
        """

        return [
            dict(
                key='voice',
                label="Voice",
                values=[(code, "%s" % (name))
                        for code, name in sorted(self._LANGUAGE_CODES.items(),
                                                 key=lambda x: x[1])],
                transform=lambda x: x,
            ),
        ]

    def modify(self, text):
        """
        Remove punctuation but leave case as-is (sometimes it matters).

        If the input is multiple words and the first word is a definite
        article, drop it.
        """

        text = RE_NONWORD.sub('_', text).replace('_', ' ').strip()

        tokenized = text.split(' ', 1)
        if len(tokenized) == 2:
            first, rest = tokenized
            if first in DEFINITE_ARTICLES:
                return rest

        return text

    def run(self, text, options, path):
        """
        Downloads from Wiktionary directly to an OGG, and then
        converts to MP3.

        Many words (and all phrases) are not listed on Wiktionary.
        Thus, this will fail often.
        """

        if text.count(' ') > TEXT_SPACE_LIMIT:
            raise IOError("Wiktionary does not support phrases")
        elif len(text) > TEXT_LENGTH_LIMIT:
            raise IOError("Wiktionary only supports short input")

        # Execute search using the text *as is* (i.e. no lowercasing) so that
        # Wiktionary can pick the best page (i.e. decide whether case matters)
        webpage = self.net_stream(
            (
                'https://%s.wiktionary.org/w/index.php' % options['voice'],
                dict(
                    search=text,
                    title='Special:Search',
                ),
            ),
            require=dict(mime='text/html'),
        )

        # Now parse the page, looking for the ogg file.  This will
        # find at most one match, as we expect there to be no more
        # than one pronunciation on the wiktionary page for any
        # given word.  This is sometimes violated if the word has
        # multiple pronunciations, but since there is no trivial
        # way to choose between them, this should be good enough
        # for now.
        matcher = re.search("//.*\\.ogg", webpage)
        if not matcher:
            raise IOError("Wiktionary doesn't have any audio for this input.")
        oggurl = "https:" + matcher.group(0)

        ogg_path = self.path_temp('ogg')
        wav_path = self.path_temp('wav')

        try:
            self.net_download(ogg_path, oggurl,
                              require=dict(mime='application/ogg', size=1024))
            self.net_dump(wav_path, ogg_path)
            self.cli_transcode(wav_path, path)

        finally:
            self.path_unlink(ogg_path, wav_path)
