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
Service implementation for the FPT.AI Vietnamese Text To Speech
https://fpt.ai/tts
"""

from .base import Service
import requests
import json
import time
from .languages import StandardVoice
from .voicelist import VOICE_LIST
from typing import List

__all__ = ['FptAi']



class FptAi(Service):
    """
    Provides a Service-compliant implementation for iSpeech.
    """

    __slots__ = [
    ]

    NAME = "FptAi Vietnamese"

    TRAITS = []

    def desc(self):
        """Returns name with a voice count."""

        return "FPT.API Vietnamese"

    def extras(self):
        """The FPT.AI API requires an API key."""

        if self.languagetools.use_plus_mode():
            # plus mode, no need for an API key
            return []        

        return [dict(key='key', label="API Key", required=True)]


    def get_voices(self) -> List[StandardVoice]:
        naver_voices = [x for x in VOICE_LIST if x['service'] == 'FptAi']
        naver_voices = sorted(naver_voices, key=lambda x: x['voice_description'])
        voice_list = []
        for voice_data in naver_voices:
            voice_list.append(StandardVoice(voice_data))
        return voice_list        

    def get_voice_list(self):
        voice_list = [(voice.get_voice_key(), voice.get_description()) for voice in self.get_voices()]
        voice_list.sort(key=lambda x: x[1])
        return voice_list

    def get_voice_for_key(self, key) -> StandardVoice:
        voice = [voice for voice in self.get_voices() if voice.get_voice_key() == key]
        assert(len(voice) == 1)
        return voice[0]

    def options(self):
        """Provides access to voice and speed."""

        return [
            dict(key='voice',
                 label="Voice",
                 values=self.get_voice_list(),
                 transform=lambda value: value),

            dict(key='speed',
                 label="Speed",
                 values=(-3, +3),
                 transform=lambda i: min(max(-3, int(round(float(i)))), +3),
                 default=0),

        ]

    def run(self, text, options, path):
        """Downloads from FPT.AI Vietnamese API directly to an MP3."""
        
        voice_key = options['voice']
        voice = self.get_voice_for_key(voice_key)

        speed = options['speed']

        if self.languagetools.use_plus_mode():
            self._logger.info(f'using language tools API')
            service = 'FptAi'
            voice_key = voice.get_voice_key()
            language = voice.get_language_code()
            options = {
                'speed': speed
            }
            self.languagetools.generate_audio_v2(text, service, 'batch', language, 'n/a', voice_key, options, path)        
        else:

            # make request first, then we'll have a result URL
            headers = {
                'api_key': options['key'],
                'voice': options['voice']['voice_id'],
                'Cache-Control': 'no-cache',
                'format': 'mp3',
                'speed': str(options['speed'])
            }            

            api_url = "https://api.fpt.ai/hmi/tts/v5"
            body = text
            response = requests.post(api_url, headers=headers, data=body.encode('utf-8'))

            self._logger.debug(f'executing POST on {api_url} with headers {headers}, text: {text}')

            if response.status_code != 200:
                error_message = f"Status code: {response.status_code} voice: {options['voice']} API key: {options['key']}"
                self._logger.error(error_message)
                raise ValueError(error_message)

            self._logger.debug(f'got response: {response.content}')

            data = json.loads(response.content)
            if data['error'] != 0:
                error_message = f"error: {data['error']} message: {data['message']}"
                self._logger.error(error_message)
                raise ValueError(error_message)

            async_url = data['async']

            self._logger.debug(f"got async url: {async_url}")

            # wait until the audio is available
            audio_available = False
            max_tries = 7
            wait_time = 0.2
            while audio_available == False and max_tries > 0:
                time.sleep(wait_time)
                r = requests.get(async_url, allow_redirects=True)
                self._logger.debug(f"status code: {r.status_code}")
                if r.status_code == 200:
                    audio_available = True
                wait_time = wait_time * 2
                max_tries -= 1

            self.net_download(
                path,
                async_url,
                require=dict(mime='audio/mpeg', size=256),
            )

