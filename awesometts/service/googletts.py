# -*- coding: utf-8 -*-

# AwesomeTTS text-to-speech add-on for Anki
# Copyright (C) 2010-Present  Anki AwesomeTTS Development Team
# Copyright (C) 2019 Nickolay <kelciour@gmail.com>
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
Service implementation for Google Cloud Text-to-Speech API
"""

import base64
import requests

from .base import Service
from .common import Trait

__all__ = ['GoogleTTS']


class GoogleTTS(Service):
    """
    Provides a Service-compliant implementation for Google Cloud Text-to-Speech.
    """

    __slots__ = []

    NAME = "Google Cloud Text-to-Speech"

    TRAITS = [Trait.INTERNET]

    _voice_list = [
        ('da-DK-Wavenet-A', "Danish (da-DK-Wavenet-A)"),
        ('de-DE-Wavenet-A', "German (de-DE-Wavenet-A)"),
        ('de-DE-Wavenet-B', "German (de-DE-Wavenet-B)"),
        ('de-DE-Wavenet-C', "German (de-DE-Wavenet-C)"),
        ('de-DE-Wavenet-D', "German (de-DE-Wavenet-D)"),
        ('en-AU-Wavenet-A', "English, Australia (en-AU-Wavenet-A)"),
        ('en-AU-Wavenet-B', "English, Australia (en-AU-Wavenet-B)"),
        ('en-AU-Wavenet-C', "English, Australia (en-AU-Wavenet-C)"),
        ('en-AU-Wavenet-D', "English, Australia (en-AU-Wavenet-D)"),
        ('en-GB-Wavenet-A', "English, United Kingdom (en-GB-Wavenet-A)"),
        ('en-GB-Wavenet-B', "English, United Kingdom (en-GB-Wavenet-B)"),
        ('en-GB-Wavenet-C', "English, United Kingdom (en-GB-Wavenet-C)"),
        ('en-GB-Wavenet-D', "English, United Kingdom (en-GB-Wavenet-D)"),
        ('en-US-Wavenet-A', "English, United States (en-US-Wavenet-A)"),
        ('en-US-Wavenet-B', "English, United States (en-US-Wavenet-B)"),
        ('en-US-Wavenet-C', "English, United States (en-US-Wavenet-C)"),
        ('en-US-Wavenet-D', "English, United States (en-US-Wavenet-D)"),
        ('en-US-Wavenet-E', "English, United States (en-US-Wavenet-E)"),
        ('en-US-Wavenet-F', "English, United States (en-US-Wavenet-F)"),
        ('fr-CA-Wavenet-A', "French, Canada (fr-CA-Wavenet-A)"),
        ('fr-CA-Wavenet-B', "French, Canada (fr-CA-Wavenet-B)"),
        ('fr-CA-Wavenet-C', "French, Canada (fr-CA-Wavenet-C)"),
        ('fr-CA-Wavenet-D', "French, Canada (fr-CA-Wavenet-D)"),
        ('fr-FR-Wavenet-A', "French, France (fr-FR-Wavenet-A)"),
        ('fr-FR-Wavenet-B', "French, France (fr-FR-Wavenet-B)"),
        ('fr-FR-Wavenet-C', "French, France (fr-FR-Wavenet-C)"),
        ('fr-FR-Wavenet-D', "French, France (fr-FR-Wavenet-D)"),
        ('it-IT-Wavenet-A', "Italian (it-IT-Wavenet-A)"),
        ('ja-JP-Wavenet-A', "Japanese (ja-JP-Wavenet-A)"),
        ('ko-KR-Wavenet-B', "Korean (ko-KR-Wavenet-B)"),
        ('ko-KR-Wavenet-C', "Korean (ko-KR-Wavenet-C)"),
        ('ko-KR-Wavenet-D', "Korean (ko-KR-Wavenet-D)"),
        ('ko-KR-Wavenet-A', "Korean (ko-KR-Wavenet-A)"),
        ('nl-NL-Wavenet-A', "Dutch (nl-NL-Wavenet-A)"),
        ('pl-PL-Wavenet-A', "Polish (pl-PL-Wavenet-A)"),
        ('pl-PL-Wavenet-B', "Polish (pl-PL-Wavenet-B)"),
        ('pl-PL-Wavenet-C', "Polish (pl-PL-Wavenet-C)"),
        ('pl-PL-Wavenet-D', "Polish (pl-PL-Wavenet-D)"),
        ('pt-BR-Wavenet-A', "Portuguese, Brazil (pt-BR-Wavenet-A)"),
        ('pt-PT-Wavenet-A', "Portuguese, Portugal (pt-PT-Wavenet-A)"),
        ('pt-PT-Wavenet-B', "Portuguese, Portugal (pt-PT-Wavenet-B)"),
        ('pt-PT-Wavenet-C', "Portuguese, Portugal (pt-PT-Wavenet-C)"),
        ('pt-PT-Wavenet-D', "Portuguese, Portugal (pt-PT-Wavenet-D)"),
        ('ru-RU-Wavenet-A', "Russian (ru-RU-Wavenet-A)"),
        ('ru-RU-Wavenet-B', "Russian (ru-RU-Wavenet-B)"),
        ('ru-RU-Wavenet-C', "Russian (ru-RU-Wavenet-C)"),
        ('ru-RU-Wavenet-D', "Russian (ru-RU-Wavenet-D)"),
        ('sk-SK-Wavenet-A', "Slovak (sk-SK-Wavenet-A)"),
        ('sv-SE-Wavenet-A', "Swedish (sv-SE-Wavenet-A)"),
        ('tr-TR-Wavenet-A', "Turkish (tr-TR-Wavenet-A)"),
        ('tr-TR-Wavenet-B', "Turkish (tr-TR-Wavenet-B)"),
        ('tr-TR-Wavenet-C', "Turkish (tr-TR-Wavenet-C)"),
        ('tr-TR-Wavenet-D', "Turkish (tr-TR-Wavenet-D)"),
        ('tr-TR-Wavenet-E', "Turkish (tr-TR-Wavenet-E)"),
        ('uk-UA-Wavenet-A', "Ukrainian (uk-UA-Wavenet-A)"),
        ('es-ES-Standard-A', "Spanish (es-ES-Standard-A)"),
        ('it-IT-Standard-A', "Italian (it-IT-Standard-A)"),
        ('ru-RU-Standard-A', "Russian (ru-RU-Standard-A)"),
        ('ru-RU-Standard-B', "Russian (ru-RU-Standard-B)"),
        ('ru-RU-Standard-C', "Russian (ru-RU-Standard-C)"),
        ('ru-RU-Standard-D', "Russian (ru-RU-Standard-D)"),
        ('ko-KR-Standard-A', "Korean (ko-KR-Standard-A)"),
        ('ko-KR-Standard-B', "Korean (ko-KR-Standard-B)"),
        ('ko-KR-Standard-C', "Korean (ko-KR-Standard-C)"),
        ('ja-JP-Standard-A', "Japanese (ja-JP-Standard-A)"),
        ('nl-NL-Standard-A', "Dutch (nl-NL-Standard-A)"),
        ('pt-BR-Standard-A', "Portuguese, Brazil (pt-BR-Standard-A)"),
        ('pl-PL-Standard-A', "Polish (pl-PL-Standard-A)"),
        ('pl-PL-Standard-B', "Polish (pl-PL-Standard-B)"),
        ('pl-PL-Standard-C', "Polish (pl-PL-Standard-C)"),
        ('pl-PL-Standard-D', "Polish (pl-PL-Standard-D)"),
        ('sk-SK-Standard-A', "Slovak (sk-SK-Standard-A)"),
        ('tr-TR-Standard-A', "Turkish (tr-TR-Standard-A)"),
        ('tr-TR-Standard-B', "Turkish (tr-TR-Standard-B)"),
        ('tr-TR-Standard-C', "Turkish (tr-TR-Standard-C)"),
        ('tr-TR-Standard-D', "Turkish (tr-TR-Standard-D)"),
        ('tr-TR-Standard-E', "Turkish (tr-TR-Standard-E)"),
        ('da-DK-Standard-A', "Danish (da-DK-Standard-A)"),
        ('pt-PT-Standard-A', "Portuguese, Portugal (pt-PT-Standard-A)"),
        ('pt-PT-Standard-B', "Portuguese, Portugal (pt-PT-Standard-B)"),
        ('pt-PT-Standard-C', "Portuguese, Portugal (pt-PT-Standard-C)"),
        ('pt-PT-Standard-D', "Portuguese, Portugal (pt-PT-Standard-D)"),
        ('sv-SE-Standard-A', "Swedish (sv-SE-Standard-A)"),
        ('en-GB-Standard-A', "English, United Kingdom (en-GB-Standard-A)"),
        ('en-GB-Standard-B', "English, United Kingdom (en-GB-Standard-B)"),
        ('en-GB-Standard-C', "English, United Kingdom (en-GB-Standard-C)"),
        ('en-GB-Standard-D', "English, United Kingdom (en-GB-Standard-D)"),
        ('en-US-Standard-B', "English, United States (en-US-Standard-B)"),
        ('en-US-Standard-C', "English, United States (en-US-Standard-C)"),
        ('en-US-Standard-D', "English, United States (en-US-Standard-D)"),
        ('en-US-Standard-E', "English, United States (en-US-Standard-E)"),
        ('de-DE-Standard-A', "German (de-DE-Standard-A)"),
        ('de-DE-Standard-B', "German (de-DE-Standard-B)"),
        ('en-AU-Standard-A', "English, Australia (en-AU-Standard-A)"),
        ('en-AU-Standard-B', "English, Australia (en-AU-Standard-B)"),
        ('en-AU-Standard-C', "English, Australia (en-AU-Standard-C)"),
        ('en-AU-Standard-D', "English, Australia (en-AU-Standard-D)"),
        ('fr-CA-Standard-A', "French, Canada (fr-CA-Standard-A)"),
        ('fr-CA-Standard-B', "French, Canada (fr-CA-Standard-B)"),
        ('fr-CA-Standard-C', "French, Canada (fr-CA-Standard-C)"),
        ('fr-CA-Standard-D', "French, Canada (fr-CA-Standard-D)"),
        ('fr-FR-Standard-A', "French, France (fr-FR-Standard-A)"),
        ('fr-FR-Standard-B', "French, France (fr-FR-Standard-B)"),
        ('fr-FR-Standard-C', "French, France (fr-FR-Standard-C)"),
        ('fr-FR-Standard-D', "French, France (fr-FR-Standard-D"),
    ]

    def desc(self):
        """
        Returns a short, static description.
        """

        return "Google Cloud Text-to-Speech (%d voices)." % (
            len(set(map(lambda x: x[0][:5], self._voice_list))))

    def extras(self):
        """The Google Cloud Text-to-Speech requires an API key."""

        return [dict(key='key', label="API Key", required=True)]

    def options(self):
        """
        Provides access to voice only.
        """

        return [
            dict(
                key='voice',
                label="Voice",
                values=self._voice_list,
                transform=lambda value: value,
                default='en-US-Wavenet-D',
            ),

            dict(
                key='speed',
                label="Speed",
                values=(0.25, 4),
                transform=float,
                default=1.00,
            ),

            dict(
                key='pitch',
                label="Pitch",
                values=(-20.00, 20.00),
                transform=float,
                default=0.00,
            )
        ]

    def run(self, text, options, path):
        """
        Send a synthesis request to the Text-to-Speech API and
        decode the base64-encoded string into an audio file.
        """

        payload = {
          "audioConfig": {
              "audioEncoding": "MP3",
              "pitch": options['pitch'],
              "speakingRate": options['speed'],
          },
          "input": {
              "text": text
          },
          "voice": {
              "languageCode": options['voice'][:5],
              "name": options['voice'],
          }
        }

        r = requests.post("https://texttospeech.googleapis.com/v1/text:synthesize?key={}".format(options['key']), json=payload)
        r.raise_for_status()

        data = r.json()
        encoded = data['audioContent']
        audio_content = base64.b64decode(encoded)

        with open(path, 'wb') as response_output:
            response_output.write(audio_content)
