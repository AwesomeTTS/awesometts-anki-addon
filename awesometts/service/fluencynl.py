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
Service implementation for Fluency.nl text-to-speech demo
"""

from urllib.parse import quote

from .base import Service
from .common import Trait

__all__ = ['FluencyNl']


VOICES = [
    # short value, API value, human-readable
    ('arno', 'Arno', "Arno (male)"),
    ('arthur', 'Arthur', "Arthur (male)"),
    ('marco', 'Marco', "Marco (male)"),
    ('rob', 'Rob', "Rob (male)"),
    ('janneke', 'Janneke', "Janneke (female)"),
    ('miriam', 'Miriam', "Miriam (female)"),
    ('david', 'Dav%EDd%20%2813%20jaar%29', "Davíd (male, 13)"),
    ('giovanni', 'Giovanni%20%2815%20jaar%29', "Giovanni (male, 15)"),
    ('koen', 'Koen%20%2814%20jaar%29', "Koen (male, 14)"),
    ('fiona', 'Fiona%20%2816%20jaar%29', "Fiona (female, 16)"),
    ('dirk', 'Dirk%20%28Vlaams%29', "Dirk (Flemish, male)"),
    ('linze', 'Linze%20%28Fries%29', "Linze (Frisian, male)"),
    ('siebren', 'Siebren%20%28Fries%29', "Siebren (Frisian, male)"),
    ('sjoukje', 'Sjoukje%20%28Fries%29', "Sjoukje (Frisian, female)"),
    ('sanghita', 'Sanghita%20%28Surinaams%29', "Sanghita (Sranan)"),
    ('fluisterste', 'Fluisterstem', "Fluisterstem"),
    ('arthur-m', 'Arthur%20%28MBROLA%29', "Arthur (male) [MBROLA]"),
    ('johan-m', 'Johan%20%28MBROLA%29', "Johan (male) [MBROLA]"),
    ('tom-m', 'Tom%20%28MBROLA%29', "Tom (male) [MBROLA]"),
    ('diana-m', 'Diana%20%28MBROLA%29', "Diana (female) [MBROLA]"),
    ('isabelle-m', 'Isabelle%20%28MBROLA%29', "Isabelle (female) [MBROLA]"),
    ('gekko-m', 'Gekko%20%28MBROLA%29', "Gekko [MBROLA]"),
]

VOICE_MAP = {voice[0]: voice for voice in VOICES}

SPEEDS = [(-10, "slowest"), (-8, "very slow"), (-6, "slower"), (-2, "slow"),
          (0, "normal"), (2, "fast"), (6, "faster"), (8, "very fast"),
          (10, "fastest")]

SPEED_VALUES = [value for value, label in SPEEDS]


def _quoter(user_string):
    """
    n.b. This quoter throws away some characters that are not in
    latin-1, like curly quotes (which the Flash version encodes as
    `%u201C` and `%u201D`), which is probably fine for 99.99% of use
    cases
    """

    return quote(user_string.encode('latin-1', 'ignore').decode())


class FluencyNl(Service):
    """
    Provides a Service-compliant implementation for Fluency.nl's
    text-to-speech demo.
    """

    __slots__ = []

    NAME = "Fluency.nl"

    TRAITS = [Trait.INTERNET]

    def desc(self):
        """Returns service name with a voice count."""

        return "Fluency.nl Demo for Dutch (%d voices)" % len(VOICES)

    def options(self):
        """Provides access to voice and speed."""

        voice_lookup = {self.normalize(key): key for key in VOICE_MAP.keys()}

        def transform_voice(user_value):
            """Tries to figure out our short value from user input."""

            normalized_value = self.normalize(user_value.replace('í', 'i'))
            if normalized_value in voice_lookup:
                return voice_lookup[normalized_value]

            normalized_value += 'm'  # MBROLA variation?
            if normalized_value in voice_lookup:
                return voice_lookup[normalized_value]

            return user_value

        def transform_speed(user_value):
            """Rounds user value to closest official value."""

            user_value = float(user_value)
            return min(
                SPEED_VALUES,
                key=lambda official_value: abs(user_value - official_value),
            )

        return [
            dict(
                key='voice',
                label="Voice",
                values=[(short_value, human_description)
                        for short_value, _, human_description
                        in VOICES],
                transform=transform_voice,
            ),

            dict(
                key='speed',
                label="Speed",
                values=SPEEDS,
                transform=transform_speed,
                default=0,
            ),
        ]

    def run(self, text, options, path):
        """Downloads from Fluency.nl directly to an MP3."""

        api_voice_value = VOICE_MAP[options['voice']][1]
        api_speed_value = options['speed']

        self.net_download(
            path,
            [
                (
                    'http://www.fluency-server.nl/cgi-bin/speak.exe',
                    dict(
                        id='Fluency',
                        voice=api_voice_value,
                        text=_quoter(subtext),  # intentionally double-encoded
                        tempo=api_speed_value,
                        rtf=50,
                    ),
                )
                for subtext in self.util_split(text, 250)
            ],
            method='POST',
            custom_headers=dict(Referer='http://www.fluency.nl/speak.swf'),
            require=dict(mime='audio/mpeg', size=256),
            add_padding=True,
        )
