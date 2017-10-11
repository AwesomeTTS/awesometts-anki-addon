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

"""Youdao Dictionary"""

from .base import Service
from .common import Trait

__all__ = ['Youdao']


VOICE_CODES = [
    ('en-GB', ("English, British", 1)),
    ('en-US', ("English, American", 2)),
    ('en', ("English, alternative", 3)),
]

VOICE_LOOKUP = dict(VOICE_CODES)


class Youdao(Service):
    """Provides a Service implementation for Youdao Dictionary."""

    __slots__ = []

    NAME = "Youdao Dictionary"

    TRAITS = [Trait.INTERNET]

    def desc(self):
        """Returns a static description."""

        return "Youdao (American and British English)"

    def options(self):
        """Returns an option to select the voice."""

        voice_lookup = dict([
            (self.normalize(alias), 'en-GB')
            for alias in ['en-EU', 'en-UK']
        ] + [
            (self.normalize(alias), 'en')
            for alias in ['English', 'en', 'eng']
        ] + [
            (self.normalize(code), code)
            for code in VOICE_LOOKUP.keys()
        ])

        def transform_voice(value):
            """Normalize and attempt to convert to official code."""

            normalized = self.normalize(value)
            return (voice_lookup[normalized]
                    if normalized in voice_lookup else value)

        return [
            dict(
                key='voice',
                label="Voice",
                values=[(key, description)
                        for key, (description, _) in VOICE_CODES],
                transform=transform_voice,
                default='en-US',
            ),
        ]

    def run(self, text, options, path):
        """Downloads from dict.youdao.com directly to an MP3."""

        self.net_download(
            path,
            [
                ('http://dict.youdao.com/dictvoice', dict(
                    audio=subtext,
                    type=VOICE_LOOKUP[options['voice']][1],
                ))
                for subtext in self.util_split(text, 1000)
            ],
            require=dict(mime='audio/mpeg', size=256),
            add_padding=True,
        )
