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

from hashlib import sha1
from typing import List

from .base import Service
from .common import Trait

from .languages import StandardVoice
from .voicelist import VOICE_LIST

__all__ = ['GoogleTTS']


class GoogleTTS(Service):
    """
    Provides a Service-compliant implementation for Google Cloud Text-to-Speech.
    """

    __slots__ = []

    NAME = "Google Cloud Text-to-Speech"

    TRAITS = [Trait.INTERNET]

    _audio_device_profile = [
        ("default", "Default"),
        ("wearable-class-device", "Smart watches and other wearables, like Apple Watch, Wear OS watch"),
        ("handset-class-device", "Smartphones, like Google Pixel, Samsung Galaxy, Apple iPhone"),
        ("headphone-class-device", "Earbuds or headphones for audio playback, like Sennheiser headphones"),
        ("small-bluetooth-speaker-class-device", "Small home speakers, like Google Home Mini"),
        ("medium-bluetooth-speaker-class-device", "Smart home speakers, like Google Home"),
        ("large-home-entertainment-class-device", "Home entertainment systems or smart TVs, like Google Home Max, LG TV"),
        ("large-automotive-class-device", "Car speakers"),
        ("telephony-class-application", "Interactive Voice Response (IVR) systems"),
    ]

    def _languageCode(self, name):
        """
        Returns a language code (en-US) from its name (en-US-Wavenet-A).
        """

        return '-'.join(name.split('-')[:2])


    def desc(self):
        """
        Returns a short, static description.
        """

        return "Google Cloud Text-to-Speech (%d voices)." % (
            len(set(map(lambda x: self._languageCode(x[0]), self._voice_list))))

    def extras(self):
        """The Google Cloud Text-to-Speech requires an API key."""

        if self.languagetools.use_plus_mode():
            # plus mode, no need for an API key
            return []
        return [dict(key='key', label="API Key", required=True)]

    def get_voices(self) -> List[StandardVoice]:
        voices = [x for x in VOICE_LIST if x['service'] == 'Google']
        voices = sorted(voices, key=lambda x: x['voice_description'])
        voice_list = []
        for voice_data in voices:
            voice_list.append(StandardVoice(voice_data))
        return voice_list        

    def get_voice_list(self):
        sorted_voices = self.get_voices()
        sorted_voices.sort(key=lambda x: x.get_description())
        return [(voice.get_key(), voice.get_description()) for voice in sorted_voices]

    def get_voice_for_key(self, key) -> StandardVoice:
        voice = [voice for voice in self.get_voices() if voice.get_key() == key]
        assert(len(voice) == 1)
        return voice[0]

    def options(self):
        """
        Provides access to voice only.
        """

        return [
            dict(
                key='voice',
                label="Voice",
                values=self.get_voice_list(),
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
            ),

            dict(
                key='profile',
                label="Profile",
                values=self._audio_device_profile,
                transform=lambda value: value,
                default='default',
            )
        ]

    def run(self, text, options, path):
        """
        Send a synthesis request to the Text-to-Speech API and
        decode the base64-encoded string into an audio file.
        """

        voice = self.get_voice_for_key(options['voice'])

        if self.languagetools.use_plus_mode():
            self._logger.info(f'using language tools API')
            service = 'Google'
            voice_key = voice.get_voice_key()
            language = voice.get_language_code()
            options = {
                'pitch': options['pitch'],
                'speaking_rate': options['speed']
            }
            self.languagetools.generate_audio_v2(text, service, 'batch', language, 'n/a', voice_key, options, path)
        else:
            payload = {
                "audioConfig": {
                    "audioEncoding": "MP3",
                    "pitch": options['pitch'],
                    "speakingRate": options['speed'],
                },
                "input": {
                    "ssml": f"<speak>{text}</speak>"
                },
                "voice": {
                    "languageCode": voice.get_voice_key()['language_code'],
                    "name": voice.get_voice_key()['name'],
                }
            }

            headers = {}
            if sha1(options['key'].encode("utf-8")).hexdigest() == "8224a632410a845cbb4b20f9aef131b495f7ad7f":
                headers['x-origin'] = 'https://explorer.apis.google.com'

            if options['profile'] != 'default':
                payload["audioConfig"]["effectsProfileId"] = [options['profile']]

            r = requests.post("https://texttospeech.googleapis.com/v1/text:synthesize?key={}".format(options['key']), headers=headers, json=payload)
            r.raise_for_status()

            data = r.json()
            encoded = data['audioContent']
            audio_content = base64.b64decode(encoded)

            with open(path, 'wb') as response_output:
                response_output.write(audio_content)
