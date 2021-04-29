from enum import Enum
import abc
#from abc import ABC
#from abc import abstractmethod

class Gender(Enum):
    Male = 1
    Female = 2
    Unknown = 3



class Language(Enum):
    ar_AR = ("Arabic")
    ar_EG = ("Arabic (Egypt)")
    ar_SA = ("Arabic (Saudi Arabia)")
    bg_BG = ("Bulgarian")
    bn_IN = ("Bengali (India)")
    ca_ES = ("Catalan")
    cs_CZ = ("Czech")
    cy_GB = ("Welsh")
    da_DK = ("Danish")
    de_AT = ("German (Austria)")
    de_CH = ("German (Switzerland)")
    de_DE = ("German (Germany)")
    el_GR = ("Greek")
    en_AU = ("English (Australia)")
    en_CA = ("English (Canada)")
    en_GB = ("English (UK)")
    en_GB_WLS = ("English (Welsh)")
    en_IE = ("English (Ireland)")
    en_IN = ("English (India)")
    en_US = ("English (US)")
    en_PH = ("English (Philippines)")
    es_ES = ("Spanish (Spain)")
    es_MX = ("Spanish (Mexico)")
    es_LA = ("Spanish (Latin America)")
    es_US = ("Spanish (North America)")
    et_EE = ("Estonian (Estonia)")
    fi_FI = ("Finnish")
    fil_PH = ("Filipino (Philippines)")
    fr_CA = ("French (Canada)")
    fr_BE = ("French (Belgium)")
    fr_CH = ("French (Switzerland)")
    fr_FR = ("French (France)")
    ga_IE = ("Irish (Ireland)")
    gu_IN = ("Gujarati (India)")
    he_IL = ("Hebrew (Israel)")
    hi_IN = ("Hindi (India)")
    hr_HR = ("Croatian")
    hu_HU = ("Hungarian")
    id_ID = ("Indonesian")
    is_IS = ("Icelandic")
    it_IT = ("Italian")
    ja_JP = ("Japanese")
    kn_IN = ("Kannada (India)")
    lt_LT = ("Lithuanian (Lithuania)")
    lv_LV = ("Latvian (Latvia)"),
    ko_KR = ("Korean")
    ml_IN = ("Malayalam (India)")
    ms_MY = ("Malay")
    mt_MT = ("Maltese (Malta)"),
    nb_NO = ("Norwegian")
    nl_NL = ("Dutch")
    nl_BE = ("Dutch (Belgium)")
    pl_PL = ("Polish")
    pt_BR = ("Portuguese (Brazil)")
    pt_PT = ("Portuguese (Portugal)")
    ro_RO = ("Romanian")
    ru_RU = ("Russian")
    sk_SK = ("Slovak")
    sl_SI = ("Slovenian")
    sv_SE = ("Swedish")
    ta_IN = ("Tamil (India)")
    te_IN = ("Telugu (India)")
    th_TH = ("Thai")
    tr_TR = ("Turkish (Turkey)")
    uk_UA = ("Ukrainian (Ukraine)")
    ur_PK = ("Urdu (Pakistan)")
    vi_VN = ("Vietnamese")
    zh_CN = ("Chinese (Mandarin, simplified)")
    zh_HK = ("Chinese (Cantonese, Traditional)")
    zh_TW = ("Chinese (Taiwanese Mandarin)")

    def __init__(self, lang_name):
        self.lang_name = lang_name


class Voice(abc.ABC):
        
    @abc.abstractmethod
    def get_key(self) -> str:
        pass

    @abc.abstractmethod
    def get_description(self) -> str:
        pass

class StandardVoice(Voice):
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