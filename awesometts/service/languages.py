from enum import Enum
from abc import ABC

class Gender(Enum):
    Male = 1
    Female = 2
    Unknown = 3

class Language(Enum):
    en_US = ("English (US)")

    def __init__(self, lang_name):
        self.lang_name = lang_name


class Voice(ABC):
        
    @abstractmethod
    def get_gender(self) -> Gender:
        pass

    @abstractmethod
    def get_language(self) -> Language:
        pass

    @abstractmethod
    def get_key(self) -> str:
        pass