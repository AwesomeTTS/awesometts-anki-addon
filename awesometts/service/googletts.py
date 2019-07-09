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
        ("ar-XA-Standard-A", "Arabic (ar-XA-Standard-A)"),
        ("ar-XA-Standard-B", "Arabic (ar-XA-Standard-B)"),
        ("ar-XA-Standard-C", "Arabic (ar-XA-Standard-C)"),
        ("ar-XA-Wavenet-A", "Arabic (ar-XA-Wavenet-A)"),
        ("ar-XA-Wavenet-B", "Arabic (ar-XA-Wavenet-B)"),
        ("ar-XA-Wavenet-C", "Arabic (ar-XA-Wavenet-C)"),
        ("cs-CZ-Standard-A", "Czech (cs-CZ-Standard-A)"),
        ("cs-CZ-Wavenet-A", "Czech (cs-CZ-Wavenet-A)"),
        ("da-DK-Standard-A", "Danish (da-DK-Standard-A)"),
        ("da-DK-Wavenet-A", "Danish (da-DK-Wavenet-A)"),
        ("de-DE-Standard-A", "German (de-DE-Standard-A)"),
        ("de-DE-Standard-B", "German (de-DE-Standard-B)"),
        ("de-DE-Wavenet-A", "German (de-DE-Wavenet-A)"),
        ("de-DE-Wavenet-B", "German (de-DE-Wavenet-B)"),
        ("de-DE-Wavenet-C", "German (de-DE-Wavenet-C)"),
        ("de-DE-Wavenet-D", "German (de-DE-Wavenet-D)"),
        ("el-GR-Standard-A", "Greek (el-GR-Standard-A)"),
        ("el-GR-Wavenet-A", "Greek (el-GR-Wavenet-A)"),
        ("en-AU-Standard-A", "English, Australia (en-AU-Standard-A)"),
        ("en-AU-Standard-B", "English, Australia (en-AU-Standard-B)"),
        ("en-AU-Standard-C", "English, Australia (en-AU-Standard-C)"),
        ("en-AU-Standard-D", "English, Australia (en-AU-Standard-D)"),
        ("en-AU-Wavenet-A", "English, Australia (en-AU-Wavenet-A)"),
        ("en-AU-Wavenet-B", "English, Australia (en-AU-Wavenet-B)"),
        ("en-AU-Wavenet-C", "English, Australia (en-AU-Wavenet-C)"),
        ("en-AU-Wavenet-D", "English, Australia (en-AU-Wavenet-D)"),
        ("en-GB-Standard-A", "English, United Kingdom (en-GB-Standard-A)"),
        ("en-GB-Standard-B", "English, United Kingdom (en-GB-Standard-B)"),
        ("en-GB-Standard-C", "English, United Kingdom (en-GB-Standard-C)"),
        ("en-GB-Standard-D", "English, United Kingdom (en-GB-Standard-D)"),
        ("en-GB-Wavenet-A", "English, United Kingdom (en-GB-Wavenet-A)"),
        ("en-GB-Wavenet-B", "English, United Kingdom (en-GB-Wavenet-B)"),
        ("en-GB-Wavenet-C", "English, United Kingdom (en-GB-Wavenet-C)"),
        ("en-GB-Wavenet-D", "English, United Kingdom (en-GB-Wavenet-D)"),
        ("en-IN-Standard-A", "English (en-IN-Standard-A)"),
        ("en-IN-Standard-B", "English (en-IN-Standard-B)"),
        ("en-IN-Standard-C", "English (en-IN-Standard-C)"),
        ("en-IN-Wavenet-A", "English (en-IN-Wavenet-A)"),
        ("en-IN-Wavenet-B", "English (en-IN-Wavenet-B)"),
        ("en-IN-Wavenet-C", "English (en-IN-Wavenet-C)"),
        ("en-US-Standard-B", "English, United States (en-US-Standard-B)"),
        ("en-US-Standard-C", "English, United States (en-US-Standard-C)"),
        ("en-US-Standard-D", "English, United States (en-US-Standard-D)"),
        ("en-US-Standard-E", "English, United States (en-US-Standard-E)"),
        ("en-US-Wavenet-A", "English, United States (en-US-Wavenet-A)"),
        ("en-US-Wavenet-B", "English, United States (en-US-Wavenet-B)"),
        ("en-US-Wavenet-C", "English, United States (en-US-Wavenet-C)"),
        ("en-US-Wavenet-D", "English, United States (en-US-Wavenet-D)"),
        ("en-US-Wavenet-E", "English, United States (en-US-Wavenet-E)"),
        ("en-US-Wavenet-F", "English, United States (en-US-Wavenet-F)"),
        ("es-ES-Standard-A", "Spanish (es-ES-Standard-A)"),
        ("fi-FI-Standard-A", "Finnish (fi-FI-Standard-A)"),
        ("fi-FI-Wavenet-A", "Finnish (fi-FI-Wavenet-A)"),
        ("fil-PH-Standard-A", "Filipino (fil-PH-Standard-A)"),
        ("fil-PH-Standard-A", "Filipino (fil-PH-Standard-A)"),
        ("fil-PH-Wavenet-A", "Filipino (fil-PH-Wavenet-A)"),
        ("fr-CA-Standard-A", "French, Canada (fr-CA-Standard-A)"),
        ("fr-CA-Standard-B", "French, Canada (fr-CA-Standard-B)"),
        ("fr-CA-Standard-C", "French, Canada (fr-CA-Standard-C)"),
        ("fr-CA-Standard-D", "French, Canada (fr-CA-Standard-D)"),
        ("fr-CA-Wavenet-A", "French, Canada (fr-CA-Wavenet-A)"),
        ("fr-CA-Wavenet-B", "French, Canada (fr-CA-Wavenet-B)"),
        ("fr-CA-Wavenet-C", "French, Canada (fr-CA-Wavenet-C)"),
        ("fr-CA-Wavenet-D", "French, Canada (fr-CA-Wavenet-D)"),
        ("fr-FR-Standard-A", "French, France (fr-FR-Standard-A)"),
        ("fr-FR-Standard-B", "French, France (fr-FR-Standard-B)"),
        ("fr-FR-Standard-C", "French, France (fr-FR-Standard-C)"),
        ("fr-FR-Standard-D", "French, France (fr-FR-Standard-D)"),
        ("fr-FR-Wavenet-A", "French, France (fr-FR-Wavenet-A)"),
        ("fr-FR-Wavenet-B", "French, France (fr-FR-Wavenet-B)"),
        ("fr-FR-Wavenet-C", "French, France (fr-FR-Wavenet-C)"),
        ("fr-FR-Wavenet-D", "French, France (fr-FR-Wavenet-D)"),
        ("hi-IN-Standard-A", "Hindi (hi-IN-Standard-A)"),
        ("hi-IN-Standard-B", "Hindi (hi-IN-Standard-B)"),
        ("hi-IN-Standard-C", "Hindi (hi-IN-Standard-C)"),
        ("hi-IN-Wavenet-A", "Hindi (hi-IN-Wavenet-A)"),
        ("hi-IN-Wavenet-B", "Hindi (hi-IN-Wavenet-B)"),
        ("hi-IN-Wavenet-C", "Hindi (hi-IN-Wavenet-C)"),
        ("hu-HU-Wavenet-A", "Hungarian (hu-HU-Wavenet-A)"),
        ("id-ID-Standard-A", "Indonesian (id-ID-Standard-A)"),
        ("id-ID-Standard-A", "Indonesian (id-ID-Standard-A)"),
        ("id-ID-Standard-B", "Indonesian (id-ID-Standard-B)"),
        ("id-ID-Standard-B", "Indonesian (id-ID-Standard-B)"),
        ("id-ID-Standard-C", "Indonesian (id-ID-Standard-C)"),
        ("id-ID-Standard-C", "Indonesian (id-ID-Standard-C)"),
        ("id-ID-Wavenet-A", "Indonesian (id-ID-Wavenet-A)"),
        ("id-ID-Wavenet-B", "Indonesian (id-ID-Wavenet-B)"),
        ("id-ID-Wavenet-C", "Indonesian (id-ID-Wavenet-C)"),
        ("it-IT-Standard-A", "Italian (it-IT-Standard-A)"),
        ("it-IT-Wavenet-A", "Italian (it-IT-Wavenet-A)"),
        ("ja-JP-Standard-A", "Japanese (ja-JP-Standard-A)"),
        ("ja-JP-Standard-B", "Japanese (ja-JP-Standard-B)"),
        ("ja-JP-Standard-C", "Japanese (ja-JP-Standard-C)"),
        ("ja-JP-Standard-D", "Japanese (ja-JP-Standard-D)"),
        ("ja-JP-Wavenet-A", "Japanese (ja-JP-Wavenet-A)"),
        ("ja-JP-Wavenet-B", "Japanese (ja-JP-Wavenet-B)"),
        ("ja-JP-Wavenet-C", "Japanese (ja-JP-Wavenet-C)"),
        ("ja-JP-Wavenet-D", "Japanese (ja-JP-Wavenet-D)"),
        ("ko-KR-Standard-A", "Korean (ko-KR-Standard-A)"),
        ("ko-KR-Standard-B", "Korean (ko-KR-Standard-B)"),
        ("ko-KR-Standard-C", "Korean (ko-KR-Standard-C)"),
        ("ko-KR-Standard-D", "Korean (ko-KR-Standard-D)"),
        ("ko-KR-Wavenet-A", "Korean (ko-KR-Wavenet-A)"),
        ("ko-KR-Wavenet-B", "Korean (ko-KR-Wavenet-B)"),
        ("ko-KR-Wavenet-C", "Korean (ko-KR-Wavenet-C)"),
        ("ko-KR-Wavenet-D", "Korean (ko-KR-Wavenet-D)"),
        ("nb-NO-Standard-A", "Norwegian (nb-NO-Standard-A)"),
        ("nb-NO-Standard-B", "Norwegian (nb-NO-Standard-B)"),
        ("nb-NO-Standard-C", "Norwegian (nb-NO-Standard-C)"),
        ("nb-NO-Standard-D", "Norwegian (nb-NO-Standard-D)"),
        ("nb-no-Standard-E", "Norwegian (nb-no-Standard-E)"),
        ("nb-NO-Wavenet-A", "Norwegian (nb-NO-Wavenet-A)"),
        ("nb-NO-Wavenet-B", "Norwegian (nb-NO-Wavenet-B)"),
        ("nb-NO-Wavenet-C", "Norwegian (nb-NO-Wavenet-C)"),
        ("nb-NO-Wavenet-D", "Norwegian (nb-NO-Wavenet-D)"),
        ("nb-no-Wavenet-E", "Norwegian (nb-no-Wavenet-E)"),
        ("nl-NL-Standard-A", "Dutch (nl-NL-Standard-A)"),
        ("nl-NL-Standard-A", "Dutch (nl-NL-Standard-A)"),
        ("nl-NL-Standard-B", "Dutch (nl-NL-Standard-B)"),
        ("nl-NL-Standard-B", "Dutch (nl-NL-Standard-B)"),
        ("nl-NL-Standard-C", "Dutch (nl-NL-Standard-C)"),
        ("nl-NL-Standard-C", "Dutch (nl-NL-Standard-C)"),
        ("nl-NL-Standard-D", "Dutch (nl-NL-Standard-D)"),
        ("nl-NL-Standard-D", "Dutch (nl-NL-Standard-D)"),
        ("nl-NL-Standard-E", "Dutch (nl-NL-Standard-E)"),
        ("nl-NL-Standard-E", "Dutch (nl-NL-Standard-E)"),
        ("nl-NL-Wavenet-A", "Dutch (nl-NL-Wavenet-A)"),
        ("nl-NL-Wavenet-B", "Dutch (nl-NL-Wavenet-B)"),
        ("nl-NL-Wavenet-C", "Dutch (nl-NL-Wavenet-C)"),
        ("nl-NL-Wavenet-D", "Dutch (nl-NL-Wavenet-D)"),
        ("nl-NL-Wavenet-E", "Dutch (nl-NL-Wavenet-E)"),
        ("pl-PL-Wavenet-A", "Polish (pl-PL-Wavenet-A)"),
        ("pl-PL-Wavenet-B", "Polish (pl-PL-Wavenet-B)"),
        ("pl-PL-Wavenet-C", "Polish (pl-PL-Wavenet-C)"),
        ("pl-PL-Wavenet-D", "Polish (pl-PL-Wavenet-D)"),
        ("pl-PL-Wavenet-E", "Polish (pl-PL-Wavenet-E)"),
        ("pt-BR-Standard-A", "Portuguese, Brazil (pt-BR-Standard-A)"),
        ("pt-BR-Wavenet-A", "Portuguese, Brazil (pt-BR-Wavenet-A)"),
        ("pt-PT-Standard-A", "Portuguese, Portugal (pt-PT-Standard-A)"),
        ("pt-PT-Standard-B", "Portuguese, Portugal (pt-PT-Standard-B)"),
        ("pt-PT-Standard-C", "Portuguese, Portugal (pt-PT-Standard-C)"),
        ("pt-PT-Standard-D", "Portuguese, Portugal (pt-PT-Standard-D)"),
        ("pt-PT-Wavenet-A", "Portuguese, Portugal (pt-PT-Wavenet-A)"),
        ("pt-PT-Wavenet-B", "Portuguese, Portugal (pt-PT-Wavenet-B)"),
        ("pt-PT-Wavenet-C", "Portuguese, Portugal (pt-PT-Wavenet-C)"),
        ("pt-PT-Wavenet-D", "Portuguese, Portugal (pt-PT-Wavenet-D)"),
        ("ru-RU-Standard-A", "Russian (ru-RU-Standard-A)"),
        ("ru-RU-Standard-B", "Russian (ru-RU-Standard-B)"),
        ("ru-RU-Standard-C", "Russian (ru-RU-Standard-C)"),
        ("ru-RU-Standard-D", "Russian (ru-RU-Standard-D)"),
        ("ru-RU-Wavenet-A", "Russian (ru-RU-Wavenet-A)"),
        ("ru-RU-Wavenet-B", "Russian (ru-RU-Wavenet-B)"),
        ("ru-RU-Wavenet-C", "Russian (ru-RU-Wavenet-C)"),
        ("ru-RU-Wavenet-D", "Russian (ru-RU-Wavenet-D)"),
        ("sk-SK-Wavenet-A", "Slovak (sk-SK-Wavenet-A)"),
        ("sv-SE-Standard-A", "Swedish (sv-SE-Standard-A)"),
        ("sv-SE-Wavenet-A", "Swedish (sv-SE-Wavenet-A)"),
        ("tr-TR-Wavenet-A", "Turkish (tr-TR-Wavenet-A)"),
        ("tr-TR-Wavenet-B", "Turkish (tr-TR-Wavenet-B)"),
        ("tr-TR-Wavenet-C", "Turkish (tr-TR-Wavenet-C)"),
        ("tr-TR-Wavenet-D", "Turkish (tr-TR-Wavenet-D)"),
        ("tr-TR-Wavenet-E", "Turkish (tr-TR-Wavenet-E)"),
        ("uk-UA-Wavenet-A", "Ukrainian (uk-UA-Wavenet-A)"),
        ("vi-VN-Standard-A", "Vietnamese (vi-VN-Standard-A)"),
        ("vi-VN-Standard-B", "Vietnamese (vi-VN-Standard-B)"),
        ("vi-VN-Standard-C", "Vietnamese (vi-VN-Standard-C)"),
        ("vi-VN-Standard-D", "Vietnamese (vi-VN-Standard-D)"),
        ("vi-VN-Wavenet-A", "Vietnamese (vi-VN-Wavenet-A)"),
        ("vi-VN-Wavenet-B", "Vietnamese (vi-VN-Wavenet-B)"),
        ("vi-VN-Wavenet-C", "Vietnamese (vi-VN-Wavenet-C)"),
        ("vi-VN-Wavenet-D", "Vietnamese (vi-VN-Wavenet-D)"),
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
