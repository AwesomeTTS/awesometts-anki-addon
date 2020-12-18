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
    ca_ES = ("Catalan")
    cs_CZ = ("Czech")
    da_DK = ("Danish")
    de_AT = ("German (Austria)")
    de_CH = ("German (Switzerland)")
    de_DE = ("German (Germany)")
    el_GR = ("Greek")
    en_AU = ("English (Australia)")
    en_CA = ("English (Canada)")
    en_GB = ("English (UK)")
    en_IE = ("English (Ireland)")
    en_IN = ("English (India)")
    en_US = ("English (US)")
    es_ES = ("Spanish (Spain)")
    es_MX = ("Spanish (Mexico)")
    es_LA = ("Spanish (Latin America)")
    es_US = ("Spanish (North America)")
    et_EE = ("Estonian (Estonia)")
    fi_FI = ("Finnish")
    fr_CA = ("French (Canada)")
    fr_CH = ("French (Switzerland)")
    fr_FR = ("French (France)")
    ga_IE = ("Irish (Ireland)")
    he_IL = ("Hebrew (Israel)")
    hi_IN = ("Hindi (India)")
    hr_HR = ("Croatian")
    hu_HU = ("Hungarian")
    id_ID = ("Indonesian")
    it_IT = ("Italian")
    ja_JP = ("Japanese")
    lt_LT = ("Lithuanian (Lithuania)")
    lv_LV = ("Latvian (Latvia)"),
    ko_KR = ("Korean")
    ms_MY = ("Malay")
    mt_MT = ("Maltese (Malta)"),
    nb_NO = ("Norwegian")
    nl_NL = ("Dutch")
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
    vi_VN = ("Vietnamese")
    zh_CN = ("Chinese (Mandarin, simplified)")
    zh_HK = ("Chinese (Cantonese, Traditional)")
    zh_TW = ("Chinese (Taiwanese Mandarin)")

    def __init__(self, lang_name):
        self.lang_name = lang_name


class Voice(abc.ABC):
        
    @abc.abstractmethod
    def get_gender(self) -> Gender:
        pass

    @abc.abstractmethod
    def get_language(self) -> Language:
        pass

    @abc.abstractmethod
    def get_key(self) -> str:
        pass

    @abc.abstractmethod
    def get_description(self) -> str:
        pass