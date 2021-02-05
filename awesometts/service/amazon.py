
"""
Service implementation for the Amazon/AWS Polly service, routed through the Language Tools backend
"""

import time
import datetime
import requests
from xml.etree import ElementTree
from .base import Service
from .languages import Gender
from .languages import Language
from .languages import Voice
from typing import List

__all__ = ['Amazon']


class AmazonVoice(Voice):
    def __init__(self, language: Language, gender: Gender, name: str, voice_id: str, engine: str):
        self.language = language
        self.gender = gender
        self.name = name
        self.voice_id = voice_id
        self.engine = engine

    def get_language(self) -> Language:
        return self.language

    def get_gender(self) -> Gender:
        return self.gender

    def get_key(self) -> str:
        return self.name

    def get_language_code(self) -> str:
        return self.language_code

    def get_voice_key(self):
        return {
            'voice_id': self.voice_id,
            'engine': self.engine
        }

    def get_description(self) -> str:
        value = f"{self.language.lang_name}, {self.gender.name}, {self.name} ({self.engine.capitalize()})"
        return value


class Amazon(Service):

    NAME = "Amazon"

    TRAITS = []

    def desc(self):
        """Returns name with a voice count."""

        return "Amazon AWS Polly (%d voices)" % len(VOICE_LIST)

    def extras(self):
        # no api key required, but this service is only usable with Language Tools
        return []

    def get_voices(self) -> List[AmazonVoice]:
        # generated using cloud language tools
        return [
            AmazonVoice(Language.nl_NL, Gender.Female, 'Lotte', 'Lotte', 'standard'),
            AmazonVoice(Language.ru_RU, Gender.Male, 'Maxim', 'Maxim', 'standard'),
            AmazonVoice(Language.en_US, Gender.Female, 'Salli', 'Salli', 'neural'),
            # AmazonVoice(Language.en_GB_WLS, Gender.Male, 'Geraint', 'Geraint', 'standard'),
            AmazonVoice(Language.es_US, Gender.Male, 'Miguel', 'Miguel', 'standard'),
            AmazonVoice(Language.de_DE, Gender.Female, 'Marlene', 'Marlene', 'standard'),
            AmazonVoice(Language.it_IT, Gender.Male, 'Giorgio', 'Giorgio', 'standard'),
            AmazonVoice(Language.pt_PT, Gender.Female, 'Inês', 'Ines', 'standard'),
            AmazonVoice(Language.ar_AR, Gender.Female, 'Zeina', 'Zeina', 'standard'),
            AmazonVoice(Language.zh_CN, Gender.Female, 'Zhiyu', 'Zhiyu', 'standard'),
            AmazonVoice(Language.cy_GB, Gender.Female, 'Gwyneth', 'Gwyneth', 'standard'),
            AmazonVoice(Language.is_IS, Gender.Male, 'Karl', 'Karl', 'standard'),
            AmazonVoice(Language.en_US, Gender.Female, 'Joanna', 'Joanna', 'neural'),
            AmazonVoice(Language.es_ES, Gender.Female, 'Lucia', 'Lucia', 'standard'),
            AmazonVoice(Language.pt_PT, Gender.Male, 'Cristiano', 'Cristiano', 'standard'),
            AmazonVoice(Language.sv_SE, Gender.Female, 'Astrid', 'Astrid', 'standard'),
            AmazonVoice(Language.de_DE, Gender.Female, 'Vicki', 'Vicki', 'standard'),
            AmazonVoice(Language.es_MX, Gender.Female, 'Mia', 'Mia', 'standard'),
            AmazonVoice(Language.it_IT, Gender.Female, 'Bianca', 'Bianca', 'standard'),
            AmazonVoice(Language.pt_BR, Gender.Female, 'Vitória', 'Vitoria', 'standard'),
            AmazonVoice(Language.en_IN, Gender.Female, 'Raveena', 'Raveena', 'standard'),
            AmazonVoice(Language.fr_CA, Gender.Female, 'Chantal', 'Chantal', 'standard'),
            AmazonVoice(Language.en_GB, Gender.Female, 'Amy', 'Amy', 'neural'),
            AmazonVoice(Language.en_GB, Gender.Male, 'Brian', 'Brian', 'neural'),
            AmazonVoice(Language.en_US, Gender.Male, 'Kevin', 'Kevin', 'neural'),
            AmazonVoice(Language.en_AU, Gender.Male, 'Russell', 'Russell', 'standard'),
            AmazonVoice(Language.en_IN, Gender.Female, 'Aditi', 'Aditi', 'standard'),
            AmazonVoice(Language.en_US, Gender.Male, 'Matthew', 'Matthew', 'neural'),
            AmazonVoice(Language.is_IS, Gender.Female, 'Dóra', 'Dora', 'standard'),
            AmazonVoice(Language.es_ES, Gender.Male, 'Enrique', 'Enrique', 'standard'),
            AmazonVoice(Language.de_DE, Gender.Male, 'Hans', 'Hans', 'standard'),
            AmazonVoice(Language.ro_RO, Gender.Female, 'Carmen', 'Carmen', 'standard'),
            AmazonVoice(Language.en_US, Gender.Female, 'Ivy', 'Ivy', 'neural'),
            AmazonVoice(Language.pl_PL, Gender.Female, 'Ewa', 'Ewa', 'standard'),
            AmazonVoice(Language.pl_PL, Gender.Female, 'Maja', 'Maja', 'standard'),
            AmazonVoice(Language.en_AU, Gender.Female, 'Nicole', 'Nicole', 'standard'),
            AmazonVoice(Language.pt_BR, Gender.Female, 'Camila', 'Camila', 'neural'),
            AmazonVoice(Language.tr_TR, Gender.Female, 'Filiz', 'Filiz', 'standard'),
            AmazonVoice(Language.pl_PL, Gender.Male, 'Jacek', 'Jacek', 'standard'),
            AmazonVoice(Language.en_US, Gender.Male, 'Justin', 'Justin', 'neural'),
            AmazonVoice(Language.fr_FR, Gender.Female, 'Céline', 'Celine', 'standard'),
            AmazonVoice(Language.en_US, Gender.Female, 'Kendra', 'Kendra', 'neural'),
            AmazonVoice(Language.pt_BR, Gender.Male, 'Ricardo', 'Ricardo', 'standard'),
            AmazonVoice(Language.da_DK, Gender.Male, 'Mads', 'Mads', 'standard'),
            AmazonVoice(Language.fr_FR, Gender.Male, 'Mathieu', 'Mathieu', 'standard'),
            AmazonVoice(Language.fr_FR, Gender.Female, 'Léa', 'Lea', 'standard'),
            AmazonVoice(Language.da_DK, Gender.Female, 'Naja', 'Naja', 'standard'),
            AmazonVoice(Language.es_US, Gender.Female, 'Penélope', 'Penelope', 'standard'),
            AmazonVoice(Language.ru_RU, Gender.Female, 'Tatyana', 'Tatyana', 'standard'),
            AmazonVoice(Language.en_AU, Gender.Female, 'Olivia', 'Olivia', 'neural'),
            AmazonVoice(Language.nl_NL, Gender.Male, 'Ruben', 'Ruben', 'standard'),
            AmazonVoice(Language.ja_JP, Gender.Female, 'Mizuki', 'Mizuki', 'standard'),
            AmazonVoice(Language.ja_JP, Gender.Male, 'Takumi', 'Takumi', 'standard'),
            AmazonVoice(Language.es_ES, Gender.Female, 'Conchita', 'Conchita', 'standard'),
            AmazonVoice(Language.it_IT, Gender.Female, 'Carla', 'Carla', 'standard'),
            AmazonVoice(Language.en_US, Gender.Female, 'Kimberly', 'Kimberly', 'neural'),
            AmazonVoice(Language.pl_PL, Gender.Male, 'Jan', 'Jan', 'standard'),
            AmazonVoice(Language.nb_NO, Gender.Female, 'Liv', 'Liv', 'standard'),
            AmazonVoice(Language.en_US, Gender.Male, 'Joey', 'Joey', 'neural'),
            AmazonVoice(Language.es_US, Gender.Female, 'Lupe', 'Lupe', 'neural'),
            AmazonVoice(Language.ko_KR, Gender.Female, 'Seoyeon', 'Seoyeon', 'standard'),
            AmazonVoice(Language.en_GB, Gender.Female, 'Emma', 'Emma', 'neural')
        ]


    def get_voice_for_key(self, key) -> AmazonVoice:
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
        options = {
            'pitch': pitch,
            'rate': rate
        }
        self.languagetools.generate_audio(text, service, voice_key, options, path)



