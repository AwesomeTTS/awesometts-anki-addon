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
from .languages import Voice
from typing import List

__all__ = ['NaverClovaPremium']

VOICE_LIST = [
    ('nara', 'Korean, female voice'),
]


class NaverVoice(Voice):
    def __init__(self, language, name, gender, description, voice_type):
        self.language = language
        self.name = name
        self.gender = gender
        self.description = description
        self.voice_type = voice_type

    def get_voice_key(self):
        return {
            'name': self.name
        }

    def get_language(self) -> Language:
        return self.language

    def get_gender(self) -> Gender:
        return self.gender

    def get_key(self) -> str:
        return self.name

    def get_voice_shortname(self):
        return f'{self.description} ({self.voice_type})'

    def get_description(self) -> str:
        value = f"{self.language.lang_name}, {self.gender.name}, {self.voice_type}, {self.description}"
        return value


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

        return [dict(key='clientid', label="API Client Id", required=True),
            dict(key='clientsecret', label="API Client Secret", required=True)]
    
    def get_voices(self) -> List[NaverVoice]:
        return [
            NaverVoice(Language.ko_KR, 'mijin', Gender.Female, 'Mijin', 'General'),
            NaverVoice(Language.ko_KR, 'jinho', Gender.Male, 'Jinho', 'General'),
            NaverVoice(Language.en_US, 'clara', Gender.Female, 'Clara', 'General'),
            NaverVoice(Language.en_US, 'matt', Gender.Male, 'Matt', 'General'),
            NaverVoice(Language.ja_JP, 'shinji', Gender.Male, 'Shinji', 'General'),
            NaverVoice(Language.zh_CN, 'meimei', Gender.Female, 'Meimei', 'General'),
            NaverVoice(Language.zh_CN, 'liangliang', Gender.Male, 'Liangliang', 'General'),
            NaverVoice(Language.es_ES, 'jose', Gender.Male, 'Jose', 'General'),
            NaverVoice(Language.es_ES, 'carmen', Gender.Female, 'Carmen', 'General'),

            NaverVoice(Language.ko_KR, 'nara', Gender.Female, 'Nara', 'Premium'),
            NaverVoice(Language.ko_KR, 'nminsang', Gender.Male, 'Minsang', 'Premium'),
            NaverVoice(Language.ko_KR, 'nhajun', Gender.Male, 'Hajoon', 'Premium (Child)'),
            NaverVoice(Language.ko_KR, 'ndain', Gender.Female, 'Dain', 'Premium (Child)'),
            NaverVoice(Language.ko_KR, 'njiyun', Gender.Female, 'Jiyoon', 'Premium'),
            NaverVoice(Language.ko_KR, 'nsujin', Gender.Female, 'Sujin', 'Premium'),
            NaverVoice(Language.ko_KR, 'njinho', Gender.Male, 'Jinho', 'Premium'),
            NaverVoice(Language.ko_KR, 'nsinu', Gender.Male, 'Shinwoo', 'Premium'),
            NaverVoice(Language.ko_KR, 'njihun', Gender.Male, 'Jihoon', 'Premium'),

            NaverVoice(Language.ja_JP, 'ntomoko', Gender.Female, 'Tomoko', 'Premium'),
            NaverVoice(Language.ja_JP, 'nnaomi', Gender.Female, 'Naomi', 'Premium'),
            NaverVoice(Language.ja_JP, 'nsayuri', Gender.Female, 'Sayuri', 'Premium'),

            NaverVoice(Language.ko_KR, 'ngoeun', Gender.Female, 'Koeun', 'Premium'),
            NaverVoice(Language.ko_KR, 'neunyoung', Gender.Female, 'Eunyoung', 'Premium'),
            NaverVoice(Language.ko_KR, 'nsunkyung', Gender.Female, 'Sunkyung', 'Premium'),
            NaverVoice(Language.ko_KR, 'nyujin', Gender.Female, 'Yujin', 'Premium'),
            
            NaverVoice(Language.ko_KR, 'ntaejin', Gender.Male, 'Taejin', 'Premium'),
            NaverVoice(Language.ko_KR, 'nyoungil', Gender.Male, 'Youngil', 'Premium'),
            NaverVoice(Language.ko_KR, 'nseungpyo', Gender.Male, 'Seungpyo', 'Premium'),
            NaverVoice(Language.ko_KR, 'nwontak', Gender.Male, 'Wontak', 'Premium'),                
        ]

    def get_voice_list(self):
        voice_list = [(voice.get_key(), voice.get_description()) for voice in self.get_voices()]
        voice_list.sort(key=lambda x: x[1])
        return voice_list

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

        client_id = options['clientid']
        client_secret = options['clientsecret']
        encText = urllib.parse.quote(text)
        voice = options['voice']
        speed = options['speed']
        pitch = options['pitch']

        data = f"speaker={voice}&speed={speed}&pitch={pitch}&text={encText}"
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

