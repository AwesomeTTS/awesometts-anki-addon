"""
Service implementation for VocalWare TTS service
"""

from .base import Service
import requests
import json
import time
import urllib
import hashlib
from .languages import StandardVoice
from .voicelist import VOICE_LIST
from typing import List

__all__ = ['VocalWare']



class VocalWare(Service):

    __slots__ = [
    ]

    NAME = "VocalWare"

    TRAITS = []

    def desc(self):
        """Returns name with a voice count."""

        return "VocalWare Text to Speech Service"

    def extras(self):
        """The VocalWare API requires API identifiers"""

        if self.languagetools.use_plus_mode():
            # plus mode, no need for an API key
            return []        

        return [
            dict(key='secretphrase', label="Secret Phrase", required=True),
            dict(key='accountid', label="Account ID", required=True),
            dict(key='apiid', label="API ID", required=True),
        ]


    def get_voices(self) -> List[StandardVoice]:
        voices = [x for x in VOICE_LIST if x['service'] == 'VocalWare']
        voices = sorted(voices, key=lambda x: x['voice_description'])
        voice_list = []
        for voice_data in voices:
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
        ]

    def run(self, text, options, path):
        
        voice_key = options['voice']
        voice = self.get_voice_for_key(voice_key)

        if self.languagetools.use_plus_mode():
            self._logger.info(f'using language tools API')
            service = 'VocalWare'
            voice_key = voice.get_voice_key()
            language = voice.get_language_code()
            options = {
            }
            self.languagetools.generate_audio_v2(text, service, 'batch', language, 'n/a', voice_key, options, path)        
        else:
            secret_phrase = options['secretphrase']
            account_id = options['accountid']
            api_id = options['apiid']

            urlencoded_text = urllib.parse.unquote_plus(text)

            # checksum calculation
            # CS = md5 (EID + LID + VID + TXT + EXT + FX_TYPE + FX_LEVEL + ACC + API+ SESSION + HTTP_ERR + SECRET PHRASE)
            checksum_input = f"""{voice_key['engine_id']}{voice_key['language_id']}{voice_key['voice_id']}{text}{account_id}{api_id}{secret_phrase}"""
            checksum = hashlib.md5(checksum_input.encode('utf-8')).hexdigest()

            url_parameters = f"""EID={voice_key['engine_id']}&LID={voice_key['language_id']}&VID={voice_key['voice_id']}&TXT={urlencoded_text}&ACC={account_id}&API={api_id}&CS={checksum}"""
            url = f"""http://www.vocalware.com/tts/gen.php?{url_parameters}"""

            response = requests.get(url)
            if response.status_code == 200:
                with open(path, 'wb') as audio:
                    audio.write(response.content)
            else:
                error_message = f"Ran into error generating VocalWare voice, status code: {response.status_code}: {response.content}"
                raise ValueError(error_message)


