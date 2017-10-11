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
Service implementation for SAPI 5 on the Windows platform via win32com
"""

from .base import Service
from .common import Trait

from .sapi5js import LANGUAGE_CODES

__all__ = ['SAPI5COM']


class SAPI5COM(Service):
    """
    Provides a Service-compliant implementation for SAPI 5 via win32com.
    """

    __slots__ = [
        '_client',     # reference to the win32com.client module
        '_pythoncom',  # reference to the pythoncom module
        '_voice_map',  # dict of voice names to their SAPI objects
    ]

    NAME = "Microsoft Speech API COM"

    TRAITS = [Trait.TRANSCODING]

    def __init__(self, *args, **kwargs):
        """
        Attempts to retrieve list of voices from the SAPI.SpVoice API.

        However, if not running on Windows, no environment inspection is
        attempted and an exception is immediately raised.
        """

        if not self.IS_WINDOWS:
            raise EnvironmentError("SAPI 5 is only available on Windows")

        super(SAPI5COM, self).__init__(*args, **kwargs)

        # win32com and pythoncom are Windows only, pylint:disable=import-error

        try:
            import win32com.client
        except IOError:  # some Anki packages have an unwritable cache path
            self._logger.warn("win32com.client import failed; trying again "
                              "with alternate __gen_path__ set")
            import win32com
            import os.path
            import tempfile
            win32com.__gen_path__ = os.path.join(tempfile.gettempdir(),
                                                 'gen_py')
            import win32com.client
        self._client = win32com.client

        import pythoncom
        self._pythoncom = pythoncom

        # pylint:enable=import-error

        voices = self._client.Dispatch('SAPI.SpVoice').getVoices()
        self._voice_map = {
            voice.getAttribute('name'): voice
            for voice in [voices.item(i) for i in range(voices.count)]
        }

        if not self._voice_map:
            raise EnvironmentError("No voices returned by SAPI 5")

    def desc(self):
        """
        Returns a short, static description.
        """

        count = len(self._voice_map)
        return ("SAPI 5.0 via win32com (%d %s)" %
                (count, "voice" if count == 1 else "voices"))

    def options(self):
        """
        Provides access to voice, speed, and volume.
        """

        voice_lookup = dict([
            # normalized with characters w/ diacritics stripped
            (self.normalize(voice[0]), voice[0])
            for voice in self._voice_map.keys()
        ] + [
            # normalized with diacritics converted
            (self.normalize(self.util_approx(voice[0])), voice[0])
            for voice in self._voice_map.keys()
        ])

        def transform_voice(value):
            """Normalize and attempt to convert to official voice."""

            normalized = self.normalize(value)

            return (
                voice_lookup[normalized] if normalized in voice_lookup
                else value
            )

        def get_voice_desc(name):
            try:
                lang = str(self._voice_map[name].getAttribute('language')).lower().strip()
                return '%s (%s)' % (name, LANGUAGE_CODES.get(lang, lang))
            except:
                return name

        return [
            dict(
                key='voice',
                label="Voice",
                values=[(voice, get_voice_desc(voice))
                        for voice in sorted(self._voice_map.keys())],
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
        Writes a temporary wave file, and then transcodes to MP3.
        """

        output_wav = self.path_temp('wav')
        self._pythoncom.CoInitializeEx(self._pythoncom.COINIT_MULTITHREADED)

        try:
            stream = self._client.Dispatch('SAPI.SpFileStream')
            stream.Format.Type = options['quality']
            stream.open(output_wav, 3)  # 3=SSFMCreateForWrite

            try:
                speech = self._client.Dispatch('SAPI.SpVoice')
                speech.AudioOutputStream = stream
                speech.Rate = options['speed']
                speech.Voice = self._voice_map[options['voice']]
                speech.Volume = options['volume']

                if options['xml']:
                    speech.speak(text, options['xml'])
                else:
                    speech.speak(text)
            finally:
                stream.close()

            self.cli_transcode(
                output_wav,
                path,
                require=dict(
                    size_in=4096,
                ),
            )

        finally:
            self._pythoncom.CoUninitialize()
            self.path_unlink(output_wav)
