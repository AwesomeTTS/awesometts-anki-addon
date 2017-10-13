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
Service implementation for SVOX Pico TTS
"""

from .base import Service
from .common import Trait

__all__ = ['Pico2Wave']


class Pico2Wave(Service):
    """
    Provides a Service-compliant implementation for SVOX Pico TTS.
    """

    __slots__ = [
        '_binary',      # path to the pico2wave binary
        '_voice_list',  # list of installed voices as a list of tuples
    ]

    NAME = "SVOX Pico"

    TRAITS = [Trait.TRANSCODING]

    def __init__(self, *args, **kwargs):
        """
        Attempts to read the list of voices from stderr when triggering
        a usage error with `pico2wave --lang X --wave X X`.
        """

        if self.IS_WINDOWS:
            raise EnvironmentError(
                "SVOX Pico cannot be used on Windows because unicode text "
                "cannot be passed to the CLI via the subprocess module in "
                "in Python 2 and pico2wave offers no input alternative"
            )

        super(Pico2Wave, self).__init__(*args, **kwargs)

        import re
        re_voice = re.compile(r'^[a-z]{2}-[A-Z]{2}$')

        for binary in ['pico2wave', 'lt-pico2wave']:
            try:
                self._voice_list = sorted({
                    (line, line)
                    for line in self.cli_output_error(
                        binary,
                        '--lang', 'x',
                        '--wave', 'x',
                        'x',
                    )
                    if re_voice.match(line)
                })

                if self._voice_list:
                    self._binary = binary
                    break

            except Exception:
                continue

        else:
            raise EnvironmentError("No usable pico2wave call was found")

    def desc(self):
        """
        Returns the name of the binary in-use and how many voices it
        reported.
        """

        return "%s (%d voices)" % (self._binary, len(self._voice_list))

    def options(self):
        """
        Provides access to voice only.
        """

        voice_lookup = dict([
            # two-letter language codes (for countries with multiple variants,
            # last one alphabetically wins, e.g. en maps to en-US, not en-GB)
            (self.normalize(voice[0][0:2]), voice[0])
            for voice in self._voice_list
        ] + [
            # official language codes
            (self.normalize(voice[0]), voice[0])
            for voice in self._voice_list
        ])

        def transform_voice(value):
            """Normalize and attempt to convert to official voice."""

            normalized = self.normalize(value)
            return voice_lookup[normalized] if normalized in voice_lookup \
                else value

        return [
            dict(
                key='voice',
                label="Voice",
                values=self._voice_list,
                transform=transform_voice,
            ),
        ]

    def run(self, text, options, path):
        """
        Writes a temporary wave file and then transcodes to MP3.

        Note that unlike other services (e.g. eSpeak), we do not attempt
        to workaround the unicode problem on Windows because `pico2wave`
        has no alternate input method for reading from a file.
        """

        output_wav = self.path_temp('wav')

        try:
            self.cli_call(
                self._binary,
                '--lang', options['voice'],
                '--wave', output_wav,
                '--', text,
            )

            self.cli_transcode(
                output_wav,
                path,
                require=dict(
                    size_in=4096,
                ),
                add_padding=True,
            )

        finally:
            self.path_unlink(output_wav)
