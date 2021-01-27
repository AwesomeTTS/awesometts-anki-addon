# -*- coding: utf-8 -*-

# AwesomeTTS text-to-speech add-on for Anki
# Copyright (C) 2010-Present  Anki AwesomeTTS Development Team
# Copyright (C) 2019 Nickolay <kelciour@gmail.com>
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
Service implementation for Google Cloud Text-to-Speech API
"""

import base64
import requests

from hashlib import sha1
from typing import List

from .base import Service
from .common import Trait
from .languages import Gender
from .languages import Language
from .languages import Voice

__all__ = ['GoogleTTS']

class GoogleVoice(Voice):
    def __init__(self, language: Language, gender: Gender, name: str, google_language_code: str):
        self.language = language
        self.gender = gender
        self.name = name
        self.google_language_code = google_language_code

    def get_language(self) -> Language:
        return self.language

    def get_gender(self) -> Gender:
        return self.gender

    def get_key(self) -> str:
        return self.name

    def get_language_code(self) -> str:
        return self.language_code

    def get_google_language_code(self):
        return self.google_language_code

    def get_description(self) -> str:
        value = f"{self.language.lang_name}, {self.gender.name}, {self.name}"
        return value

    def get_voice_key(self):
        return {
            'language_code': self.google_language_code,
            'name': self.name,
            'ssml_gender': self.gender.name.upper()
        }

class GoogleTTS(Service):
    """
    Provides a Service-compliant implementation for Google Cloud Text-to-Speech.
    """

    __slots__ = []

    NAME = "Google Cloud Text-to-Speech"

    TRAITS = [Trait.INTERNET]

    _audio_device_profile = [
        ("default", "Default"),
        ("wearable-class-device", "Smart watches and other wearables, like Apple Watch, Wear OS watch"),
        ("handset-class-device", "Smartphones, like Google Pixel, Samsung Galaxy, Apple iPhone"),
        ("headphone-class-device", "Earbuds or headphones for audio playback, like Sennheiser headphones"),
        ("small-bluetooth-speaker-class-device", "Small home speakers, like Google Home Mini"),
        ("medium-bluetooth-speaker-class-device", "Smart home speakers, like Google Home"),
        ("large-home-entertainment-class-device", "Home entertainment systems or smart TVs, like Google Home Max, LG TV"),
        ("large-automotive-class-device", "Car speakers"),
        ("telephony-class-application", "Interactive Voice Response (IVR) systems"),
    ]

    def _languageCode(self, name):
        """
        Returns a language code (en-US) from its name (en-US-Wavenet-A).
        """

        return '-'.join(name.split('-')[:2])


    def desc(self):
        """
        Returns a short, static description.
        """

        return "Google Cloud Text-to-Speech (%d voices)." % (
            len(set(map(lambda x: self._languageCode(x[0]), self._voice_list))))

    def extras(self):
        """The Google Cloud Text-to-Speech requires an API key."""

        if self.languagetools.use_plus_mode():
            # plus mode, no need for an API key
            return []
        return [dict(key='key', label="API Key", required=True)]

    def get_voices(self) -> List[GoogleVoice]:
        # generated using tools/service_google_voicelist.py
        return [
            GoogleVoice(Language.en_GB, Gender.Female, 'en-GB-Wavenet-A', 'en-GB'),
            GoogleVoice(Language.en_GB, Gender.Male, 'en-GB-Wavenet-B', 'en-GB'),
            GoogleVoice(Language.en_GB, Gender.Female, 'en-GB-Wavenet-C', 'en-GB'),
            GoogleVoice(Language.en_GB, Gender.Male, 'en-GB-Wavenet-D', 'en-GB'),
            GoogleVoice(Language.en_GB, Gender.Female, 'en-GB-Wavenet-F', 'en-GB'),
            GoogleVoice(Language.ar_AR, Gender.Female, 'ar-XA-Wavenet-A', 'ar-XA'),
            GoogleVoice(Language.ar_AR, Gender.Male, 'ar-XA-Wavenet-B', 'ar-XA'),
            GoogleVoice(Language.ar_AR, Gender.Male, 'ar-XA-Wavenet-C', 'ar-XA'),
            GoogleVoice(Language.zh_CN, Gender.Female, 'cmn-CN-Wavenet-A', 'cmn-CN'),
            GoogleVoice(Language.zh_CN, Gender.Male, 'cmn-CN-Wavenet-B', 'cmn-CN'),
            GoogleVoice(Language.zh_CN, Gender.Male, 'cmn-CN-Wavenet-C', 'cmn-CN'),
            GoogleVoice(Language.zh_CN, Gender.Female, 'cmn-CN-Wavenet-D', 'cmn-CN'),
            GoogleVoice(Language.zh_TW, Gender.Female, 'cmn-TW-Wavenet-A', 'cmn-TW'),
            GoogleVoice(Language.zh_TW, Gender.Male, 'cmn-TW-Wavenet-B', 'cmn-TW'),
            GoogleVoice(Language.zh_TW, Gender.Male, 'cmn-TW-Wavenet-C', 'cmn-TW'),
            GoogleVoice(Language.da_DK, Gender.Female, 'da-DK-Wavenet-A', 'da-DK'),
            GoogleVoice(Language.da_DK, Gender.Male, 'da-DK-Wavenet-C', 'da-DK'),
            GoogleVoice(Language.da_DK, Gender.Female, 'da-DK-Wavenet-D', 'da-DK'),
            GoogleVoice(Language.da_DK, Gender.Female, 'da-DK-Wavenet-E', 'da-DK'),
            GoogleVoice(Language.el_GR, Gender.Female, 'el-GR-Wavenet-A', 'el-GR'),
            GoogleVoice(Language.en_AU, Gender.Female, 'en-AU-Wavenet-A', 'en-AU'),
            GoogleVoice(Language.en_AU, Gender.Male, 'en-AU-Wavenet-B', 'en-AU'),
            GoogleVoice(Language.en_AU, Gender.Female, 'en-AU-Wavenet-C', 'en-AU'),
            GoogleVoice(Language.en_AU, Gender.Male, 'en-AU-Wavenet-D', 'en-AU'),
            GoogleVoice(Language.en_US, Gender.Female, 'en-US-Wavenet-G', 'en-US'),
            GoogleVoice(Language.en_US, Gender.Female, 'en-US-Wavenet-H', 'en-US'),
            GoogleVoice(Language.en_US, Gender.Male, 'en-US-Wavenet-I', 'en-US'),
            GoogleVoice(Language.en_US, Gender.Male, 'en-US-Wavenet-J', 'en-US'),
            GoogleVoice(Language.en_US, Gender.Male, 'en-US-Wavenet-A', 'en-US'),
            GoogleVoice(Language.en_US, Gender.Male, 'en-US-Wavenet-B', 'en-US'),
            GoogleVoice(Language.en_US, Gender.Female, 'en-US-Wavenet-C', 'en-US'),
            GoogleVoice(Language.en_US, Gender.Male, 'en-US-Wavenet-D', 'en-US'),
            GoogleVoice(Language.en_US, Gender.Female, 'en-US-Wavenet-E', 'en-US'),
            GoogleVoice(Language.en_US, Gender.Female, 'en-US-Wavenet-F', 'en-US'),
            GoogleVoice(Language.es_ES, Gender.Male, 'es-ES-Wavenet-B', 'es-ES'),
            GoogleVoice(Language.fi_FI, Gender.Female, 'fi-FI-Wavenet-A', 'fi-FI'),
            GoogleVoice(Language.fil_PH, Gender.Female, 'fil-PH-Wavenet-A', 'fil-PH'),
            GoogleVoice(Language.fil_PH, Gender.Female, 'fil-PH-Wavenet-B', 'fil-PH'),
            GoogleVoice(Language.fil_PH, Gender.Male, 'fil-PH-Wavenet-C', 'fil-PH'),
            GoogleVoice(Language.fil_PH, Gender.Male, 'fil-PH-Wavenet-D', 'fil-PH'),
            GoogleVoice(Language.fr_CA, Gender.Female, 'fr-CA-Wavenet-A', 'fr-CA'),
            GoogleVoice(Language.fr_CA, Gender.Male, 'fr-CA-Wavenet-B', 'fr-CA'),
            GoogleVoice(Language.fr_CA, Gender.Female, 'fr-CA-Wavenet-C', 'fr-CA'),
            GoogleVoice(Language.fr_CA, Gender.Male, 'fr-CA-Wavenet-D', 'fr-CA'),
            GoogleVoice(Language.hu_HU, Gender.Female, 'hu-HU-Wavenet-A', 'hu-HU'),
            GoogleVoice(Language.ja_JP, Gender.Female, 'ja-JP-Wavenet-A', 'ja-JP'),
            GoogleVoice(Language.ja_JP, Gender.Female, 'ja-JP-Wavenet-B', 'ja-JP'),
            GoogleVoice(Language.ja_JP, Gender.Male, 'ja-JP-Wavenet-C', 'ja-JP'),
            GoogleVoice(Language.ja_JP, Gender.Male, 'ja-JP-Wavenet-D', 'ja-JP'),
            GoogleVoice(Language.nb_NO, Gender.Female, 'nb-no-Wavenet-E', 'nb-NO'),
            GoogleVoice(Language.nb_NO, Gender.Female, 'nb-NO-Wavenet-A', 'nb-NO'),
            GoogleVoice(Language.nb_NO, Gender.Male, 'nb-NO-Wavenet-B', 'nb-NO'),
            GoogleVoice(Language.nb_NO, Gender.Female, 'nb-NO-Wavenet-C', 'nb-NO'),
            GoogleVoice(Language.nb_NO, Gender.Male, 'nb-NO-Wavenet-D', 'nb-NO'),
            GoogleVoice(Language.nl_NL, Gender.Male, 'nl-NL-Wavenet-B', 'nl-NL'),
            GoogleVoice(Language.nl_NL, Gender.Male, 'nl-NL-Wavenet-C', 'nl-NL'),
            GoogleVoice(Language.nl_NL, Gender.Female, 'nl-NL-Wavenet-D', 'nl-NL'),
            GoogleVoice(Language.nl_NL, Gender.Female, 'nl-NL-Wavenet-E', 'nl-NL'),
            GoogleVoice(Language.nl_NL, Gender.Female, 'nl-NL-Wavenet-A', 'nl-NL'),
            GoogleVoice(Language.pl_PL, Gender.Female, 'pl-PL-Wavenet-A', 'pl-PL'),
            GoogleVoice(Language.pl_PL, Gender.Male, 'pl-PL-Wavenet-B', 'pl-PL'),
            GoogleVoice(Language.pl_PL, Gender.Male, 'pl-PL-Wavenet-C', 'pl-PL'),
            GoogleVoice(Language.pl_PL, Gender.Female, 'pl-PL-Wavenet-D', 'pl-PL'),
            GoogleVoice(Language.pl_PL, Gender.Female, 'pl-PL-Wavenet-E', 'pl-PL'),
            GoogleVoice(Language.pt_BR, Gender.Female, 'pt-BR-Wavenet-A', 'pt-BR'),
            GoogleVoice(Language.pt_PT, Gender.Female, 'pt-PT-Wavenet-A', 'pt-PT'),
            GoogleVoice(Language.pt_PT, Gender.Male, 'pt-PT-Wavenet-B', 'pt-PT'),
            GoogleVoice(Language.pt_PT, Gender.Male, 'pt-PT-Wavenet-C', 'pt-PT'),
            GoogleVoice(Language.pt_PT, Gender.Female, 'pt-PT-Wavenet-D', 'pt-PT'),
            GoogleVoice(Language.sk_SK, Gender.Female, 'sk-SK-Wavenet-A', 'sk-SK'),
            GoogleVoice(Language.sv_SE, Gender.Female, 'sv-SE-Wavenet-A', 'sv-SE'),
            GoogleVoice(Language.tr_TR, Gender.Female, 'tr-TR-Wavenet-A', 'tr-TR'),
            GoogleVoice(Language.tr_TR, Gender.Male, 'tr-TR-Wavenet-B', 'tr-TR'),
            GoogleVoice(Language.tr_TR, Gender.Female, 'tr-TR-Wavenet-C', 'tr-TR'),
            GoogleVoice(Language.tr_TR, Gender.Female, 'tr-TR-Wavenet-D', 'tr-TR'),
            GoogleVoice(Language.tr_TR, Gender.Male, 'tr-TR-Wavenet-E', 'tr-TR'),
            GoogleVoice(Language.vi_VN, Gender.Female, 'vi-VN-Wavenet-A', 'vi-VN'),
            GoogleVoice(Language.vi_VN, Gender.Male, 'vi-VN-Wavenet-B', 'vi-VN'),
            GoogleVoice(Language.vi_VN, Gender.Female, 'vi-VN-Wavenet-C', 'vi-VN'),
            GoogleVoice(Language.vi_VN, Gender.Male, 'vi-VN-Wavenet-D', 'vi-VN'),
            GoogleVoice(Language.cs_CZ, Gender.Female, 'cs-CZ-Wavenet-A', 'cs-CZ'),
            GoogleVoice(Language.de_DE, Gender.Female, 'de-DE-Wavenet-F', 'de-DE'),
            GoogleVoice(Language.de_DE, Gender.Female, 'de-DE-Wavenet-A', 'de-DE'),
            GoogleVoice(Language.de_DE, Gender.Male, 'de-DE-Wavenet-B', 'de-DE'),
            GoogleVoice(Language.de_DE, Gender.Female, 'de-DE-Wavenet-C', 'de-DE'),
            GoogleVoice(Language.de_DE, Gender.Male, 'de-DE-Wavenet-D', 'de-DE'),
            GoogleVoice(Language.de_DE, Gender.Male, 'de-DE-Wavenet-E', 'de-DE'),
            GoogleVoice(Language.en_IN, Gender.Female, 'en-IN-Wavenet-D', 'en-IN'),
            GoogleVoice(Language.en_IN, Gender.Female, 'en-IN-Wavenet-A', 'en-IN'),
            GoogleVoice(Language.en_IN, Gender.Male, 'en-IN-Wavenet-B', 'en-IN'),
            GoogleVoice(Language.en_IN, Gender.Male, 'en-IN-Wavenet-C', 'en-IN'),
            GoogleVoice(Language.fr_FR, Gender.Female, 'fr-FR-Wavenet-E', 'fr-FR'),
            GoogleVoice(Language.fr_FR, Gender.Female, 'fr-FR-Wavenet-A', 'fr-FR'),
            GoogleVoice(Language.fr_FR, Gender.Male, 'fr-FR-Wavenet-B', 'fr-FR'),
            GoogleVoice(Language.fr_FR, Gender.Female, 'fr-FR-Wavenet-C', 'fr-FR'),
            GoogleVoice(Language.fr_FR, Gender.Male, 'fr-FR-Wavenet-D', 'fr-FR'),
            GoogleVoice(Language.hi_IN, Gender.Female, 'hi-IN-Wavenet-D', 'hi-IN'),
            GoogleVoice(Language.hi_IN, Gender.Female, 'hi-IN-Wavenet-A', 'hi-IN'),
            GoogleVoice(Language.hi_IN, Gender.Male, 'hi-IN-Wavenet-B', 'hi-IN'),
            GoogleVoice(Language.hi_IN, Gender.Male, 'hi-IN-Wavenet-C', 'hi-IN'),
            GoogleVoice(Language.id_ID, Gender.Female, 'id-ID-Wavenet-D', 'id-ID'),
            GoogleVoice(Language.id_ID, Gender.Female, 'id-ID-Wavenet-A', 'id-ID'),
            GoogleVoice(Language.id_ID, Gender.Male, 'id-ID-Wavenet-B', 'id-ID'),
            GoogleVoice(Language.id_ID, Gender.Male, 'id-ID-Wavenet-C', 'id-ID'),
            GoogleVoice(Language.it_IT, Gender.Female, 'it-IT-Wavenet-A', 'it-IT'),
            GoogleVoice(Language.it_IT, Gender.Female, 'it-IT-Wavenet-B', 'it-IT'),
            GoogleVoice(Language.it_IT, Gender.Male, 'it-IT-Wavenet-C', 'it-IT'),
            GoogleVoice(Language.it_IT, Gender.Male, 'it-IT-Wavenet-D', 'it-IT'),
            GoogleVoice(Language.ko_KR, Gender.Female, 'ko-KR-Wavenet-A', 'ko-KR'),
            GoogleVoice(Language.ko_KR, Gender.Female, 'ko-KR-Wavenet-B', 'ko-KR'),
            GoogleVoice(Language.ko_KR, Gender.Male, 'ko-KR-Wavenet-C', 'ko-KR'),
            GoogleVoice(Language.ko_KR, Gender.Male, 'ko-KR-Wavenet-D', 'ko-KR'),
            GoogleVoice(Language.ru_RU, Gender.Female, 'ru-RU-Wavenet-E', 'ru-RU'),
            GoogleVoice(Language.ru_RU, Gender.Female, 'ru-RU-Wavenet-A', 'ru-RU'),
            GoogleVoice(Language.ru_RU, Gender.Male, 'ru-RU-Wavenet-B', 'ru-RU'),
            GoogleVoice(Language.ru_RU, Gender.Female, 'ru-RU-Wavenet-C', 'ru-RU'),
            GoogleVoice(Language.ru_RU, Gender.Male, 'ru-RU-Wavenet-D', 'ru-RU'),
            GoogleVoice(Language.uk_UA, Gender.Female, 'uk-UA-Wavenet-A', 'uk-UA'),
            GoogleVoice(Language.es_ES, Gender.Male, 'es-ES-Standard-B', 'es-ES'),
            GoogleVoice(Language.es_ES, Gender.Female, 'es-ES-Standard-A', 'es-ES'),
            GoogleVoice(Language.en_US, Gender.Male, 'en-US-Standard-B', 'en-US'),
            GoogleVoice(Language.en_US, Gender.Female, 'en-US-Standard-C', 'en-US'),
            GoogleVoice(Language.en_US, Gender.Male, 'en-US-Standard-D', 'en-US'),
            GoogleVoice(Language.en_US, Gender.Female, 'en-US-Standard-E', 'en-US'),
            GoogleVoice(Language.en_US, Gender.Female, 'en-US-Standard-G', 'en-US'),
            GoogleVoice(Language.en_US, Gender.Female, 'en-US-Standard-H', 'en-US'),
            GoogleVoice(Language.en_US, Gender.Male, 'en-US-Standard-I', 'en-US'),
            GoogleVoice(Language.en_US, Gender.Male, 'en-US-Standard-J', 'en-US'),
            GoogleVoice(Language.ar_AR, Gender.Female, 'ar-XA-Standard-A', 'ar-XA'),
            GoogleVoice(Language.ar_AR, Gender.Male, 'ar-XA-Standard-B', 'ar-XA'),
            GoogleVoice(Language.ar_AR, Gender.Male, 'ar-XA-Standard-C', 'ar-XA'),
            GoogleVoice(Language.ar_AR, Gender.Female, 'ar-XA-Standard-D', 'ar-XA'),
            GoogleVoice(Language.fr_FR, Gender.Female, 'fr-FR-Standard-E', 'fr-FR'),
            GoogleVoice(Language.it_IT, Gender.Female, 'it-IT-Standard-A', 'it-IT'),
            GoogleVoice(Language.ru_RU, Gender.Female, 'ru-RU-Standard-E', 'ru-RU'),
            GoogleVoice(Language.ru_RU, Gender.Female, 'ru-RU-Standard-A', 'ru-RU'),
            GoogleVoice(Language.ru_RU, Gender.Male, 'ru-RU-Standard-B', 'ru-RU'),
            GoogleVoice(Language.ru_RU, Gender.Female, 'ru-RU-Standard-C', 'ru-RU'),
            GoogleVoice(Language.ru_RU, Gender.Male, 'ru-RU-Standard-D', 'ru-RU'),
            GoogleVoice(Language.zh_CN, Gender.Female, 'cmn-CN-Standard-D', 'cmn-CN'),
            GoogleVoice(Language.zh_CN, Gender.Male, 'cmn-CN-Standard-C', 'cmn-CN'),
            GoogleVoice(Language.zh_CN, Gender.Male, 'cmn-CN-Standard-B', 'cmn-CN'),
            GoogleVoice(Language.zh_CN, Gender.Female, 'cmn-CN-Standard-A', 'cmn-CN'),
            GoogleVoice(Language.ja_JP, Gender.Female, 'ja-JP-Standard-A', 'ja-JP'),
            GoogleVoice(Language.ja_JP, Gender.Male, 'ja-JP-Standard-C', 'ja-JP'),
            GoogleVoice(Language.ja_JP, Gender.Female, 'ja-JP-Standard-B', 'ja-JP'),
            GoogleVoice(Language.ja_JP, Gender.Male, 'ja-JP-Standard-D', 'ja-JP'),
            GoogleVoice(Language.zh_TW, Gender.Female, 'cmn-TW-Standard-A', 'cmn-TW'),
            GoogleVoice(Language.zh_TW, Gender.Male, 'cmn-TW-Standard-B', 'cmn-TW'),
            GoogleVoice(Language.zh_TW, Gender.Male, 'cmn-TW-Standard-C', 'cmn-TW'),
            GoogleVoice(Language.ko_KR, Gender.Female, 'ko-KR-Standard-B', 'ko-KR'),
            GoogleVoice(Language.ko_KR, Gender.Male, 'ko-KR-Standard-C', 'ko-KR'),
            GoogleVoice(Language.ko_KR, Gender.Male, 'ko-KR-Standard-D', 'ko-KR'),
            GoogleVoice(Language.ko_KR, Gender.Female, 'ko-KR-Standard-A', 'ko-KR'),
            GoogleVoice(Language.vi_VN, Gender.Female, 'vi-VN-Standard-A', 'vi-VN'),
            GoogleVoice(Language.vi_VN, Gender.Male, 'vi-VN-Standard-B', 'vi-VN'),
            GoogleVoice(Language.vi_VN, Gender.Female, 'vi-VN-Standard-C', 'vi-VN'),
            GoogleVoice(Language.vi_VN, Gender.Male, 'vi-VN-Standard-D', 'vi-VN'),
            GoogleVoice(Language.id_ID, Gender.Female, 'id-ID-Standard-D', 'id-ID'),
            GoogleVoice(Language.id_ID, Gender.Female, 'id-ID-Standard-A', 'id-ID'),
            GoogleVoice(Language.id_ID, Gender.Male, 'id-ID-Standard-B', 'id-ID'),
            GoogleVoice(Language.id_ID, Gender.Male, 'id-ID-Standard-C', 'id-ID'),
            GoogleVoice(Language.nl_NL, Gender.Male, 'nl-NL-Standard-B', 'nl-NL'),
            GoogleVoice(Language.nl_NL, Gender.Male, 'nl-NL-Standard-C', 'nl-NL'),
            GoogleVoice(Language.nl_NL, Gender.Female, 'nl-NL-Standard-D', 'nl-NL'),
            GoogleVoice(Language.nl_NL, Gender.Female, 'nl-NL-Standard-E', 'nl-NL'),
            GoogleVoice(Language.nl_NL, Gender.Female, 'nl-NL-Standard-A', 'nl-NL'),
            GoogleVoice(Language.fil_PH, Gender.Female, 'fil-PH-Standard-B', 'fil-PH'),
            GoogleVoice(Language.fil_PH, Gender.Male, 'fil-PH-Standard-C', 'fil-PH'),
            GoogleVoice(Language.fil_PH, Gender.Male, 'fil-PH-Standard-D', 'fil-PH'),
            GoogleVoice(Language.fil_PH, Gender.Female, 'fil-PH-Standard-A', 'fil-PH'),
            GoogleVoice(Language.zh_HK, Gender.Female, 'yue-HK-Standard-A', 'yue-HK'),
            GoogleVoice(Language.zh_HK, Gender.Male, 'yue-HK-Standard-B', 'yue-HK'),
            GoogleVoice(Language.zh_HK, Gender.Female, 'yue-HK-Standard-C', 'yue-HK'),
            GoogleVoice(Language.zh_HK, Gender.Male, 'yue-HK-Standard-D', 'yue-HK'),
            GoogleVoice(Language.cs_CZ, Gender.Female, 'cs-CZ-Standard-A', 'cs-CZ'),
            GoogleVoice(Language.el_GR, Gender.Female, 'el-GR-Standard-A', 'el-GR'),
            GoogleVoice(Language.pt_BR, Gender.Female, 'pt-BR-Standard-A', 'pt-BR'),
            GoogleVoice(Language.hu_HU, Gender.Female, 'hu-HU-Standard-A', 'hu-HU'),
            GoogleVoice(Language.pl_PL, Gender.Female, 'pl-PL-Standard-E', 'pl-PL'),
            GoogleVoice(Language.ro_RO, Gender.Female, 'ro-RO-Standard-A', 'ro-RO'),
            GoogleVoice(Language.sk_SK, Gender.Female, 'sk-SK-Standard-A', 'sk-SK'),
            GoogleVoice(Language.uk_UA, Gender.Female, 'uk-UA-Standard-A', 'uk-UA'),
            GoogleVoice(Language.pl_PL, Gender.Female, 'pl-PL-Standard-A', 'pl-PL'),
            GoogleVoice(Language.pl_PL, Gender.Male, 'pl-PL-Standard-B', 'pl-PL'),
            GoogleVoice(Language.pl_PL, Gender.Male, 'pl-PL-Standard-C', 'pl-PL'),
            GoogleVoice(Language.pl_PL, Gender.Female, 'pl-PL-Standard-D', 'pl-PL'),
            GoogleVoice(Language.tr_TR, Gender.Male, 'tr-TR-Standard-B', 'tr-TR'),
            GoogleVoice(Language.tr_TR, Gender.Female, 'tr-TR-Standard-C', 'tr-TR'),
            GoogleVoice(Language.tr_TR, Gender.Female, 'tr-TR-Standard-D', 'tr-TR'),
            GoogleVoice(Language.tr_TR, Gender.Male, 'tr-TR-Standard-E', 'tr-TR'),
            GoogleVoice(Language.tr_TR, Gender.Female, 'tr-TR-Standard-A', 'tr-TR'),
            GoogleVoice(Language.th_TH, Gender.Female, 'th-TH-Standard-A', 'th-TH'),
            GoogleVoice(Language.bn_IN, Gender.Female, 'bn-IN-Standard-A', 'bn-IN'),
            GoogleVoice(Language.bn_IN, Gender.Male, 'bn-IN-Standard-B', 'bn-IN'),
            GoogleVoice(Language.en_IN, Gender.Female, 'en-IN-Standard-D', 'en-IN'),
            GoogleVoice(Language.en_IN, Gender.Female, 'en-IN-Standard-A', 'en-IN'),
            GoogleVoice(Language.en_IN, Gender.Male, 'en-IN-Standard-B', 'en-IN'),
            GoogleVoice(Language.en_IN, Gender.Male, 'en-IN-Standard-C', 'en-IN'),
            GoogleVoice(Language.gu_IN, Gender.Female, 'gu-IN-Standard-A', 'gu-IN'),
            GoogleVoice(Language.gu_IN, Gender.Male, 'gu-IN-Standard-B', 'gu-IN'),
            GoogleVoice(Language.hi_IN, Gender.Female, 'hi-IN-Standard-D', 'hi-IN'),
            GoogleVoice(Language.hi_IN, Gender.Female, 'hi-IN-Standard-A', 'hi-IN'),
            GoogleVoice(Language.hi_IN, Gender.Male, 'hi-IN-Standard-B', 'hi-IN'),
            GoogleVoice(Language.hi_IN, Gender.Male, 'hi-IN-Standard-C', 'hi-IN'),
            GoogleVoice(Language.kn_IN, Gender.Female, 'kn-IN-Standard-A', 'kn-IN'),
            GoogleVoice(Language.kn_IN, Gender.Male, 'kn-IN-Standard-B', 'kn-IN'),
            GoogleVoice(Language.ml_IN, Gender.Female, 'ml-IN-Standard-A', 'ml-IN'),
            GoogleVoice(Language.ml_IN, Gender.Male, 'ml-IN-Standard-B', 'ml-IN'),
            GoogleVoice(Language.ta_IN, Gender.Female, 'ta-IN-Standard-A', 'ta-IN'),
            GoogleVoice(Language.ta_IN, Gender.Male, 'ta-IN-Standard-B', 'ta-IN'),
            GoogleVoice(Language.te_IN, Gender.Female, 'te-IN-Standard-A', 'te-IN'),
            GoogleVoice(Language.te_IN, Gender.Male, 'te-IN-Standard-B', 'te-IN'),
            GoogleVoice(Language.da_DK, Gender.Female, 'da-DK-Standard-A', 'da-DK'),
            GoogleVoice(Language.da_DK, Gender.Male, 'da-DK-Standard-C', 'da-DK'),
            GoogleVoice(Language.da_DK, Gender.Female, 'da-DK-Standard-D', 'da-DK'),
            GoogleVoice(Language.da_DK, Gender.Female, 'da-DK-Standard-E', 'da-DK'),
            GoogleVoice(Language.fi_FI, Gender.Female, 'fi-FI-Standard-A', 'fi-FI'),
            GoogleVoice(Language.sv_SE, Gender.Female, 'sv-SE-Standard-A', 'sv-SE'),
            GoogleVoice(Language.nb_NO, Gender.Female, 'nb-NO-Standard-A', 'nb-NO'),
            GoogleVoice(Language.nb_NO, Gender.Male, 'nb-NO-Standard-B', 'nb-NO'),
            GoogleVoice(Language.nb_NO, Gender.Female, 'nb-NO-Standard-C', 'nb-NO'),
            GoogleVoice(Language.nb_NO, Gender.Male, 'nb-NO-Standard-D', 'nb-NO'),
            GoogleVoice(Language.nb_NO, Gender.Female, 'nb-no-Standard-E', 'nb-NO'),
            GoogleVoice(Language.nb_NO, Gender.Female, 'nb-no-Standard-E', 'nb-NO'),
            GoogleVoice(Language.pt_PT, Gender.Female, 'pt-PT-Standard-A', 'pt-PT'),
            GoogleVoice(Language.pt_PT, Gender.Male, 'pt-PT-Standard-B', 'pt-PT'),
            GoogleVoice(Language.pt_PT, Gender.Male, 'pt-PT-Standard-C', 'pt-PT'),
            GoogleVoice(Language.pt_PT, Gender.Female, 'pt-PT-Standard-D', 'pt-PT'),
            GoogleVoice(Language.fr_FR, Gender.Female, 'fr-FR-Standard-A', 'fr-FR'),
            GoogleVoice(Language.fr_FR, Gender.Male, 'fr-FR-Standard-B', 'fr-FR'),
            GoogleVoice(Language.fr_FR, Gender.Female, 'fr-FR-Standard-C', 'fr-FR'),
            GoogleVoice(Language.fr_FR, Gender.Male, 'fr-FR-Standard-D', 'fr-FR'),
            GoogleVoice(Language.de_DE, Gender.Male, 'de-DE-Standard-E', 'de-DE'),
            GoogleVoice(Language.de_DE, Gender.Female, 'de-DE-Standard-A', 'de-DE'),
            GoogleVoice(Language.de_DE, Gender.Male, 'de-DE-Standard-B', 'de-DE'),
            GoogleVoice(Language.de_DE, Gender.Female, 'de-DE-Standard-F', 'de-DE'),
            GoogleVoice(Language.fr_CA, Gender.Female, 'fr-CA-Standard-A', 'fr-CA'),
            GoogleVoice(Language.fr_CA, Gender.Male, 'fr-CA-Standard-B', 'fr-CA'),
            GoogleVoice(Language.fr_CA, Gender.Female, 'fr-CA-Standard-C', 'fr-CA'),
            GoogleVoice(Language.fr_CA, Gender.Male, 'fr-CA-Standard-D', 'fr-CA'),
            GoogleVoice(Language.it_IT, Gender.Female, 'it-IT-Standard-B', 'it-IT'),
            GoogleVoice(Language.it_IT, Gender.Male, 'it-IT-Standard-C', 'it-IT'),
            GoogleVoice(Language.it_IT, Gender.Male, 'it-IT-Standard-D', 'it-IT'),
            GoogleVoice(Language.en_AU, Gender.Female, 'en-AU-Standard-A', 'en-AU'),
            GoogleVoice(Language.en_AU, Gender.Male, 'en-AU-Standard-B', 'en-AU'),
            GoogleVoice(Language.en_AU, Gender.Female, 'en-AU-Standard-C', 'en-AU'),
            GoogleVoice(Language.en_AU, Gender.Male, 'en-AU-Standard-D', 'en-AU'),
            GoogleVoice(Language.en_GB, Gender.Female, 'en-GB-Standard-A', 'en-GB'),
            GoogleVoice(Language.en_GB, Gender.Male, 'en-GB-Standard-B', 'en-GB'),
            GoogleVoice(Language.en_GB, Gender.Female, 'en-GB-Standard-C', 'en-GB'),
            GoogleVoice(Language.en_GB, Gender.Male, 'en-GB-Standard-D', 'en-GB'),
            GoogleVoice(Language.en_GB, Gender.Female, 'en-GB-Standard-F', 'en-GB'),


        ]


    def get_voice_list(self):
        sorted_voices = self.get_voices()
        sorted_voices.sort(key=lambda x: x.get_description())
        return [(voice.get_key(), voice.get_description()) for voice in sorted_voices]

    def get_voice_for_key(self, key) -> GoogleVoice:
        voice = [voice for voice in self.get_voices() if voice.get_key() == key]
        assert(len(voice) == 1)
        return voice[0]

    def options(self):
        """
        Provides access to voice only.
        """

        return [
            dict(
                key='voice',
                label="Voice",
                values=self.get_voice_list(),
                transform=lambda value: value,
                default='en-US-Wavenet-D',
            ),

            dict(
                key='speed',
                label="Speed",
                values=(0.25, 4),
                transform=float,
                default=1.00,
            ),

            dict(
                key='pitch',
                label="Pitch",
                values=(-20.00, 20.00),
                transform=float,
                default=0.00,
            ),

            dict(
                key='profile',
                label="Profile",
                values=self._audio_device_profile,
                transform=lambda value: value,
                default='default',
            )
        ]

    def run(self, text, options, path):
        """
        Send a synthesis request to the Text-to-Speech API and
        decode the base64-encoded string into an audio file.
        """

        voice = self.get_voice_for_key(options['voice'])

        if self.languagetools.use_plus_mode():
            self._logger.info(f'using language tools API')
            service = 'Google'
            voice_key = voice.get_voice_key()
            options = {
                'pitch': options['pitch'],
                'speaking_rate': options['speed']
            }
            self.languagetools.generate_audio(text, service, voice_key, options, path)
        else:
            payload = {
                "audioConfig": {
                    "audioEncoding": "MP3",
                    "pitch": options['pitch'],
                    "speakingRate": options['speed'],
                },
                "input": {
                    "ssml": f"<speak>{text}</speak>"
                },
                "voice": {
                    "languageCode": self._languageCode(options['voice']),
                    "name": options['voice'],
                }
            }

            headers = {}
            if sha1(options['key'].encode("utf-8")).hexdigest() == "8224a632410a845cbb4b20f9aef131b495f7ad7f":
                headers['x-origin'] = 'https://explorer.apis.google.com'

            if options['profile'] != 'default':
                payload["audioConfig"]["effectsProfileId"] = [options['profile']]

            r = requests.post("https://texttospeech.googleapis.com/v1/text:synthesize?key={}".format(options['key']), headers=headers, json=payload)
            r.raise_for_status()

            data = r.json()
            encoded = data['audioContent']
            audio_content = base64.b64decode(encoded)

            with open(path, 'wb') as response_output:
                response_output.write(audio_content)
