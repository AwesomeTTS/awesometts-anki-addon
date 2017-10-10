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
Service implementation for SAPI 5 on the Windows platform via JScript

This module functions with the help of a JScript gateway script. See
also the sapi5js.js file in this directory.
"""

import os
import os.path

from .base import Service
from .common import Trait

__all__ = ['SAPI5JS']


LANGUAGE_CODES = {
    '404': 'zh',
    '405': 'cs',
    '406': 'da',
    '407': 'de',
    '408': 'el',
    '409': 'en',
    '40a': 'es',
    '40c': 'fr',
    '410': 'it',
    '411': 'jp',
    '412': 'ko',
    '413': 'nl',
    '415': 'pl',
    '416': 'pt',
    '41d': 'sv',
    '41f': 'tr',
    '436': 'af',
    '439': 'hi',
    '804': 'zh',
}


class SAPI5JS(Service):
    """
    Provides a Service-compliant implementation for SAPI 5 via JScript.
    """

    __slots__ = [
        '_binary',        # path to the cscript binary
        '_voice_list',    # list of installed voices as a list of tuples
    ]

    NAME = "Microsoft Speech API JScript"

    TRAITS = [Trait.TRANSCODING]

    _SCRIPT = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'sapi5js.js',
    )

    def __init__(self, *args, **kwargs):
        """
        Attempts to locate the cscript binary and read the list of
        voices from the `cscript.exe sapi5js.js voice-list` output.

        However, if not running on Windows, no environment inspection is
        attempted and an exception is immediately raised.
        """

        if not self.IS_WINDOWS:
            raise EnvironmentError("SAPI 5 is only available on Windows")

        super(SAPI5JS, self).__init__(*args, **kwargs)

        self._binary = next(
            fullpath
            for windows in [
                os.environ.get('SYSTEMROOT', None),
                r'C:\Windows',
                r'C:\WinNT',
            ]
            if windows and os.path.exists(windows)
            for subdirectory in ['syswow64', 'system32', 'system']
            for filename in ['cscript.exe']
            for fullpath in [os.path.join(windows, subdirectory, filename)]
            if os.path.exists(fullpath)
        )

        output = [
            line.strip()
            for line in self.cli_output(
                self._binary,
                self._SCRIPT,
                'voice-list',
            )
        ]

        output = output[output.index('__AWESOMETTS_VOICE_LIST__') + 1:]

        def hex2uni(string):
            """Convert hexadecimal-escaped string back to unicode."""
            return ''.join(chr(int(string[i:i + 4], 16))
                           for i in range(0, len(string), 4))

        def convlang(string):
            """Get language code"""
            string = hex2uni(string).lower().strip()
            return LANGUAGE_CODES.get(string, string)

        self._voice_list = sorted({
            (voice, voice + ' (' + language + ')')
            for (voice, language) in [
                (
                    hex2uni(tokens[0]).strip(),
                    convlang(tokens[1]).strip()
                )
                for tokens
                in [line.split() for line in output]
            ]
            if voice
        }, key=lambda voice: voice[1].lower())

        if not self._voice_list:
            raise EnvironmentError("No voices in `sapi5js.js voice-list`")

    def desc(self):
        """
        Returns a short, static description.
        """

        count = len(self._voice_list)
        return ("SAPI 5.0 via JScript (%d %s)" %
                (count, "voice" if count == 1 else "voices"))

    def options(self):
        """
        Provides access to voice, speed, volume, and quality.
        """

        voice_lookup = dict([
            # normalized with characters w/ diacritics stripped
            (self.normalize(voice[0]), voice[0])
            for voice in self._voice_list
        ] + [
            # normalized with diacritics converted
            (self.normalize(self.util_approx(voice[0])), voice[0])
            for voice in self._voice_list
        ])

        def transform_voice(value):
            """Normalize and attempt to convert to official voice."""

            normalized = self.normalize(value)

            return (
                voice_lookup[normalized] if normalized in voice_lookup
                else value
            )

        return [
            # See also sapi5js.js when adjusting any of these

            dict(
                key='voice',
                label="Voice",
                values=self._voice_list,
                transform=transform_voice,
            ),

            dict(
                key='speed',
                label="Speed",
                values=(-10, 10),
                transform=int,
                default=0,
            ),

            dict(
                key='volume',
                label="Volume",
                values=(1, 100, "%"),
                transform=int,
                default=100,
            ),

            dict(
                key='quality',
                label="Quality",
                values=[
                    (4, "8 kHz, 8-bit, Mono"),
                    (5, "8 kHz, 8-bit, Stereo"),
                    (6, "8 kHz, 16-bit, Mono"),
                    (7, "8 kHz, 16-bit, Stereo"),
                    (8, "11 kHz, 8-bit, Mono"),
                    (9, "11 kHz, 8-bit, Stereo"),
                    (10, "11 kHz, 16-bit, Mono"),
                    (11, "11 kHz, 16-bit, Stereo"),
                    (12, "12 kHz, 8-bit, Mono"),
                    (13, "12 kHz, 8-bit, Stereo"),
                    (14, "12 kHz, 16-bit, Mono"),
                    (15, "12 kHz, 16-bit, Stereo"),
                    (16, "16 kHz, 8-bit, Mono"),
                    (17, "16 kHz, 8-bit, Stereo"),
                    (18, "16 kHz, 16-bit, Mono"),
                    (19, "16 kHz, 16-bit, Stereo"),
                    (20, "22 kHz, 8-bit, Mono"),
                    (21, "22 kHz, 8-bit, Stereo"),
                    (22, "22 kHz, 16-bit, Mono"),
                    (23, "22 kHz, 16-bit, Stereo"),
                    (24, "24 kHz, 8-bit, Mono"),
                    (25, "24 kHz, 8-bit, Stereo"),
                    (26, "24 kHz, 16-bit, Mono"),
                    (27, "24 kHz, 16-bit, Stereo"),
                    (28, "32 kHz, 8-bit, Mono"),
                    (29, "32 kHz, 8-bit, Stereo"),
                    (30, "32 kHz, 16-bit, Mono"),
                    (31, "32 kHz, 16-bit, Stereo"),
                    (32, "44 kHz, 8-bit, Mono"),
                    (33, "44 kHz, 8-bit, Stereo"),
                    (34, "44 kHz, 16-bit, Mono"),
                    (35, "44 kHz, 16-bit, Stereo"),
                    (36, "48 kHz, 8-bit, Mono"),
                    (37, "48 kHz, 8-bit, Stereo"),
                    (38, "48 kHz, 16-bit, Mono"),
                    (39, "48 kHz, 16-bit, Stereo"),
                ],
                transform=int,
                default=39,
            ),

            dict(
                key='xml',
                label="XML",
                values=[
                    (0, "automatic"),
                    (8, "always parse"),
                    (16, "pass through"),
                ],
                transform=int,
                default=0,
            ),
        ]

    def run(self, text, options, path):
        """
        Converts input voice and text into hex strings, writes a
        temporary wave file, and then transcodes to MP3.
        """

        def hexstr(value):
            """Convert given unicode into hexadecimal string."""
            return ''.join(['%04X' % ord(char) for char in value])

        output_wav = self.path_temp('wav')

        try:
            self.cli_call(
                self._binary,
                self._SCRIPT,
                'speech-output',
                output_wav,
                options['speed'],
                options['volume'],
                options['quality'],
                options['xml'],
                hexstr(options['voice']),
                hexstr(text),  # double dash unnecessary due to hex encoding
            )

            self.cli_transcode(
                output_wav,
                path,
                require=dict(
                    size_in=4096,
                ),
            )

        finally:
            self.path_unlink(output_wav)
