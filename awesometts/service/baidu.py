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
Service implementation for Baidu Translate's text-to-speech API
"""

from .base import Service
from .common import Trait

__all__ = ['Baidu']


VOICES = {
    'en': "English, American",
    'jp': "Japanese",
    'pt': "Portuguese",
    # returns error -- 'spa': "Spanish",
    'th': "Thai",
    'uk': "English, British",
    'zh': "Chinese",
}


class Baidu(Service):
    """
    Provides a Service-compliant implementation for Baidu Translate.
    """

    __slots__ = []

    NAME = "Baidu Translate"

    TRAITS = [Trait.INTERNET]

    def desc(self):
        """Returns a short, static description."""

        return "Baidu Translate text2audio web API (%d voices)" % len(VOICES)

    def options(self):
        """Provides access to voice only."""

        return [
            dict(
                key='voice',
                label="Voice",
                values=[(code, "%s (%s)" % (name, code))
                        for code, name
                        in sorted(VOICES.items(), key=lambda t: t[1])],
                transform=self.normalize,
            ),
        ]

    def run(self, text, options, path):
        """Downloads from Baidu directly to an MP3."""

        self.net_download(
            path,
            [
                ('http://tts.baidu.com/text2audio',
                 dict(text=subtext, lan=options['voice'], ie='UTF-8'))
                for subtext in self.util_split(text, 300)
            ],
            require=dict(mime='audio/mp3', size=512),
        )
