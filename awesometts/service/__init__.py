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
Service classes for AwesomeTTS
"""

from .common import Trait

from .amazon import Amazon
from .azure import Azure
from .baidu import Baidu
from .cambridge import Cambridge
from .cereproc import CereProc
from .collins import Collins
from .duden import Duden
from .ekho import Ekho
from .espeak import ESpeak
from .festival import Festival
from .fptai import FptAi
from .google import Google
from .googletts import GoogleTTS
from .ispeech import ISpeech
from .naver import Naver
from .naverclova import NaverClova
from .naverclovapremium import NaverClovaPremium
from .oddcast import Oddcast
from .oxford import Oxford
from .pico2wave import Pico2Wave
from .rhvoice import RHVoice
from .sapi5com import SAPI5COM
from .sapi5js import SAPI5JS
from .say import Say
from .spanishdict import SpanishDict
from .yandex import Yandex
from .youdao import Youdao
from .forvo import Forvo
from .vocalware import VocalWare
from .watson import Watson

__all__ = [
    # common
    'Trait',

    # services
    'Amazon',
    'Azure',
    'Baidu',
    'CereProc',
    'Collins',
    'Duden',
    'Ekho',
    'ESpeak',
    'Festival',
    'FPT.AI',
    'Google',
    'GoogleTTS',
    'ISpeech',
    'Naver',
    'NaverClova',
    'Oddcast',
    'Oxford',
    'Pico2Wave',
    'RHVoice',
    'SAPI5COM',
    'SAPI5JS',
    'Say',
    'SpanishDict',
    'Yandex',
    'Youdao',
    'Forvo',
    'VocalWare',
    'Watson'
]
