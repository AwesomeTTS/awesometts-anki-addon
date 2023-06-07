

"""
ElevenLabs TTS service
https://beta.elevenlabs.io/
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

SERVICE_NAME = 'ElevenLabs'

__all__ = ['ElevenLabs']

class ElevenLabs(Service):
    DEFAULT_STABILITY = 0.75
    DEFAULT_SIMILARITY = 0.75

    __slots__ = [
    ]

    NAME = SERVICE_NAME

    TRAITS = []

    def desc(self):
        """Returns name with a voice count."""

        return f"{SERVICE_NAME} TTS service"

    def extras(self):
        if self.languagetools.use_plus_mode():
            # plus mode, no need for an API key
            return []        
        return [
            dict(key='api_key', label="API Key", required=True)
        ]

    def get_voices(self) -> List[StandardVoice]:
        voices = [x for x in VOICE_LIST if x['service'] == SERVICE_NAME]
        voices = sorted(voices, key=lambda x: x['voice_description'])
        voice_list = []
        for voice_data in voices:
            voice_list.append(StandardVoice(voice_data))
        assert len(voice_list) > 0
        return voice_list

    def get_voice_for_key(self, key) -> StandardVoice:
        voice = [voice for voice in self.get_voices() if voice.get_voice_key() == key]
        assert(len(voice) == 1)
        return voice[0]

    def get_voice_list(self):
        voice_list = self.get_voices()
        sorted_voice_data = sorted(voice_list, key=lambda x: x.get_description())
        return [(voice.get_voice_key(), voice.get_description()) for voice in sorted_voice_data]

    def options(self):
        """Provides access to voice only."""

        return [
            dict(key='voice',
                 label="Voice",
                 values=self.get_voice_list(),
                 transform=lambda value: value),
            dict(key='stability',
                label='Stability',
                values=(0.0, 1.0),
                default=0.75,
                transform=float),
            dict(key='similarity_boost',
                label='Similary',
                values=(0.0, 1.0),
                default=0.75,
                transform=float),
        ]

    def run(self, text, options, path):

        voice_key = options['voice']
        voice = self.get_voice_for_key(voice_key)

        if self.languagetools.use_plus_mode():

            self._logger.info(f'using language tools API')
            service = SERVICE_NAME
            voice_key = voice.get_voice_key()
            language = voice.get_language_code()
            options = {
                "stability": options.get('stability', self.DEFAULT_STABILITY),
                "similarity_boost": options.get('similarity_boost', self.DEFAULT_SIMILARITY)
            }
            self.languagetools.generate_audio_v2(text, service, 'batch', language, 'n/a', voice_key, options, path)

        else:

            api_key = options['api_key']

            voice_id = voice.voice_key['voice_id']
            url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'

            headers = {
                "Accept": "application/json",
                "xi-api-key": api_key
            }
            headers['Accept'] = "audio/mpeg"

            data = {
                "text": text,
                "model_id": voice.voice_key['model_id'],
                "voice_settings": {
                    "stability": options.get('stability', self.DEFAULT_STABILITY),
                    "similarity_boost": options.get('similarity_boost', self.DEFAULT_SIMILARITY)
                }
            }

            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()

            with open(path, 'wb') as audio:
                audio.write(response.content)
