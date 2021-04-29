

"""
Service implementation for the IBM Watson Text-To-Speech service
https://cloud.ibm.com/docs/text-to-speech?topic=text-to-speech-gettingStarted
"""

import time
import datetime
import requests
import json
from .base import Service
from .languages import StandardVoice
from .voicelist import VOICE_LIST
from typing import List

__all__ = ['Watson']


class Watson(Service):

    __slots__ = [
        'access_token',
        'access_token_timestamp'
    ]

    NAME = "IBM Watson"

    TRAITS = []

    def desc(self):
        """Returns name with a voice count."""

        return "IBM Watson API"

    def extras(self):
        if self.languagetools.use_plus_mode():
            # plus mode, no need for an API key
            return []        
        return [dict(key='key', label="API Key", required=True),
            dict(key='url', label="API URL", required=True)
        ]

    def get_voices(self) -> List[StandardVoice]:
        voices = [x for x in VOICE_LIST if x['service'] == 'Watson']
        voices = sorted(voices, key=lambda x: x['voice_description'])
        voice_list = []
        for voice_data in voices:
            voice_list.append(StandardVoice(voice_data))
        return voice_list

    def get_voice_for_key(self, key) -> StandardVoice:
        voice = [voice for voice in self.get_voices() if voice.get_key() == key]
        assert(len(voice) == 1)
        return voice[0]


    def get_voice_list(self):
        voice_list = self.get_voices()
        sorted_voice_data = sorted(voice_list, key=lambda x: x.get_description())
        return [(voice.get_key(), voice.get_description()) for voice in sorted_voice_data]

    def options(self):
        """Provides access to voice only."""

        # make sure access token is requested when retrieving audio
        self.access_token = None

        return [
            dict(key='voice',
                 label="Voice",
                 values=self.get_voice_list(),
                 transform=lambda value: value),
        ]

    def run(self, text, options, path):
        """Downloads from Azure API directly to an MP3."""

        voice_key = options['voice']
        voice = self.get_voice_for_key(voice_key)

        if self.languagetools.use_plus_mode():

            self._logger.info(f'using language tools API')
            service = 'Watson'
            voice_key = voice.get_voice_key()
            language = voice.get_language_code()
            options = {}
            self.languagetools.generate_audio_v2(text, service, 'batch', language, 'n/a', voice_key, options, path)

        else:

            voice_name = voice.get_key()

            api_key = options['key']
            api_url = options['url']



            base_url = api_url
            url_path = '/v1/synthesize'
            constructed_url = base_url + url_path + f'?voice={voice_name}'
            self._logger.info(f'url: {constructed_url}')
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'audio/mp3'
            }

            data = {
                'text': text
            }

            self._logger.info(f'data: {data}')
            response = requests.post(constructed_url, data=json.dumps(data), auth=('apikey', api_key), headers=headers)

            if response.status_code == 200:
                with open(path, 'wb') as audio:
                    audio.write(response.content)
            else:
                self._logger.error(response.content)
                error_message = f"Status code: {response.status_code} reason: {response.reason} voice: [{voice_name}] api key: [{api_key}]]"
                raise ValueError(error_message)



