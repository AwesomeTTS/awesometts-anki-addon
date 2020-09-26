from enum import Enum
import abc
#from abc import ABC
#from abc import abstractmethod

class Gender(Enum):
    Male = 1
    Female = 2
    Unknown = 3

class Language(Enum):
    en_US = ("English (US)")
    en_GB = ("English (UK)")

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