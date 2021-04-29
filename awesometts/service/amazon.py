
"""
Service implementation for the Amazon/AWS Polly service, routed through the Language Tools backend
"""

import time
import datetime
import requests
from xml.etree import ElementTree
from .base import Service
from .languages import StandardVoice
from .voicelist import VOICE_LIST
from typing import List

__all__ = ['Amazon']

class AmazonVoice(StandardVoice):
    def __init__(self, voice_data):
        StandardVoice.__init__(self, voice_data)

    def get_key(self) -> str:
        return self.voice_key

class Amazon(Service):

    NAME = "Amazon"

    TRAITS = []

    def desc(self):
        """Returns name with a voice count."""

        return "Amazon AWS Polly (%d voices)" % len(self.get_voices())

    def extras(self):
        # no api key required, but this service is only usable with Language Tools
        return []

    def get_voices(self) -> List[StandardVoice]:
        voices = [x for x in VOICE_LIST if x['service'] == 'Amazon']
        voices = sorted(voices, key=lambda x: x['voice_description'])
        voice_list = []
        for voice_data in voices:
            voice_list.append(AmazonVoice(voice_data))
        return voice_list


    def get_voice_for_key(self, key) -> AmazonVoice:
        voice = [voice for voice in self.get_voices() if voice.get_key() == key]
        assert(len(voice) == 1)
        return voice[0]


    def get_voice_list(self):
        voice_list = [(voice.get_key(), voice.get_description()) for voice in self.get_voices()]
        voice_list.sort(key=lambda x: x[1])
        return voice_list

    def options(self):
        """Provides access to voice only."""

        # make sure access token is requested when retrieving audio
        self.access_token = None

        result = [
            dict(key='voice',
                 label="Voice",
                 values=self.get_voice_list(),
                 transform=lambda value: value),
            dict(key='rate',
                label='Speed',
                values=(20, 200),
                default=100,
                transform=float),
            dict(key='pitch',
                label='Pitch',
                values=(-50, 50),
                default=0,
                transform=int),
            
        ]
            
        return result

    
    def run(self, text, options, path):

        if not self.languagetools.use_plus_mode():
            raise ValueError(f'Amazon is only available on AwesomeTTS Plus')

        voice_key = options['voice']
        voice = self.get_voice_for_key(voice_key)

        rate = options['rate']
        pitch = options['pitch']

        self._logger.info(f'using language tools API')
        service = 'Amazon'
        voice_key = voice.get_voice_key()
        language = voice.get_language_code()
        options = {
            'pitch': pitch,
            'rate': rate
        }
        self.languagetools.generate_audio_v2(text, service, 'batch', language, 'n/a', voice_key, options, path)



