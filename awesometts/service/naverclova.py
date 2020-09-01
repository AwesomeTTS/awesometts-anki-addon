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
Service implementation for the Naver Clova cloud service
https://apidocs.ncloud.com/en/ai-naver/clova_speech_synthesis/tts/
"""

import time
import datetime
import requests
import urllib
from .base import Service

__all__ = ['NaverClova']

VOICE_LIST = [
    ('mijin', 'Korean, female voice'),
    ('jinho', 'Korean, male voice'),
    ('clara', 'English, female voice'),
    ('matt', 'English, male voice'),
    ('shinji', 'Japanese, male voice'),
    ('meimei', 'Chinese, female voice'),
    ('liangliang', 'Chinese, male voice'),
    ('jose', 'Spanish, male voice'),
    ('carmen', 'Spanish, female voice')
]



class NaverClova(Service):
    """
    Provides a Service-compliant implementation for Naver Clova Text To Speech.
    """

    __slots__ = [
    ]

    NAME = "Naver Clova"

    # Although Naver Clova is an Internet service, we do not mark it with
    # Trait.INTERNET, as it is a paid-for-by-the-user API, and we do not want
    # to rate-limit it or trigger error caching behavior
    TRAITS = []

    def desc(self):
        """Returns name with a voice count."""

        return "Naver Clova TTS API (%d voices)" % len(VOICE_LIST)

    def extras(self):
        """The Azure API requires an API key."""

        return [dict(key='clientid', label="API Client Id", required=True),
            dict(key='clientsecret', label="API Client Secret", required=True)]

    def options(self):

        return [
            dict(key='voice',
                 label="Voice",
                 values=VOICE_LIST,
                 transform=lambda value: value),
            dict(
                key='speed',
                label="Speed",
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
        speed = f"{options['speed']}"
        data = f"speaker={voice}&speed={speed}&text={encText}"
        url = "https://naveropenapi.apigw.ntruss.com/voice/v1/tts"
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

