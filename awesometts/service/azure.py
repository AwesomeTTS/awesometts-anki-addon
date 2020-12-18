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
('uksouth', 'Europe, UK South'),
]

SPEEDS = [
    ('x-slow', 'Extra Slow'),
    ('slow', 'Slow'),
    ('medium', 'Medium'),
    ('default', 'Default'),
    ('fast', 'Fast'),
    ('x-fast', 'Extra Fast')
]

PITCH = [
    ('x-low', 'Extra Low'),
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('default', 'Default'),
    ('high', 'High'),
    ('x-high', 'Extra High')
]

class AzureVoice(Voice):
    # {'Name': 'Microsoft Server Speech Text to Speech Voice (en-US, GuyNeural)', 
    # 'DisplayName': 'Guy', 'LocalName': 'Guy', 'ShortName': 'en-US-GuyNeural',
    #  'Gender': 'Male', 'Locale': 'en-US', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'English (US)'},
    def __init__(self, language: Language, gender: Gender, name: str, display_name: str, local_name: str, short_name: str, voice_type: str, language_code: str):
        self.language = language
        self.gender = gender
        self.name = name
        self.display_name = display_name
        self.local_name = local_name
        self.voice_type = voice_type
        self.language_code = language_code

    def get_language(self) -> Language:
        return self.language

    def get_gender(self) -> Gender:
        return self.gender

    def get_key(self) -> str:
        return self.name

    def get_language_code(self) -> str:
        return self.language_code

    def get_description(self) -> str:
        display_name = self.display_name
        if self.display_name != self.local_name:
            display_name = f"{self.display_name}, {self.local_name}"
        value = f"{self.language.lang_name}, {self.gender.name}, {self.voice_type}, {display_name}"
        return value


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

        return "Microft Azure API (%d voices)" % len(VOICE_LIST)

    def extras(self):
        """The Azure API requires an API key."""

        return [dict(key='key', label="API Key", required=True)]

    def get_voices(self) -> List[AzureVoice]:
        # generated using tools/service_azure_voicelist.py
        return [
            AzureVoice(Language.ar_EG, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ar-EG, SalmaNeural)', 'Salma','سلمى', 'ar-EG-SalmaNeural', 'Neural', 'ar-EG'),
            AzureVoice(Language.ar_EG, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (ar-EG, ShakirNeural)', 'Shakir','شاكر', 'ar-EG-ShakirNeural', 'Neural', 'ar-EG'),
            AzureVoice(Language.ar_EG, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ar-EG, Hoda)', 'Hoda','هدى', 'ar-EG-Hoda', 'Standard', 'ar-EG'),
            AzureVoice(Language.ar_SA, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (ar-SA, HamedNeural)', 'Hamed','حامد', 'ar-SA-HamedNeural', 'Neural', 'ar-SA'),
            AzureVoice(Language.ar_SA, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ar-SA, ZariyahNeural)', 'Zariyah','زارية', 'ar-SA-ZariyahNeural', 'Neural', 'ar-SA'),
            AzureVoice(Language.ar_SA, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (ar-SA, Naayf)', 'Naayf','نايف', 'ar-SA-Naayf', 'Standard', 'ar-SA'),
            AzureVoice(Language.bg_BG, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (bg-BG, BorislavNeural)', 'Borislav','Борислав', 'bg-BG-BorislavNeural', 'Neural', 'bg-BG'),
            AzureVoice(Language.bg_BG, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (bg-BG, KalinaNeural)', 'Kalina','Калина', 'bg-BG-KalinaNeural', 'Neural', 'bg-BG'),
            AzureVoice(Language.bg_BG, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (bg-BG, Ivan)', 'Ivan','Иван', 'bg-BG-Ivan', 'Standard', 'bg-BG'),
            AzureVoice(Language.ca_ES, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ca-ES, JoanaNeural)', 'Joana','Joana', 'ca-ES-JoanaNeural', 'Neural', 'ca-ES'),
            AzureVoice(Language.ca_ES, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ca-ES, AlbaNeural)', 'Alba','Alba', 'ca-ES-AlbaNeural', 'Neural', 'ca-ES'),
            AzureVoice(Language.ca_ES, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (ca-ES, EnricNeural)', 'Enric','Enric', 'ca-ES-EnricNeural', 'Neural', 'ca-ES'),
            AzureVoice(Language.ca_ES, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ca-ES, HerenaRUS)', 'Herena','Helena', 'ca-ES-HerenaRUS', 'Standard', 'ca-ES'),
            AzureVoice(Language.zh_HK, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (zh-HK, HiuMaanNeural)', 'HiuMaan','曉曼', 'zh-HK-HiuMaanNeural', 'Neural', 'zh-HK'),
            AzureVoice(Language.zh_HK, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (zh-HK, HiuGaaiNeural)', 'HiuGaai','曉佳', 'zh-HK-HiuGaaiNeural', 'Neural', 'zh-HK'),
            AzureVoice(Language.zh_HK, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (zh-HK, WanLungNeural)', 'WanLung','雲龍', 'zh-HK-WanLungNeural', 'Neural', 'zh-HK'),
            AzureVoice(Language.zh_HK, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (zh-HK, Danny)', 'Danny','Danny', 'zh-HK-Danny', 'Standard', 'zh-HK'),
            AzureVoice(Language.zh_HK, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (zh-HK, TracyRUS)', 'Tracy','Tracy', 'zh-HK-TracyRUS', 'Standard', 'zh-HK'),
            AzureVoice(Language.zh_CN, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoxiaoNeural)', 'Xiaoxiao','晓晓', 'zh-CN-XiaoxiaoNeural', 'Neural', 'zh-CN'),
            AzureVoice(Language.zh_CN, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (zh-CN, YunyangNeural)', 'Yunyang','云扬', 'zh-CN-YunyangNeural', 'Neural', 'zh-CN'),
            AzureVoice(Language.zh_CN, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoyouNeural)', 'Xiaoyou','晓悠', 'zh-CN-XiaoyouNeural', 'Neural', 'zh-CN'),
            AzureVoice(Language.zh_CN, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (zh-CN, YunyeNeural)', 'Yunye','云野', 'zh-CN-YunyeNeural', 'Neural', 'zh-CN'),
            AzureVoice(Language.zh_CN, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (zh-CN, XiaohanNeural)', 'Xiaohan','晓涵', 'zh-CN-XiaohanNeural', 'Neural', 'zh-CN'),
            AzureVoice(Language.zh_CN, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (zh-CN, XiaomoNeural)', 'Xiaomo','晓墨', 'zh-CN-XiaomoNeural', 'Neural', 'zh-CN'),
            AzureVoice(Language.zh_CN, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoruiNeural)', 'Xiaorui','晓睿', 'zh-CN-XiaoruiNeural', 'Neural', 'zh-CN'),
            AzureVoice(Language.zh_CN, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoxuanNeural)', 'Xiaoxuan','晓萱', 'zh-CN-XiaoxuanNeural', 'Neural', 'zh-CN'),
            AzureVoice(Language.zh_CN, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (zh-CN, YunxiNeural)', 'Yunxi','云希', 'zh-CN-YunxiNeural', 'Neural', 'zh-CN'),
            AzureVoice(Language.zh_CN, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (zh-CN, HuihuiRUS)', 'Huihui','慧慧', 'zh-CN-HuihuiRUS', 'Standard', 'zh-CN'),
            AzureVoice(Language.zh_CN, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (zh-CN, Kangkang)', 'Kangkang','康康', 'zh-CN-Kangkang', 'Standard', 'zh-CN'),
            AzureVoice(Language.zh_CN, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (zh-CN, Yaoyao)', 'Yaoyao','瑶瑶', 'zh-CN-Yaoyao', 'Standard', 'zh-CN'),
            AzureVoice(Language.zh_TW, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (zh-TW, HsiaoChenNeural)', 'HsiaoChen','曉臻', 'zh-TW-HsiaoChenNeural', 'Neural', 'zh-TW'),
            AzureVoice(Language.zh_TW, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (zh-TW, HsiaoYuNeural)', 'HsiaoYu','曉雨', 'zh-TW-HsiaoYuNeural', 'Neural', 'zh-TW'),
            AzureVoice(Language.zh_TW, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (zh-TW, YunJheNeural)', 'YunJhe','雲哲', 'zh-TW-YunJheNeural', 'Neural', 'zh-TW'),
            AzureVoice(Language.zh_TW, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (zh-TW, HanHanRUS)', 'HanHan','涵涵', 'zh-TW-HanHanRUS', 'Standard', 'zh-TW'),
            AzureVoice(Language.zh_TW, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (zh-TW, Yating)', 'Yating','雅婷', 'zh-TW-Yating', 'Standard', 'zh-TW'),
            AzureVoice(Language.zh_TW, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (zh-TW, Zhiwei)', 'Zhiwei','志威', 'zh-TW-Zhiwei', 'Standard', 'zh-TW'),
            AzureVoice(Language.hr_HR, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (hr-HR, GabrijelaNeural)', 'Gabrijela','Gabrijela', 'hr-HR-GabrijelaNeural', 'Neural', 'hr-HR'),
            AzureVoice(Language.hr_HR, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (hr-HR, SreckoNeural)', 'Srecko','Srećko', 'hr-HR-SreckoNeural', 'Neural', 'hr-HR'),
            AzureVoice(Language.hr_HR, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (hr-HR, Matej)', 'Matej','Matej', 'hr-HR-Matej', 'Standard', 'hr-HR'),
            AzureVoice(Language.cs_CZ, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (cs-CZ, AntoninNeural)', 'Antonin','Antonín', 'cs-CZ-AntoninNeural', 'Neural', 'cs-CZ'),
            AzureVoice(Language.cs_CZ, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (cs-CZ, VlastaNeural)', 'Vlasta','Vlasta', 'cs-CZ-VlastaNeural', 'Neural', 'cs-CZ'),
            AzureVoice(Language.cs_CZ, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (cs-CZ, Jakub)', 'Jakub','Jakub', 'cs-CZ-Jakub', 'Standard', 'cs-CZ'),
            AzureVoice(Language.da_DK, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (da-DK, ChristelNeural)', 'Christel','Christel', 'da-DK-ChristelNeural', 'Neural', 'da-DK'),
            AzureVoice(Language.da_DK, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (da-DK, JeppeNeural)', 'Jeppe','Jeppe', 'da-DK-JeppeNeural', 'Neural', 'da-DK'),
            AzureVoice(Language.da_DK, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (da-DK, HelleRUS)', 'Helle','Helle', 'da-DK-HelleRUS', 'Standard', 'da-DK'),
            AzureVoice(Language.nl_NL, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (nl-NL, ColetteNeural)', 'Colette','Colette', 'nl-NL-ColetteNeural', 'Neural', 'nl-NL'),
            AzureVoice(Language.nl_NL, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (nl-NL, FennaNeural)', 'Fenna','Fenna', 'nl-NL-FennaNeural', 'Neural', 'nl-NL'),
            AzureVoice(Language.nl_NL, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (nl-NL, MaartenNeural)', 'Maarten','Maarten', 'nl-NL-MaartenNeural', 'Neural', 'nl-NL'),
            AzureVoice(Language.nl_NL, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (nl-NL, HannaRUS)', 'Hanna','Hanna', 'nl-NL-HannaRUS', 'Standard', 'nl-NL'),
            AzureVoice(Language.en_AU, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (en-AU, NatashaNeural)', 'Natasha','Natasha', 'en-AU-NatashaNeural', 'Neural', 'en-AU'),
            AzureVoice(Language.en_AU, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (en-AU, WilliamNeural)', 'William','William', 'en-AU-WilliamNeural', 'Neural', 'en-AU'),
            AzureVoice(Language.en_AU, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (en-AU, Catherine)', 'Catherine','Catherine', 'en-AU-Catherine', 'Standard', 'en-AU'),
            AzureVoice(Language.en_AU, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (en-AU, HayleyRUS)', 'Hayley','Hayley', 'en-AU-HayleyRUS', 'Standard', 'en-AU'),
            AzureVoice(Language.en_CA, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (en-CA, ClaraNeural)', 'Clara','Clara', 'en-CA-ClaraNeural', 'Neural', 'en-CA'),
            AzureVoice(Language.en_CA, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (en-CA, LiamNeural)', 'Liam','Liam', 'en-CA-LiamNeural', 'Neural', 'en-CA'),
            AzureVoice(Language.en_CA, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (en-CA, HeatherRUS)', 'Heather','Heather', 'en-CA-HeatherRUS', 'Standard', 'en-CA'),
            AzureVoice(Language.en_CA, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (en-CA, Linda)', 'Linda','Linda', 'en-CA-Linda', 'Standard', 'en-CA'),
            AzureVoice(Language.en_IN, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (en-IN, NeerjaNeural)', 'Neerja','Neerja', 'en-IN-NeerjaNeural', 'Neural', 'en-IN'),
            AzureVoice(Language.en_IN, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (en-IN, PrabhatNeural)', 'Prabhat','Prabhat', 'en-IN-PrabhatNeural', 'Neural', 'en-IN'),
            AzureVoice(Language.en_IN, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (en-IN, Heera)', 'Heera','Heera', 'en-IN-Heera', 'Standard', 'en-IN'),
            AzureVoice(Language.en_IN, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (en-IN, PriyaRUS)', 'Priya','Priya', 'en-IN-PriyaRUS', 'Standard', 'en-IN'),
            AzureVoice(Language.en_IN, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (en-IN, Ravi)', 'Ravi','Ravi', 'en-IN-Ravi', 'Standard', 'en-IN'),
            AzureVoice(Language.en_IE, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (en-IE, ConnorNeural)', 'Connor','Connor', 'en-IE-ConnorNeural', 'Neural', 'en-IE'),
            AzureVoice(Language.en_IE, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (en-IE, EmilyNeural)', 'Emily','Emily', 'en-IE-EmilyNeural', 'Neural', 'en-IE'),
            AzureVoice(Language.en_IE, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (en-IE, Sean)', 'Sean','Sean', 'en-IE-Sean', 'Standard', 'en-IE'),
            AzureVoice(Language.en_GB, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (en-GB, MiaNeural)', 'Mia','Mia', 'en-GB-MiaNeural', 'Neural', 'en-GB'),
            AzureVoice(Language.en_GB, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (en-GB, LibbyNeural)', 'Libby','Libby', 'en-GB-LibbyNeural', 'Neural', 'en-GB'),
            AzureVoice(Language.en_GB, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (en-GB, RyanNeural)', 'Ryan','Ryan', 'en-GB-RyanNeural', 'Neural', 'en-GB'),
            AzureVoice(Language.en_GB, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (en-GB, George)', 'George','George', 'en-GB-George', 'Standard', 'en-GB'),
            AzureVoice(Language.en_GB, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (en-GB, HazelRUS)', 'Hazel','Hazel', 'en-GB-HazelRUS', 'Standard', 'en-GB'),
            AzureVoice(Language.en_GB, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (en-GB, Susan)', 'Susan','Susan', 'en-GB-Susan', 'Standard', 'en-GB'),
            AzureVoice(Language.en_US, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (en-US, JennyNeural)', 'Jenny','Jenny', 'en-US-JennyNeural', 'Neural', 'en-US'),
            AzureVoice(Language.en_US, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (en-US, GuyNeural)', 'Guy','Guy', 'en-US-GuyNeural', 'Neural', 'en-US'),
            AzureVoice(Language.en_US, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (en-US, AriaNeural)', 'Aria','Aria', 'en-US-AriaNeural', 'Neural', 'en-US'),
            AzureVoice(Language.en_US, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (en-US, AriaRUS)', 'Aria','Aria', 'en-US-AriaRUS', 'Standard', 'en-US'),
            AzureVoice(Language.en_US, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (en-US, BenjaminRUS)', 'Benjamin','Benjamin', 'en-US-BenjaminRUS', 'Standard', 'en-US'),
            AzureVoice(Language.en_US, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (en-US, GuyRUS)', 'Guy','Guy', 'en-US-GuyRUS', 'Standard', 'en-US'),
            AzureVoice(Language.en_US, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (en-US, ZiraRUS)', 'Zira','Zira', 'en-US-ZiraRUS', 'Standard', 'en-US'),
            AzureVoice(Language.et_EE, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (et-EE, AnuNeural)', 'Anu','Anu', 'et-EE-AnuNeural', 'Neural', 'et-EE'),
            AzureVoice(Language.et_EE, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (et-EE, KertNeural)', 'Kert','Kert', 'et-EE-KertNeural', 'Neural', 'et-EE'),
            AzureVoice(Language.fi_FI, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (fi-FI, SelmaNeural)', 'Selma','Selma', 'fi-FI-SelmaNeural', 'Neural', 'fi-FI'),
            AzureVoice(Language.fi_FI, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (fi-FI, HarriNeural)', 'Harri','Harri', 'fi-FI-HarriNeural', 'Neural', 'fi-FI'),
            AzureVoice(Language.fi_FI, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (fi-FI, NooraNeural)', 'Noora','Noora', 'fi-FI-NooraNeural', 'Neural', 'fi-FI'),
            AzureVoice(Language.fi_FI, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (fi-FI, HeidiRUS)', 'Heidi','Heidi', 'fi-FI-HeidiRUS', 'Standard', 'fi-FI'),
            AzureVoice(Language.fr_CA, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (fr-CA, SylvieNeural)', 'Sylvie','Sylvie', 'fr-CA-SylvieNeural', 'Neural', 'fr-CA'),
            AzureVoice(Language.fr_CA, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (fr-CA, JeanNeural)', 'Jean','Jean', 'fr-CA-JeanNeural', 'Neural', 'fr-CA'),
            AzureVoice(Language.fr_CA, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (fr-CA, Caroline)', 'Caroline','Caroline', 'fr-CA-Caroline', 'Standard', 'fr-CA'),
            AzureVoice(Language.fr_CA, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (fr-CA, HarmonieRUS)', 'Harmonie','Harmonie', 'fr-CA-HarmonieRUS', 'Standard', 'fr-CA'),
            AzureVoice(Language.fr_FR, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (fr-FR, DeniseNeural)', 'Denise','Denise', 'fr-FR-DeniseNeural', 'Neural', 'fr-FR'),
            AzureVoice(Language.fr_FR, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (fr-FR, HenriNeural)', 'Henri','Henri', 'fr-FR-HenriNeural', 'Neural', 'fr-FR'),
            AzureVoice(Language.fr_FR, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (fr-FR, HortenseRUS)', 'Hortense','Hortense', 'fr-FR-HortenseRUS', 'Standard', 'fr-FR'),
            AzureVoice(Language.fr_FR, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (fr-FR, Julie)', 'Julie','Julie', 'fr-FR-Julie', 'Standard', 'fr-FR'),
            AzureVoice(Language.fr_FR, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (fr-FR, Paul)', 'Paul','Paul', 'fr-FR-Paul', 'Standard', 'fr-FR'),
            AzureVoice(Language.fr_CH, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (fr-CH, ArianeNeural)', 'Ariane','Ariane', 'fr-CH-ArianeNeural', 'Neural', 'fr-CH'),
            AzureVoice(Language.fr_CH, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (fr-CH, FabriceNeural)', 'Fabrice','Fabrice', 'fr-CH-FabriceNeural', 'Neural', 'fr-CH'),
            AzureVoice(Language.fr_CH, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (fr-CH, Guillaume)', 'Guillaume','Guillaume', 'fr-CH-Guillaume', 'Standard', 'fr-CH'),
            AzureVoice(Language.de_AT, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (de-AT, IngridNeural)', 'Ingrid','Ingrid', 'de-AT-IngridNeural', 'Neural', 'de-AT'),
            AzureVoice(Language.de_AT, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (de-AT, JonasNeural)', 'Jonas','Jonas', 'de-AT-JonasNeural', 'Neural', 'de-AT'),
            AzureVoice(Language.de_AT, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (de-AT, Michael)', 'Michael','Michael', 'de-AT-Michael', 'Standard', 'de-AT'),
            AzureVoice(Language.de_DE, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (de-DE, KatjaNeural)', 'Katja','Katja', 'de-DE-KatjaNeural', 'Neural', 'de-DE'),
            AzureVoice(Language.de_DE, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (de-DE, ConradNeural)', 'Conrad','Conrad', 'de-DE-ConradNeural', 'Neural', 'de-DE'),
            AzureVoice(Language.de_DE, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (de-DE, HeddaRUS)', 'Hedda','Hedda', 'de-DE-HeddaRUS', 'Standard', 'de-DE'),
            AzureVoice(Language.de_DE, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (de-DE, Stefan)', 'Stefan','Stefan', 'de-DE-Stefan', 'Standard', 'de-DE'),
            AzureVoice(Language.de_CH, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (de-CH, JanNeural)', 'Jan','Jan', 'de-CH-JanNeural', 'Neural', 'de-CH'),
            AzureVoice(Language.de_CH, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (de-CH, LeniNeural)', 'Leni','Leni', 'de-CH-LeniNeural', 'Neural', 'de-CH'),
            AzureVoice(Language.de_CH, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (de-CH, Karsten)', 'Karsten','Karsten', 'de-CH-Karsten', 'Standard', 'de-CH'),
            AzureVoice(Language.el_GR, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (el-GR, AthinaNeural)', 'Athina','Αθηνά', 'el-GR-AthinaNeural', 'Neural', 'el-GR'),
            AzureVoice(Language.el_GR, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (el-GR, NestorasNeural)', 'Nestoras','Νέστορας', 'el-GR-NestorasNeural', 'Neural', 'el-GR'),
            AzureVoice(Language.el_GR, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (el-GR, Stefanos)', 'Stefanos','Στέφανος', 'el-GR-Stefanos', 'Standard', 'el-GR'),
            AzureVoice(Language.he_IL, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (he-IL, AvriNeural)', 'Avri','אברי', 'he-IL-AvriNeural', 'Neural', 'he-IL'),
            AzureVoice(Language.he_IL, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (he-IL, HilaNeural)', 'Hila','הילה', 'he-IL-HilaNeural', 'Neural', 'he-IL'),
            AzureVoice(Language.he_IL, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (he-IL, Asaf)', 'Asaf','אסף', 'he-IL-Asaf', 'Standard', 'he-IL'),
            AzureVoice(Language.hi_IN, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (hi-IN, MadhurNeural)', 'Madhur','मधुर', 'hi-IN-MadhurNeural', 'Neural', 'hi-IN'),
            AzureVoice(Language.hi_IN, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (hi-IN, SwaraNeural)', 'Swara','स्वरा', 'hi-IN-SwaraNeural', 'Neural', 'hi-IN'),
            AzureVoice(Language.hi_IN, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (hi-IN, Hemant)', 'Hemant','हेमन्त', 'hi-IN-Hemant', 'Standard', 'hi-IN'),
            AzureVoice(Language.hi_IN, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (hi-IN, Kalpana)', 'Kalpana','कल्पना', 'hi-IN-Kalpana', 'Standard', 'hi-IN'),
            AzureVoice(Language.hu_HU, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (hu-HU, NoemiNeural)', 'Noemi','Noémi', 'hu-HU-NoemiNeural', 'Neural', 'hu-HU'),
            AzureVoice(Language.hu_HU, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (hu-HU, TamasNeural)', 'Tamas','Tamás', 'hu-HU-TamasNeural', 'Neural', 'hu-HU'),
            AzureVoice(Language.hu_HU, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (hu-HU, Szabolcs)', 'Szabolcs','Szabolcs', 'hu-HU-Szabolcs', 'Standard', 'hu-HU'),
            AzureVoice(Language.id_ID, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (id-ID, ArdiNeural)', 'Ardi','Ardi', 'id-ID-ArdiNeural', 'Neural', 'id-ID'),
            AzureVoice(Language.id_ID, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (id-ID, GadisNeural)', 'Gadis','Gadis', 'id-ID-GadisNeural', 'Neural', 'id-ID'),
            AzureVoice(Language.id_ID, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (id-ID, Andika)', 'Andika','Andika', 'id-ID-Andika', 'Standard', 'id-ID'),
            AzureVoice(Language.ga_IE, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (ga-IE, ColmNeural)', 'Colm','Colm', 'ga-IE-ColmNeural', 'Neural', 'ga-IE'),
            AzureVoice(Language.ga_IE, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ga-IE, OrlaNeural)', 'Orla','Orla', 'ga-IE-OrlaNeural', 'Neural', 'ga-IE'),
            AzureVoice(Language.it_IT, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (it-IT, IsabellaNeural)', 'Isabella','Isabella', 'it-IT-IsabellaNeural', 'Neural', 'it-IT'),
            AzureVoice(Language.it_IT, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (it-IT, DiegoNeural)', 'Diego','Diego', 'it-IT-DiegoNeural', 'Neural', 'it-IT'),
            AzureVoice(Language.it_IT, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (it-IT, ElsaNeural)', 'Elsa','Elsa', 'it-IT-ElsaNeural', 'Neural', 'it-IT'),
            AzureVoice(Language.it_IT, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (it-IT, Cosimo)', 'Cosimo','Cosimo', 'it-IT-Cosimo', 'Standard', 'it-IT'),
            AzureVoice(Language.it_IT, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (it-IT, LuciaRUS)', 'Lucia','Lucia', 'it-IT-LuciaRUS', 'Standard', 'it-IT'),
            AzureVoice(Language.ja_JP, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ja-JP, NanamiNeural)', 'Nanami','七海', 'ja-JP-NanamiNeural', 'Neural', 'ja-JP'),
            AzureVoice(Language.ja_JP, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (ja-JP, KeitaNeural)', 'Keita','圭太', 'ja-JP-KeitaNeural', 'Neural', 'ja-JP'),
            AzureVoice(Language.ja_JP, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ja-JP, Ayumi)', 'Ayumi','歩美', 'ja-JP-Ayumi', 'Standard', 'ja-JP'),
            AzureVoice(Language.ja_JP, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ja-JP, HarukaRUS)', 'Haruka','春香', 'ja-JP-HarukaRUS', 'Standard', 'ja-JP'),
            AzureVoice(Language.ja_JP, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (ja-JP, Ichiro)', 'Ichiro','一郎', 'ja-JP-Ichiro', 'Standard', 'ja-JP'),
            AzureVoice(Language.ko_KR, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ko-KR, SunHiNeural)', 'Sun-Hi','선히', 'ko-KR-SunHiNeural', 'Neural', 'ko-KR'),
            AzureVoice(Language.ko_KR, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (ko-KR, InJoonNeural)', 'InJoon','인준', 'ko-KR-InJoonNeural', 'Neural', 'ko-KR'),
            AzureVoice(Language.ko_KR, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ko-KR, HeamiRUS)', 'Heami','해 미', 'ko-KR-HeamiRUS', 'Standard', 'ko-KR'),
            AzureVoice(Language.lv_LV, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (lv-LV, EveritaNeural)', 'Everita','Everita', 'lv-LV-EveritaNeural', 'Neural', 'lv-LV'),
            AzureVoice(Language.lv_LV, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (lv-LV, NilsNeural)', 'Nils','Nils', 'lv-LV-NilsNeural', 'Neural', 'lv-LV'),
            AzureVoice(Language.lt_LT, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (lt-LT, LeonasNeural)', 'Leonas','Leonas', 'lt-LT-LeonasNeural', 'Neural', 'lt-LT'),
            AzureVoice(Language.lt_LT, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (lt-LT, OnaNeural)', 'Ona','Ona', 'lt-LT-OnaNeural', 'Neural', 'lt-LT'),
            AzureVoice(Language.ms_MY, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (ms-MY, OsmanNeural)', 'Osman','Osman', 'ms-MY-OsmanNeural', 'Neural', 'ms-MY'),
            AzureVoice(Language.ms_MY, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ms-MY, YasminNeural)', 'Yasmin','Yasmin', 'ms-MY-YasminNeural', 'Neural', 'ms-MY'),
            AzureVoice(Language.ms_MY, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (ms-MY, Rizwan)', 'Rizwan','Rizwan', 'ms-MY-Rizwan', 'Standard', 'ms-MY'),
            AzureVoice(Language.mt_MT, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (mt-MT, GraceNeural)', 'Grace','Grace', 'mt-MT-GraceNeural', 'Neural', 'mt-MT'),
            AzureVoice(Language.mt_MT, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (mt-MT, JosephNeural)', 'Joseph','Joseph', 'mt-MT-JosephNeural', 'Neural', 'mt-MT'),
            AzureVoice(Language.nb_NO, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (nb-NO, PernilleNeural)', 'Pernille','Pernille', 'nb-NO-PernilleNeural', 'Neural', 'nb-NO'),
            AzureVoice(Language.nb_NO, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (nb-NO, FinnNeural)', 'Finn','Finn', 'nb-NO-FinnNeural', 'Neural', 'nb-NO'),
            AzureVoice(Language.nb_NO, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (nb-NO, IselinNeural)', 'Iselin','Iselin', 'nb-NO-IselinNeural', 'Neural', 'nb-NO'),
            AzureVoice(Language.nb_NO, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (nb-NO, HuldaRUS)', 'Hulda','Hulda', 'nb-NO-HuldaRUS', 'Standard', 'nb-NO'),
            AzureVoice(Language.pl_PL, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (pl-PL, AgnieszkaNeural)', 'Agnieszka','Agnieszka', 'pl-PL-AgnieszkaNeural', 'Neural', 'pl-PL'),
            AzureVoice(Language.pl_PL, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (pl-PL, MarekNeural)', 'Marek','Marek', 'pl-PL-MarekNeural', 'Neural', 'pl-PL'),
            AzureVoice(Language.pl_PL, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (pl-PL, ZofiaNeural)', 'Zofia','Zofia', 'pl-PL-ZofiaNeural', 'Neural', 'pl-PL'),
            AzureVoice(Language.pl_PL, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (pl-PL, PaulinaRUS)', 'Paulina','Paulina', 'pl-PL-PaulinaRUS', 'Standard', 'pl-PL'),
            AzureVoice(Language.pt_BR, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (pt-BR, FranciscaNeural)', 'Francisca','Francisca', 'pt-BR-FranciscaNeural', 'Neural', 'pt-BR'),
            AzureVoice(Language.pt_BR, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (pt-BR, AntonioNeural)', 'Antonio','Antônio', 'pt-BR-AntonioNeural', 'Neural', 'pt-BR'),
            AzureVoice(Language.pt_BR, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (pt-BR, Daniel)', 'Daniel','Daniel', 'pt-BR-Daniel', 'Standard', 'pt-BR'),
            AzureVoice(Language.pt_BR, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (pt-BR, HeloisaRUS)', 'Heloisa','Heloisa', 'pt-BR-HeloisaRUS', 'Standard', 'pt-BR'),
            AzureVoice(Language.pt_PT, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (pt-PT, DuarteNeural)', 'Duarte','Duarte', 'pt-PT-DuarteNeural', 'Neural', 'pt-PT'),
            AzureVoice(Language.pt_PT, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (pt-PT, FernandaNeural)', 'Fernanda','Fernanda', 'pt-PT-FernandaNeural', 'Neural', 'pt-PT'),
            AzureVoice(Language.pt_PT, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (pt-PT, RaquelNeural)', 'Raquel','Raquel', 'pt-PT-RaquelNeural', 'Neural', 'pt-PT'),
            AzureVoice(Language.pt_PT, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (pt-PT, HeliaRUS)', 'Helia','Hélia', 'pt-PT-HeliaRUS', 'Standard', 'pt-PT'),
            AzureVoice(Language.ro_RO, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ro-RO, AlinaNeural)', 'Alina','Alina', 'ro-RO-AlinaNeural', 'Neural', 'ro-RO'),
            AzureVoice(Language.ro_RO, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (ro-RO, EmilNeural)', 'Emil','Emil', 'ro-RO-EmilNeural', 'Neural', 'ro-RO'),
            AzureVoice(Language.ro_RO, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (ro-RO, Andrei)', 'Andrei','Andrei', 'ro-RO-Andrei', 'Standard', 'ro-RO'),
            AzureVoice(Language.ru_RU, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ru-RU, SvetlanaNeural)', 'Svetlana','Светлана', 'ru-RU-SvetlanaNeural', 'Neural', 'ru-RU'),
            AzureVoice(Language.ru_RU, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ru-RU, DariyaNeural)', 'Dariya','Дария', 'ru-RU-DariyaNeural', 'Neural', 'ru-RU'),
            AzureVoice(Language.ru_RU, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (ru-RU, DmitryNeural)', 'Dmitry','Дмитрий', 'ru-RU-DmitryNeural', 'Neural', 'ru-RU'),
            AzureVoice(Language.ru_RU, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ru-RU, EkaterinaRUS)', 'Ekaterina','Екатерина', 'ru-RU-EkaterinaRUS', 'Standard', 'ru-RU'),
            AzureVoice(Language.ru_RU, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ru-RU, Irina)', 'Irina','Ирина', 'ru-RU-Irina', 'Standard', 'ru-RU'),
            AzureVoice(Language.ru_RU, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (ru-RU, Pavel)', 'Pavel','Павел', 'ru-RU-Pavel', 'Standard', 'ru-RU'),
            AzureVoice(Language.sk_SK, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (sk-SK, LukasNeural)', 'Lukas','Lukáš', 'sk-SK-LukasNeural', 'Neural', 'sk-SK'),
            AzureVoice(Language.sk_SK, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (sk-SK, ViktoriaNeural)', 'Viktoria','Viktória', 'sk-SK-ViktoriaNeural', 'Neural', 'sk-SK'),
            AzureVoice(Language.sk_SK, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (sk-SK, Filip)', 'Filip','Filip', 'sk-SK-Filip', 'Standard', 'sk-SK'),
            AzureVoice(Language.sl_SI, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (sl-SI, PetraNeural)', 'Petra','Petra', 'sl-SI-PetraNeural', 'Neural', 'sl-SI'),
            AzureVoice(Language.sl_SI, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (sl-SI, RokNeural)', 'Rok','Rok', 'sl-SI-RokNeural', 'Neural', 'sl-SI'),
            AzureVoice(Language.sl_SI, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (sl-SI, Lado)', 'Lado','Lado', 'sl-SI-Lado', 'Standard', 'sl-SI'),
            AzureVoice(Language.es_MX, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (es-MX, DaliaNeural)', 'Dalia','Dalia', 'es-MX-DaliaNeural', 'Neural', 'es-MX'),
            AzureVoice(Language.es_MX, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (es-MX, JorgeNeural)', 'Jorge','Jorge', 'es-MX-JorgeNeural', 'Neural', 'es-MX'),
            AzureVoice(Language.es_MX, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (es-MX, HildaRUS)', 'Hilda','Hilda', 'es-MX-HildaRUS', 'Standard', 'es-MX'),
            AzureVoice(Language.es_MX, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (es-MX, Raul)', 'Raul','Raúl', 'es-MX-Raul', 'Standard', 'es-MX'),
            AzureVoice(Language.es_ES, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (es-ES, AlvaroNeural)', 'Alvaro','Álvaro', 'es-ES-AlvaroNeural', 'Neural', 'es-ES'),
            AzureVoice(Language.es_ES, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (es-ES, ElviraNeural)', 'Elvira','Elvira', 'es-ES-ElviraNeural', 'Neural', 'es-ES'),
            AzureVoice(Language.es_ES, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (es-ES, HelenaRUS)', 'Helena','Helena', 'es-ES-HelenaRUS', 'Standard', 'es-ES'),
            AzureVoice(Language.es_ES, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (es-ES, Laura)', 'Laura','Laura', 'es-ES-Laura', 'Standard', 'es-ES'),
            AzureVoice(Language.es_ES, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (es-ES, Pablo)', 'Pablo','Pablo', 'es-ES-Pablo', 'Standard', 'es-ES'),
            AzureVoice(Language.sv_SE, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (sv-SE, SofieNeural)', 'Sofie','Sofie', 'sv-SE-SofieNeural', 'Neural', 'sv-SE'),
            AzureVoice(Language.sv_SE, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (sv-SE, HilleviNeural)', 'Hillevi','Hillevi', 'sv-SE-HilleviNeural', 'Neural', 'sv-SE'),
            AzureVoice(Language.sv_SE, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (sv-SE, MattiasNeural)', 'Mattias','Mattias', 'sv-SE-MattiasNeural', 'Neural', 'sv-SE'),
            AzureVoice(Language.sv_SE, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (sv-SE, HedvigRUS)', 'Hedvig','Hedvig', 'sv-SE-HedvigRUS', 'Standard', 'sv-SE'),
            AzureVoice(Language.ta_IN, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (ta-IN, PallaviNeural)', 'Pallavi','பல்லவி', 'ta-IN-PallaviNeural', 'Neural', 'ta-IN'),
            AzureVoice(Language.ta_IN, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (ta-IN, ValluvarNeural)', 'Valluvar','வள்ளுவர்', 'ta-IN-ValluvarNeural', 'Neural', 'ta-IN'),
            AzureVoice(Language.ta_IN, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (ta-IN, Valluvar)', 'Valluvar','வள்ளுவர்', 'ta-IN-Valluvar', 'Standard', 'ta-IN'),
            AzureVoice(Language.te_IN, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (te-IN, MohanNeural)', 'Mohan','మోహన్', 'te-IN-MohanNeural', 'Neural', 'te-IN'),
            AzureVoice(Language.te_IN, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (te-IN, ShrutiNeural)', 'Shruti','శ్రుతి', 'te-IN-ShrutiNeural', 'Neural', 'te-IN'),
            AzureVoice(Language.te_IN, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (te-IN, Chitra)', 'Chitra','చిత్ర', 'te-IN-Chitra', 'Standard', 'te-IN'),
            AzureVoice(Language.th_TH, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (th-TH, PremwadeeNeural)', 'Premwadee','เปรมวดี', 'th-TH-PremwadeeNeural', 'Neural', 'th-TH'),
            AzureVoice(Language.th_TH, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (th-TH, AcharaNeural)', 'Achara','อัจฉรา', 'th-TH-AcharaNeural', 'Neural', 'th-TH'),
            AzureVoice(Language.th_TH, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (th-TH, NiwatNeural)', 'Niwat','นิวัฒน์', 'th-TH-NiwatNeural', 'Neural', 'th-TH'),
            AzureVoice(Language.th_TH, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (th-TH, Pattara)', 'Pattara','ภัทรา', 'th-TH-Pattara', 'Standard', 'th-TH'),
            AzureVoice(Language.tr_TR, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (tr-TR, AhmetNeural)', 'Ahmet','Ahmet', 'tr-TR-AhmetNeural', 'Neural', 'tr-TR'),
            AzureVoice(Language.tr_TR, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (tr-TR, EmelNeural)', 'Emel','Emel', 'tr-TR-EmelNeural', 'Neural', 'tr-TR'),
            AzureVoice(Language.tr_TR, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (tr-TR, SedaRUS)', 'Seda','Seda', 'tr-TR-SedaRUS', 'Standard', 'tr-TR'),
            AzureVoice(Language.vi_VN, Gender.Female, 'Microsoft Server Speech Text to Speech Voice (vi-VN, HoaiMyNeural)', 'HoaiMy','Hoài My', 'vi-VN-HoaiMyNeural', 'Neural', 'vi-VN'),
            AzureVoice(Language.vi_VN, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (vi-VN, NamMinhNeural)', 'NamMinh','Nam Minh', 'vi-VN-NamMinhNeural', 'Neural', 'vi-VN'),
            AzureVoice(Language.vi_VN, Gender.Male, 'Microsoft Server Speech Text to Speech Voice (vi-VN, An)', 'An','An', 'vi-VN-An', 'Standard', 'vi-VN')
        ]


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

        return [
            dict(key='voice',
                 label="Voice",
                 values=self.get_voice_list(),
                 transform=lambda value: value),
            dict(key='region',
                 label='Region',
                 values=REGIONS,
                 default='eastus',
                 transform=lambda value: value),
            dict(key='speed',
                label='Speed',
                values=SPEEDS,
                default='default',
                transform=lambda value: value),
            dict(key='pitch',
                label='Pitch',
                values=PITCH,
                default='default',
                transform=lambda value: value),                
            
        ]

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

        region = options['region']
        subscription_key = options['key']
        if self.token_refresh_required():
            self.get_token(subscription_key, region)

        voice_key = options['voice']
        voice = self.get_voice_for_key(voice_key)
        voice_name = voice.get_key()
        language = voice.get_language_code()

        rate = options['speed']
        pitch = options['pitch']

        base_url = f'https://{region}.tts.speech.microsoft.com/'
        url_path = 'cognitiveservices/v1'
        constructed_url = base_url + url_path
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-24khz-96kbitrate-mono-mp3',
            'User-Agent': 'anki-awesome-tts'
        }

        xml_body = ElementTree.Element('speak', version='1.0')

        xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', language)
        voice = ElementTree.SubElement(xml_body, 'voice')
        voice.set('{http://www.w3.org/XML/1998/namespace}lang', language)
        voice.set(
            'name', voice_name)

        prosody = ElementTree.SubElement(voice, 'prosody')
        prosody.set('rate', rate)
        prosody.set('pitch', pitch)

        prosody.text = text
        body = ElementTree.tostring(xml_body)

        self._logger.info(f"xml request: {body}")

        response = requests.post(constructed_url, headers=headers, data=body)
        if response.status_code == 200:
            with open(path, 'wb') as audio:
                audio.write(response.content)
        else:
            error_message = f"Status code: {response.status_code} reason: {response.reason} voice: [{voice_name}] language: [{language} " + \
            f"subscription key: [{subscription_key}]] access token timestamp: [{self.access_token_timestamp}] access token: [{self.access_token}]"
            raise ValueError(error_message)



