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
Service implementation for the Naver Clova Premium voice service
https://apidocs.ncloud.com/en/ai-naver/clova_premium_voice/tts/
"""

import time
import datetime
import requests
import urllib
from .base import Service
from .languages import Language
from .languages import Gender
from .languages import StandardVoice
from .voicelist import VOICE_LIST
from typing import List

__all__ = ['NaverClovaPremium']


class NaverClovaPremium(Service):
    """
    Provides a Service-compliant implementation for Naver Clova Premium Text To Speech.
    """

    __slots__ = [
    ]

    NAME = "Naver Clova Premium"

    # Although Naver Clova is an Internet service, we do not mark it with
    # Trait.INTERNET, as it is a paid-for-by-the-user API, and we do not want
    # to rate-limit it or trigger error caching behavior
    TRAITS = []

    def desc(self):
        """Returns name with a voice count."""

        return "Naver Clova Premium TTS API (%d voices)" % len(VOICE_LIST)

    def extras(self):
        """The Azure API requires an API key."""
        if self.languagetools.use_plus_mode():
            # plus mode, no need for an API key
            return []        

        return [dict(key='clientid', label="API Client Id", required=True),
            dict(key='clientsecret', label="API Client Secret", required=True)]
    
    def get_voices(self) -> List[StandardVoice]:
        naver_voices = [x for x in VOICE_LIST if x['service'] == 'Naver']
        naver_voices = sorted(naver_voices, key=lambda x: x['voice_description'])
        voice_list = []
        for voice_data in naver_voices:
            voice_list.append(StandardVoice(voice_data))
        return voice_list        

    def get_voice_list(self):
        voice_list = [(voice.get_key(), voice.get_description()) for voice in self.get_voices()]
        voice_list.sort(key=lambda x: x[1])
        return voice_list

    def get_voice_for_key(self, key) -> StandardVoice:
        voice = [voice for voice in self.get_voices() if voice.get_key() == key]
        assert(len(voice) == 1)
        return voice[0]

    def options(self):

        return [
            dict(key='voice',
                 label="Voice",
                 values=self.get_voice_list(),
                 transform=lambda value: value),
            dict(
                key='speed',
                label="Speed",
                values=(-5, 5),
                transform=int,
                default=0,
            ),
            dict(
                key='pitch',
                label="Pitch",
                values=(-5, 5),
                transform=int,
                default=0,
            )
        ]


    def run(self, text, options, path):
        """Downloads from Naver Clova API directly to an MP3."""
        
        voice_key = options['voice']
        voice = self.get_voice_for_key(voice_key)
        
        speed = options['speed']
        pitch = options['pitch']        

        if self.languagetools.use_plus_mode():
            self._logger.info(f'using language tools API')
            service = 'Naver'
            voice_key = voice.get_voice_key()
            language = voice.get_language_code()
            options = {
                'pitch': pitch,
                'speed': speed
            }
            self.languagetools.generate_audio_v2(text, service, 'batch', language, 'n/a', voice_key, options, path)
        else:
            client_id = options['clientid']
            client_secret = options['clientsecret']
            encText = urllib.parse.quote(text)

            voice_name = voice.get_key()
            data = f"speaker={voice_name}&speed={speed}&pitch={pitch}&text={encText}"
            url = 'https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts'
            self._logger.debug(f"url: {url}, data: {data}")
            request = urllib.request.Request(url)
            request.add_header("X-NCP-APIGW-API-KEY-ID",client_id)
            request.add_header("X-NCP-APIGW-API-KEY",client_secret)
            response = urllib.request.urlopen(request, data=data.encode('utf-8'))
            rescode = response.getcode()
            if(rescode==200):
                self._logger.debug("successful response")
                response_body = response.read()
                with open(path, 'wb') as f:
                    f.write(response_body)
            else:
                error_message = f"Status code: {rescode}"
                self._logger.error(error_message)            
                raise ValueError(error_message)            

