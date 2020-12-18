

"""
Service implementation for the IBM Watson Text-To-Speech service
https://cloud.ibm.com/docs/text-to-speech?topic=text-to-speech-gettingStarted
"""

import time
import datetime
import requests
import json
from .base import Service
from .languages import Gender
from .languages import Language
from .languages import Voice
from typing import List

__all__ = ['Watson']


class WatsonVoice(Voice):
    def __init__(self, language: Language, gender: Gender, name: str, description: str, voice_name: str):
        self.language = language
        self.gender = gender
        self.name = name
        self.voice_name = voice_name
        self.description = description

    def get_language(self) -> Language:
        return self.language

    def get_gender(self) -> Gender:
        return self.gender

    def get_key(self) -> str:
        return self.name

    def get_description(self) -> str:
        description = f"{self.language.lang_name}, {self.gender.name}, {self.voice_name}"
        return description


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
        return [dict(key='key', label="API Key", required=True)]

    def get_voices(self) -> List[WatsonVoice]:
        # generated using tools/service_watson_voicelist.py
        return [
            WatsonVoice(Language.de_DE, Gender.Female, 'de-DE_ErikaV3Voice', 'Erika: Standard German (Standarddeutsch) female voice. Dnn technology.', 'Erika (Dnn)' ),
            WatsonVoice(Language.pt_BR, Gender.Female, 'pt-BR_IsabelaVoice', 'Isabela: Brazilian Portuguese (português brasileiro) female voice.', 'Isabela' ),
            WatsonVoice(Language.en_GB, Gender.Female, 'en-GB_KateV3Voice', 'Kate: British English female voice. Dnn technology.', 'Kate (Dnn)' ),
            WatsonVoice(Language.fr_FR, Gender.Male, 'fr-FR_NicolasV3Voice', 'Nicolas: French (français) male voice. Dnn technology.', 'Nicolas (Dnn)' ),
            WatsonVoice(Language.es_ES, Gender.Male, 'es-ES_EnriqueV3Voice', 'Enrique: Castilian Spanish (español castellano) male voice. Dnn technology.', 'Enrique (Dnn)' ),
            WatsonVoice(Language.de_DE, Gender.Female, 'de-DE_BirgitV3Voice', 'Birgit: Standard German (Standarddeutsch) female voice. Dnn technology.', 'Birgit (Dnn)' ),
            WatsonVoice(Language.en_GB, Gender.Male, 'en-GB_JamesV3Voice', 'James: British English male voice. Dnn technology.', 'James (Dnn)' ),
            WatsonVoice(Language.es_ES, Gender.Female, 'es-ES_LauraV3Voice', 'Laura: Castilian Spanish (español castellano) female voice. Dnn technology.', 'Laura (Dnn)' ),
            WatsonVoice(Language.it_IT, Gender.Female, 'it-IT_FrancescaV2Voice', 'Francesca: Italian (italiano) female voice. Dnn technology.', 'Francesca (Dnn)' ),
            WatsonVoice(Language.en_US, Gender.Female, 'en-US_AllisonV2Voice', 'Allison: American English female voice. Dnn technology.', 'Allison (Dnn)' ),
            WatsonVoice(Language.es_LA, Gender.Female, 'es-LA_SofiaV3Voice', 'Sofia: Latin American Spanish (español latinoamericano) female voice. Dnn technology.', 'Sofia (Dnn)' ),
            WatsonVoice(Language.en_US, Gender.Female, 'en-US_AllisonV3Voice', 'Allison: American English female voice. Dnn technology.', 'Allison (Dnn)' ),
            WatsonVoice(Language.de_DE, Gender.Female, 'de-DE_BirgitV2Voice', 'Birgit: Standard German (Standarddeutsch) female voice. Dnn technology.', 'Birgit (Dnn)' ),
            WatsonVoice(Language.it_IT, Gender.Female, 'it-IT_FrancescaV3Voice', 'Francesca: Italian (italiano) female voice. Dnn technology.', 'Francesca (Dnn)' ),
            WatsonVoice(Language.en_GB, Gender.Female, 'en-GB_CharlotteV3Voice', 'Charlotte: British English female voice. Dnn technology.', 'Charlotte (Dnn)' ),
            WatsonVoice(Language.es_LA, Gender.Female, 'es-LA_SofiaVoice', 'Sofia: Latin American Spanish (español latinoamericano) female voice.', 'Sofia' ),
            WatsonVoice(Language.en_US, Gender.Female, 'en-US_LisaV3Voice', 'Lisa: American English female voice. Dnn technology.', 'Lisa (Dnn)' ),
            WatsonVoice(Language.en_US, Gender.Male, 'en-US_MichaelV3Voice', 'Michael: American English male voice. Dnn technology.', 'Michael (Dnn)' ),
            WatsonVoice(Language.en_US, Gender.Female, 'en-US_LisaV2Voice', 'Lisa: American English female voice. Dnn technology.', 'Lisa (Dnn)' ),
            WatsonVoice(Language.en_US, Gender.Female, 'en-US_EmilyV3Voice', 'Emily: American English female voice. Dnn technology.', 'Emily (Dnn)' ),
            WatsonVoice(Language.en_US, Gender.Male, 'en-US_MichaelV2Voice', 'Michael: American English male voice. Dnn technology.', 'Michael (Dnn)' ),
            WatsonVoice(Language.fr_FR, Gender.Female, 'fr-FR_ReneeV3Voice', 'Renee: French (français) female voice. Dnn technology.', 'Renee (Dnn)' ),
            WatsonVoice(Language.en_US, Gender.Male, 'en-US_KevinV3Voice', 'Kevin: American English male voice. Dnn technology.', 'Kevin (Dnn)' ),
            WatsonVoice(Language.en_US, Gender.Female, 'en-US_OliviaV3Voice', 'Olivia: American English female voice. Dnn technology.', 'Olivia (Dnn)' ),
            WatsonVoice(Language.es_US, Gender.Female, 'es-US_SofiaV3Voice', 'Sofia: North American Spanish (español norteamericano) female voice. Dnn technology.', 'Sofia (Dnn)' ),
            WatsonVoice(Language.en_US, Gender.Male, 'en-US_HenryV3Voice', 'Henry: American English male voice. Dnn technology.', 'Henry (Dnn)' ),
            WatsonVoice(Language.de_DE, Gender.Male, 'de-DE_DieterV3Voice', 'Dieter: Standard German (Standarddeutsch) male voice. Dnn technology.', 'Dieter (Dnn)' ),
            WatsonVoice(Language.ja_JP, Gender.Female, 'ja-JP_EmiV3Voice', 'Emi: Japanese (日本語) female voice. Dnn technology.', 'Emi (Dnn)' ),
            WatsonVoice(Language.pt_BR, Gender.Female, 'pt-BR_IsabelaV3Voice', 'Isabela: Brazilian Portuguese (português brasileiro) female voice. Dnn technology.', 'Isabela (Dnn)' ),
            WatsonVoice(Language.de_DE, Gender.Male, 'de-DE_DieterV2Voice', 'Dieter: Standard German (Standarddeutsch) male voice. Dnn technology.', 'Dieter (Dnn)' ),
            WatsonVoice(Language.de_DE, Gender.Male, 'de-DE_DieterVoice', 'Dieter: Standard German (Standarddeutsch) male voice.', 'Dieter' ),
            WatsonVoice(Language.ja_JP, Gender.Female, 'ja-JP_EmiVoice', 'Emi: Japanese (日本語) female voice.', 'Emi' ),
            WatsonVoice(Language.en_US, Gender.Female, 'en-US_AllisonVoice', 'Allison: American English female voice.', 'Allison' ),
            WatsonVoice(Language.fr_FR, Gender.Female, 'fr-FR_ReneeVoice', 'Renee: French (français) female voice.', 'Renee' ),
            WatsonVoice(Language.es_US, Gender.Female, 'es-US_SofiaVoice', 'Sofia: North American Spanish (español norteamericano) female voice.', 'Sofia' ),
            WatsonVoice(Language.en_GB, Gender.Female, 'en-GB_KateVoice', 'Kate: British English female voice.', 'Kate' ),
            WatsonVoice(Language.en_US, Gender.Male, 'en-US_MichaelVoice', 'Michael: American English male voice.', 'Michael' ),
            WatsonVoice(Language.es_ES, Gender.Male, 'es-ES_EnriqueVoice', 'Enrique: Castilian Spanish (español castellano) male voice.', 'Enrique' ),
            WatsonVoice(Language.it_IT, Gender.Female, 'it-IT_FrancescaVoice', 'Francesca: Italian (italiano) female voice.', 'Francesca' ),
            WatsonVoice(Language.es_ES, Gender.Female, 'es-ES_LauraVoice', 'Laura: Castilian Spanish (español castellano) female voice.', 'Laura' ),
            WatsonVoice(Language.en_US, Gender.Female, 'en-US_LisaVoice', 'Lisa: American English female voice.', 'Lisa' ),
            WatsonVoice(Language.de_DE, Gender.Female, 'de-DE_BirgitVoice', 'Birgit: Standard German (Standarddeutsch) female voice.', 'Birgit' ),
            WatsonVoice(Language.ar_AR, Gender.Male, 'ar-MS_OmarVoice', 'Omar: Arabic male voice.', 'Omar' ),
            WatsonVoice(Language.en_AU, Gender.Male, 'en-AU_CraigVoice', 'Craig: Australian English male voice.', 'Craig' ),
            WatsonVoice(Language.en_AU, Gender.Female, 'en-AU_MadisonVoice', 'Madison: Australian English female voice.', 'Madison' ),
            WatsonVoice(Language.ko_KR, Gender.Male, 'ko-KR_HyunjunVoice', 'Hyunjun: Korean male voice.', 'Hyunjun' ),
            WatsonVoice(Language.ko_KR, Gender.Male, 'ko-KR_SiWooVoice', 'SiWoo: Korean male voice.', 'SiWoo' ),
            WatsonVoice(Language.ko_KR, Gender.Female, 'ko-KR_YoungmiVoice', 'Youngmi: Korean female voice.', 'Youngmi' ),
            WatsonVoice(Language.ko_KR, Gender.Female, 'ko-KR_YunaVoice', 'Yuna: Korean female voice.', 'Yuna' ),
            WatsonVoice(Language.nl_NL, Gender.Female, 'nl-NL_EmmaVoice', 'Emma: Dutch female voice.', 'Emma' ),
            WatsonVoice(Language.nl_NL, Gender.Male, 'nl-NL_LiamVoice', 'Liam: Dutch male voice.', 'Liam' ),
            WatsonVoice(Language.zh_CN, Gender.Female, 'zh-CN_LiNaVoice', 'Li Na: Chinese (Mandarin) female voice.', 'Li Na' ),
            WatsonVoice(Language.zh_CN, Gender.Male, 'zh-CN_WangWeiVoice', 'Wang Wei: Chinese (Mandarin) male voice.', 'Wang Wei' ),
            WatsonVoice(Language.zh_CN, Gender.Female, 'zh-CN_ZhangJingVoice', 'Zhang Jing: Chinese (Mandarin) female voice.', 'Zhang Jing' )
        ]


    def get_voice_for_key(self, key) -> WatsonVoice:
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

        api_key = options['key']

        voice_key = options['voice']
        voice = self.get_voice_for_key(voice_key)
        voice_name = voice.get_key()

        base_url = 'https://api.us-south.text-to-speech.watson.cloud.ibm.com/instances/7f62cf20-2944-4d83-bd53-b6f11a64de9b'
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



