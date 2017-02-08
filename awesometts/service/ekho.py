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
Service implementation for Ekho text-to-speech engine
"""

from .base import Service
from .common import Trait

__all__ = ['Ekho']


class Ekho(Service):
    """
    Provides a Service-compliant implementation for Ekho.
    """

    __slots__ = [
        '_voice_list',    # list of installed voices as a list of tuples
    ]

    NAME = "Ekho"

    TRAITS = [Trait.TRANSCODING]

    def __init__(self, *args, **kwargs):
        """
        Attempts to read the list of voices from the `ekho --help`
        output.
        """

        super(Ekho, self).__init__(*args, **kwargs)

        output = self.cli_output('ekho', '--help')

        import re
        re_list = re.compile(r'(language|voice).+available', re.IGNORECASE)
        re_voice = re.compile(r"'(\w+)'")

        self._voice_list = sorted({
            (
                # Workaround for Korean: in at least ekho v5.8.2, passing
                # `--voice Hangul` fails, but `--voice hangul` works. This is
                # different from the other voices that either only work when
                # capitalized (e.g. Mandarin, Cantonese) or accept both forms
                # (e.g. hakka/Hakka, ngangien/Ngangien, tibetan/Tibetan).

                'hangul' if capture == 'Hangul' else capture,
                capture,
            )
            for line in output if re_list.search(line)
            for capture in re_voice.findall(line)
        }, key=lambda voice: voice[1].lower())

        if not self._voice_list:
            raise EnvironmentError("No usable output from `ekho --help`")

    def desc(self):
        """
        Returns a simple version using `ekho --version`.
        """

        return "ekho %s (%d voices)" % (
            self.cli_output('ekho', '--version').pop(0),
            len(self._voice_list),
        )

    def options(self):
        """
        Provides access to voice, speed, pitch, rate, and volume.
        """

        voice_lookup = {
            self.normalize(voice[0]): voice[0]
            for voice in self._voice_list
        }

        def transform_voice(value):
            """Normalize and attempt to convert to official voice."""

            normalized = self.normalize(value)

            return (
                voice_lookup[normalized] if normalized in voice_lookup

                else voice_lookup['mandarin'] if (
                    'mandarin' in voice_lookup and
                    normalized in ['cmn', 'cosc', 'goyu', 'huyu', 'mand',
                                   'zh', 'zhcn']
                )

                else voice_lookup['cantonese'] if (
                    'cantonese' in voice_lookup and
                    normalized in ['cant', 'guzh', 'yue', 'yyef', 'zhhk',
                                   'zhyue']
                )

                else voice_lookup['hakka'] if (
                    'hakka' in voice_lookup and
                    normalized in ['hak', 'hakk', 'kejia']
                )

                else voice_lookup['tibetan'] if (
                    'tibetan' in voice_lookup and
                    normalized in ['cent', 'west']
                )

                else voice_lookup['hangul'] if (
                    'hangul' in voice_lookup and
                    normalized in ['ko', 'kor', 'kore', 'korean']
                )

                else value
            )

        voice_option = dict(
            key='voice',
            label="Voice",
            values=self._voice_list,
            transform=transform_voice,
        )

        if 'mandarin' in voice_lookup:  # default is Mandarin, if we have it
            voice_option['default'] = voice_lookup['mandarin']

        return [
            voice_option,

            dict(
                key='speed',
                label="Speed Delta",
                values=(-50, 300, "%"),
                transform=int,
                default=0,
            ),

            dict(
                key='pitch',
                label="Pitch Delta",
                values=(-100, 100, "%"),
                transform=int,
                default=0,
            ),

            dict(
                key='rate',
                label="Rate Delta",
                values=(-50, 100, "%"),
                transform=int,
                default=0,
            ),

            dict(
                key='volume',
                label="Volume Delta",
                values=(-100, 100, "%"),
                transform=int,
                default=0,
            ),
        ]

    def run(self, text, options, path):
        """
        Checks for unicode workaround on Windows, writes a temporary
        wave file, and then transcodes to MP3.

        Technically speaking, Ekho supports writing directly to MP3, but
        by going through LAME, we can apply the user's custom flags.
        """

        input_file = self.path_workaround(text)
        output_wav = self.path_temp('wav')

        try:
            self.cli_call(
                [
                    'ekho',
                    '-v', options['voice'],
                    '-s', options['speed'],
                    '-p', options['pitch'],
                    '-r', options['rate'],
                    '-a', options['volume'],
                    '-o', output_wav,
                ] + (
                    ['-f', input_file] if input_file
                    else ['--', text]
                )
            )

            self.cli_transcode(
                output_wav,
                path,
                require=dict(
                    size_in=4096,
                ),
            )

        finally:
            self.path_unlink(input_file, output_wav)
