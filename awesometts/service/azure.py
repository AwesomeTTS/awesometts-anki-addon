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
Service implementation for the Microsoft Azure Text-To-Speech service
https://azure.microsoft.com/en-us/services/cognitive-services/text-to-speech/
"""

import time
import datetime
import requests
from xml.etree import ElementTree
from .base import Service
from .languages import Gender
from .languages import Language
from .languages import Voice
from .voicelist import VOICE_LIST
from typing import List

__all__ = ['Azure']


REGIONS = [
('centralus', 'Americas, Central US'),
('eastus', 'Americas, East US'),
('eastus2', 'Americas, East US 2'),
('northcentralus', 'Americas, North Central US'),
('southcentralus', 'Americas, South Central US'),
('westcentralus', 'Americas, West Central US'),
('westus', 'Americas, West US'),
('westus2', 'Americas, West US 2'),
('canadacentral', 'Americas, Canada Central'),
('brazilsouth', 'Americas, Brazil South'),
('eastasia', 'Asia Pacific, East Asia'),
('southeastasia', 'Asia Pacific, Southeast Asia'),
('australiaeast', 'Asia Pacific, Australia East'),
('centralindia', 'Asia Pacific, Central India'),
('japaneast', 'Asia Pacific, Japan East'),
('japanwest', 'Asia Pacific, Japan West'),
('koreacentral', 'Asia Pacific, Korea Central'),
('northeurope', 'Europe, North Europe'),
('westeurope', 'Europe, West Europe'),
('francecentral', 'Europe, France Central'),
('switzerlandnorth', 'Europe, Switzerland North'),
('uksouth', 'Europe, UK South'),
]

class AzureVoice(Voice):
    def __init__(self, voice_data):
        self.language_code = voice_data['language_code']
        self.voice_key = voice_data['voice_key']
        self.voice_description = voice_data['voice_description']

    def get_key(self) -> str:
        return self.voice_key['name']

    def get_language_code(self) -> str:
        return self.language_code

    def get_voice_key(self):
        return self.voice_key

    def get_description(self) -> str:
        return self.voice_description


class Azure(Service):
    """
    Provides a Service-compliant implementation for Microsoft Azure Text To Speech.
    """

    __slots__ = [
        'access_token',
        'access_token_timestamp'
    ]

    NAME = "Microsoft Azure"

    # Although Azure is an Internet service, we do not mark it with
    # Trait.INTERNET, as it is a paid-for-by-the-user API, and we do not want
    # to rate-limit it or trigger error caching behavior
    TRAITS = []

    def desc(self):
        """Returns name with a voice count."""

        return "Microft Azure API (%d voices)" % len(self.get_voices())

    def extras(self):
        """The Azure API requires an API key."""
        if self.languagetools.use_plus_mode():
            # plus mode, no need for an API key
            return []
        return [dict(key='key', label="API Key", required=True)]

    def get_voices(self) -> List[AzureVoice]:
        # generated using tools/service_azure_voicelist.py
        azure_voices = [x for x in VOICE_LIST if x['service'] == 'Azure']
        azure_voices = sorted(azure_voices, key=lambda x: x['voice_description'])
        voice_list = []
        for voice_data in azure_voices:
            voice_list.append(AzureVoice(voice_data))
        return voice_list

    def get_voice_for_key(self, key) -> AzureVoice:
        voice = [voice for voice in self.get_voices() if voice.get_key() == key]
        assert(len(voice) == 1)
        return voice[0]


    def get_voice_list(self):
        return [(voice.get_key(), voice.get_description()) for voice in self.get_voices()]

    def options(self):
        """Provides access to voice only."""

        # make sure access token is requested when retrieving audio
        self.access_token = None

        result = [
            dict(key='voice',
                 label="Voice",
                 values=self.get_voice_list(),
                 transform=lambda value: value),
            dict(key='azurespeed',
                label='Speed',
                values=(0.5, 3.0),
                default=1.0,
                transform=float),
            dict(key='azurepitch',
                label='Pitch',
                values=(-100, 100),
                default=0,
                transform=int),
            
        ]

        if not self.languagetools.use_plus_mode():
            result.append(dict(key='region',
                 label='Region',
                 values=REGIONS,
                 default='eastus',
                 transform=lambda value: value))
            
        return result

    def get_token(self, subscription_key, region):
        if len(subscription_key) == 0:
            raise ValueError("subscription key required")

        fetch_token_url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        self.access_token = str(response.text)
        self.access_token_timestamp = datetime.datetime.now()
        self._logger.debug(f'requested access_token')



    def token_refresh_required(self):
        if self.access_token == None:
            self._logger.debug(f'no token, must request')
            return True
        time_diff = datetime.datetime.now() - self.access_token_timestamp
        if time_diff.total_seconds() > 300:
            self._logger.debug(f'time_diff: {time_diff}, requesting token')
            return True
        return False

    def run(self, text, options, path):
        """Downloads from Azure API directly to an MP3."""

        voice_key = options['voice']
        voice = self.get_voice_for_key(voice_key)

        rate = options['azurespeed']
        pitch = options['azurepitch']

        sleep_time = self.config.get('service_azure_sleep_time', 0)

        if self.languagetools.use_plus_mode():
            self._logger.info(f'using language tools API')
            service = 'Azure'
            voice_key = voice.get_voice_key()
            language = voice.get_language_code()
            options = {
                'pitch': pitch,
                'rate': rate
            }
            self.languagetools.generate_audio_v2(text, service, 'batch', language, 'n/a', voice_key, options, path)
        else:

            region = options['region']
            subscription_key = options['key']
            if self.token_refresh_required():
                self.get_token(subscription_key, region)

            voice_name = voice.get_key()
            language = voice.get_language_code()

            base_url = f'https://{region}.tts.speech.microsoft.com/'
            url_path = 'cognitiveservices/v1'
            constructed_url = base_url + url_path
            headers = {
                'Authorization': 'Bearer ' + self.access_token,
                'Content-Type': 'application/ssml+xml',
                'X-Microsoft-OutputFormat': 'audio-24khz-96kbitrate-mono-mp3',
                'User-Agent': 'anki-awesome-tts'
            }

            ssml_str = f"""<speak version="1.0" xmlns="https://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
<voice name="{voice_name}"><prosody rate="{rate:0.1f}" pitch="{pitch:+.0f}Hz" >{text}</prosody></voice>
</speak>""".replace('\n', '')
            
            body = ssml_str.encode(encoding='utf-8')

            response = requests.post(constructed_url, headers=headers, data=body)
            if response.status_code == 200:
                with open(path, 'wb') as audio:
                    audio.write(response.content)
            else:
                error_message = f"Status code: {response.status_code} reason: {response.reason} voice: [{voice_name}] language: [{language} " + \
                f"subscription key: [{subscription_key}]] access token timestamp: [{self.access_token_timestamp}] access token: [{self.access_token}]"
                raise ValueError(error_message)

            self._logger.debug(f'sleeping for {sleep_time} seconds')
            time.sleep(sleep_time)


