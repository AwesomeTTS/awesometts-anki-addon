

"""
CereProc TTS service
https://www.cereproc.com/
"""

import time
import datetime
import requests
import json
import base64
from .base import Service
from .languages import StandardVoice
from .voicelist import VOICE_LIST
from typing import List

__all__ = ['CereProc']


class CereProc(Service):

    __slots__ = [
    ]

    NAME = "CereProc"

    TRAITS = []

    def desc(self):
        """Returns name with a voice count."""

        return "CereProc TTS Service"

    def extras(self):
        if self.languagetools.use_plus_mode():
            # plus mode, no need for an API key
            return []        
        return [dict(key='username', label="Username", required=True),
            dict(key='password', label="Password", required=True)
        ]

    def get_voices(self) -> List[StandardVoice]:
        voices = [x for x in VOICE_LIST if x['service'] == 'CereProc']
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

        return [
            dict(key='voice',
                 label="Voice",
                 values=self.get_voice_list(),
                 transform=lambda value: value),
        ]

    def get_access_token(self, username, password):
        combined = f'{username}:{password}'
        auth_string = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
        headers = {'authorization': f'Basic {auth_string}'}

        auth_url = 'https://api.cerevoice.com/v2/auth'
        response = requests.get(auth_url, headers=headers)

        access_token = response.json()['access_token']
        return access_token

    def get_auth_headers(self, username, password):
        headers={'Authorization': f'Bearer {self.get_access_token(username, password)}'}
        return headers

    def run(self, text, options, path):

        voice_key = options['voice']
        voice = self.get_voice_for_key(voice_key)

        if self.languagetools.use_plus_mode():

            self._logger.info(f'using language tools API')
            service = 'CereProc'
            voice_key = voice.get_voice_key()
            language = voice.get_language_code()
            options = {}
            self.languagetools.generate_audio_v2(text, service, 'batch', language, 'n/a', voice_key, options, path)

        else:

            voice_name = voice.get_key()

            username = options['username']
            password = options['password']

            ssml_text = f"""<?xml version="1.0" encoding="UTF-8"?>
    <speak xmlns="http://www.w3.org/2001/10/synthesis">{text}</speak>""".encode(encoding='utf-8')

            url = f'https://api.cerevoice.com/v2/speak?voice={voice_name}&audio_format=mp3'
            # logging.debug(f'querying url: {url}')            
            response = requests.post(url, data=ssml_text, headers=self.get_auth_headers(username, password))

            if response.status_code == 200:
                with open(path, 'wb') as audio:
                    audio.write(response.content)
            else:
                self._logger.error(response.content)
                error_message = f"Status code: {response.status_code} reason: {response.reason} voice: [{voice_name}]]]"
                raise ValueError(error_message)
