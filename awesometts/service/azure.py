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
import requests
from xml.etree import ElementTree
from .base import Service

__all__ = ['Azure']

# generated using tools/service_azure_voicelist.py
VOICE_LIST = [
{'Name': 'Microsoft Server Speech Text to Speech Voice (ar-EG, Hoda)', 'ShortName': 'ar-EG-Hoda', 'Gender': 'Female', 'Locale': 'ar-EG', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Arabic (Egypt)', 'ShortNameFriendly': 'Hoda'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ar-SA, Naayf)', 'ShortName': 'ar-SA-Naayf', 'Gender': 'Male', 'Locale': 'ar-SA', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Arabic (Saudi Arabia)', 'ShortNameFriendly': 'Naayf'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (bg-BG, Ivan)', 'ShortName': 'bg-BG-Ivan', 'Gender': 'Male', 'Locale': 'bg-BG', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Bulgarian', 'ShortNameFriendly': 'Ivan'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ca-ES, HerenaRUS)', 'ShortName': 'ca-ES-HerenaRUS', 'Gender': 'Female', 'Locale': 'ca-ES', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Catalan', 'ShortNameFriendly': 'HerenaRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (cs-CZ, Jakub)', 'ShortName': 'cs-CZ-Jakub', 'Gender': 'Male', 'Locale': 'cs-CZ', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Czech', 'ShortNameFriendly': 'Jakub'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (da-DK, HelleRUS)', 'ShortName': 'da-DK-HelleRUS', 'Gender': 'Female', 'Locale': 'da-DK', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Danish', 'ShortNameFriendly': 'HelleRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (de-AT, Michael)', 'ShortName': 'de-AT-Michael', 'Gender': 'Male', 'Locale': 'de-AT', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'German (Austria)', 'ShortNameFriendly': 'Michael'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (de-CH, Karsten)', 'ShortName': 'de-CH-Karsten', 'Gender': 'Male', 'Locale': 'de-CH', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'German (Switzerland)', 'ShortNameFriendly': 'Karsten'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (de-DE, Hedda)', 'ShortName': 'de-DE-Hedda', 'Gender': 'Female', 'Locale': 'de-DE', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'German (Germany)', 'ShortNameFriendly': 'Hedda'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (de-DE, HeddaRUS)', 'ShortName': 'de-DE-HeddaRUS', 'Gender': 'Female', 'Locale': 'de-DE', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'German (Germany)', 'ShortNameFriendly': 'HeddaRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (de-DE, KatjaNeural)', 'ShortName': 'de-DE-KatjaNeural', 'Gender': 'Female', 'Locale': 'de-DE', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'German (Germany)', 'ShortNameFriendly': 'KatjaNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (de-DE, Stefan, Apollo)', 'ShortName': 'de-DE-Stefan-Apollo', 'Gender': 'Male', 'Locale': 'de-DE', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'German (Germany)', 'ShortNameFriendly': 'Stefan,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (el-GR, Stefanos)', 'ShortName': 'el-GR-Stefanos', 'Gender': 'Male', 'Locale': 'el-GR', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Greek', 'ShortNameFriendly': 'Stefanos'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-AU, Catherine)', 'ShortName': 'en-AU-Catherine', 'Gender': 'Female', 'Locale': 'en-AU', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (Australia)', 'ShortNameFriendly': 'Catherine'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-AU, HayleyRUS)', 'ShortName': 'en-AU-HayleyRUS', 'Gender': 'Female', 'Locale': 'en-AU', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (Australia)', 'ShortNameFriendly': 'HayleyRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-AU, NatashaNeural)', 'ShortName': 'en-AU-NatashaNeural', 'Gender': 'Female', 'Locale': 'en-AU', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'English (Australia)', 'ShortNameFriendly': 'NatashaNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-CA, ClaraNeural)', 'ShortName': 'en-CA-ClaraNeural', 'Gender': 'Female', 'Locale': 'en-CA', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'English (Canada)', 'ShortNameFriendly': 'ClaraNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-CA, HeatherRUS)', 'ShortName': 'en-CA-HeatherRUS', 'Gender': 'Female', 'Locale': 'en-CA', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (Canada)', 'ShortNameFriendly': 'HeatherRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-CA, Linda)', 'ShortName': 'en-CA-Linda', 'Gender': 'Female', 'Locale': 'en-CA', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (Canada)', 'ShortNameFriendly': 'Linda'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-GB, George, Apollo)', 'ShortName': 'en-GB-George-Apollo', 'Gender': 'Male', 'Locale': 'en-GB', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (UK)', 'ShortNameFriendly': 'George,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-GB, HazelRUS)', 'ShortName': 'en-GB-HazelRUS', 'Gender': 'Female', 'Locale': 'en-GB', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (UK)', 'ShortNameFriendly': 'HazelRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-GB, LibbyNeural)', 'ShortName': 'en-GB-LibbyNeural', 'Gender': 'Female', 'Locale': 'en-GB', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'English (UK)', 'ShortNameFriendly': 'LibbyNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-GB, MiaNeural)', 'ShortName': 'en-GB-MiaNeural', 'Gender': 'Female', 'Locale': 'en-GB', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'English (UK)', 'ShortNameFriendly': 'MiaNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-GB, Susan, Apollo)', 'ShortName': 'en-GB-Susan-Apollo', 'Gender': 'Female', 'Locale': 'en-GB', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (UK)', 'ShortNameFriendly': 'Susan,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-IE, Sean)', 'ShortName': 'en-IE-Sean', 'Gender': 'Male', 'Locale': 'en-IE', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (Ireland)', 'ShortNameFriendly': 'Sean'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-IN, Heera, Apollo)', 'ShortName': 'en-IN-Heera-Apollo', 'Gender': 'Female', 'Locale': 'en-IN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (India)', 'ShortNameFriendly': 'Heera,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-IN, PriyaRUS)', 'ShortName': 'en-IN-PriyaRUS', 'Gender': 'Female', 'Locale': 'en-IN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (India)', 'ShortNameFriendly': 'PriyaRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-IN, Ravi, Apollo)', 'ShortName': 'en-IN-Ravi-Apollo', 'Gender': 'Male', 'Locale': 'en-IN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (India)', 'ShortNameFriendly': 'Ravi,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-US, Aria24kRUS)', 'ShortName': 'en-US-Aria24kRUS', 'Gender': 'Female', 'Locale': 'en-US', 'SampleRateHertz': '24000', 'VoiceType': 'Standard', 'Language': 'English (US)', 'ShortNameFriendly': 'Aria24kRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-US, AriaNeural)', 'ShortName': 'en-US-AriaNeural', 'Gender': 'Female', 'Locale': 'en-US', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'English (US)', 'ShortNameFriendly': 'AriaNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-US, AriaRUS)', 'ShortName': 'en-US-AriaRUS', 'Gender': 'Female', 'Locale': 'en-US', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (US)', 'ShortNameFriendly': 'AriaRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-US, BenjaminRUS)', 'ShortName': 'en-US-BenjaminRUS', 'Gender': 'Male', 'Locale': 'en-US', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (US)', 'ShortNameFriendly': 'BenjaminRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24kRUS)', 'ShortName': 'en-US-Guy24kRUS', 'Gender': 'Male', 'Locale': 'en-US', 'SampleRateHertz': '24000', 'VoiceType': 'Standard', 'Language': 'English (US)', 'ShortNameFriendly': 'Guy24kRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-US, GuyNeural)', 'ShortName': 'en-US-GuyNeural', 'Gender': 'Male', 'Locale': 'en-US', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'English (US)', 'ShortNameFriendly': 'GuyNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-US, ZiraRUS)', 'ShortName': 'en-US-ZiraRUS', 'Gender': 'Female', 'Locale': 'en-US', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (US)', 'ShortNameFriendly': 'ZiraRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (es-ES, ElviraNeural)', 'ShortName': 'es-ES-ElviraNeural', 'Gender': 'Female', 'Locale': 'es-ES', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Spanish (Spain)', 'ShortNameFriendly': 'ElviraNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (es-ES, HelenaRUS)', 'ShortName': 'es-ES-HelenaRUS', 'Gender': 'Female', 'Locale': 'es-ES', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Spanish (Spain)', 'ShortNameFriendly': 'HelenaRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (es-ES, Laura, Apollo)', 'ShortName': 'es-ES-Laura-Apollo', 'Gender': 'Female', 'Locale': 'es-ES', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Spanish (Spain)', 'ShortNameFriendly': 'Laura,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (es-ES, Pablo, Apollo)', 'ShortName': 'es-ES-Pablo-Apollo', 'Gender': 'Male', 'Locale': 'es-ES', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Spanish (Spain)', 'ShortNameFriendly': 'Pablo,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (es-MX, DaliaNeural)', 'ShortName': 'es-MX-DaliaNeural', 'Gender': 'Female', 'Locale': 'es-MX', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Spanish (Mexico)', 'ShortNameFriendly': 'DaliaNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (es-MX, HildaRUS)', 'ShortName': 'es-MX-HildaRUS', 'Gender': 'Female', 'Locale': 'es-MX', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Spanish (Mexico)', 'ShortNameFriendly': 'HildaRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (es-MX, Raul, Apollo)', 'ShortName': 'es-MX-Raul-Apollo', 'Gender': 'Male', 'Locale': 'es-MX', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Spanish (Mexico)', 'ShortNameFriendly': 'Raul,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fi-FI, HeidiRUS)', 'ShortName': 'fi-FI-HeidiRUS', 'Gender': 'Female', 'Locale': 'fi-FI', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Finnish', 'ShortNameFriendly': 'HeidiRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fr-CA, Caroline)', 'ShortName': 'fr-CA-Caroline', 'Gender': 'Female', 'Locale': 'fr-CA', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'French (Canada)', 'ShortNameFriendly': 'Caroline'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fr-CA, HarmonieRUS)', 'ShortName': 'fr-CA-HarmonieRUS', 'Gender': 'Female', 'Locale': 'fr-CA', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'French (Canada)', 'ShortNameFriendly': 'HarmonieRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fr-CA, SylvieNeural)', 'ShortName': 'fr-CA-SylvieNeural', 'Gender': 'Female', 'Locale': 'fr-CA', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'French (Canada)', 'ShortNameFriendly': 'SylvieNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fr-CH, Guillaume)', 'ShortName': 'fr-CH-Guillaume', 'Gender': 'Male', 'Locale': 'fr-CH', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'French (Switzerland)', 'ShortNameFriendly': 'Guillaume'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fr-FR, DeniseNeural)', 'ShortName': 'fr-FR-DeniseNeural', 'Gender': 'Female', 'Locale': 'fr-FR', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'French (France)', 'ShortNameFriendly': 'DeniseNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fr-FR, HortenseRUS)', 'ShortName': 'fr-FR-HortenseRUS', 'Gender': 'Female', 'Locale': 'fr-FR', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'French (France)', 'ShortNameFriendly': 'HortenseRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fr-FR, Julie, Apollo)', 'ShortName': 'fr-FR-Julie-Apollo', 'Gender': 'Female', 'Locale': 'fr-FR', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'French (France)', 'ShortNameFriendly': 'Julie,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fr-FR, Paul, Apollo)', 'ShortName': 'fr-FR-Paul-Apollo', 'Gender': 'Male', 'Locale': 'fr-FR', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'French (France)', 'ShortNameFriendly': 'Paul,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (he-IL, Asaf)', 'ShortName': 'he-IL-Asaf', 'Gender': 'Male', 'Locale': 'he-IL', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Hebrew (Israel)', 'ShortNameFriendly': 'Asaf'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (hi-IN, Hemant)', 'ShortName': 'hi-IN-Hemant', 'Gender': 'Male', 'Locale': 'hi-IN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Hindi (India)', 'ShortNameFriendly': 'Hemant'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (hi-IN, Kalpana)', 'ShortName': 'hi-IN-Kalpana', 'Gender': 'Female', 'Locale': 'hi-IN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Hindi (India)', 'ShortNameFriendly': 'Kalpana'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (hi-IN, Kalpana, Apollo)', 'ShortName': 'hi-IN-Kalpana-Apollo', 'Gender': 'Female', 'Locale': 'hi-IN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Hindi (India)', 'ShortNameFriendly': 'Kalpana,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (hr-HR, Matej)', 'ShortName': 'hr-HR-Matej', 'Gender': 'Male', 'Locale': 'hr-HR', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Croatian', 'ShortNameFriendly': 'Matej'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (hu-HU, Szabolcs)', 'ShortName': 'hu-HU-Szabolcs', 'Gender': 'Male', 'Locale': 'hu-HU', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Hungarian', 'ShortNameFriendly': 'Szabolcs'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (id-ID, Andika)', 'ShortName': 'id-ID-Andika', 'Gender': 'Male', 'Locale': 'id-ID', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Indonesian', 'ShortNameFriendly': 'Andika'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (it-IT, Cosimo, Apollo)', 'ShortName': 'it-IT-Cosimo-Apollo', 'Gender': 'Male', 'Locale': 'it-IT', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Italian', 'ShortNameFriendly': 'Cosimo,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (it-IT, ElsaNeural)', 'ShortName': 'it-IT-ElsaNeural', 'Gender': 'Female', 'Locale': 'it-IT', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Italian', 'ShortNameFriendly': 'ElsaNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (it-IT, LuciaRUS)', 'ShortName': 'it-IT-LuciaRUS', 'Gender': 'Female', 'Locale': 'it-IT', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Italian', 'ShortNameFriendly': 'LuciaRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ja-JP, Ayumi, Apollo)', 'ShortName': 'ja-JP-Ayumi-Apollo', 'Gender': 'Female', 'Locale': 'ja-JP', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Japanese', 'ShortNameFriendly': 'Ayumi,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ja-JP, HarukaRUS)', 'ShortName': 'ja-JP-HarukaRUS', 'Gender': 'Female', 'Locale': 'ja-JP', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Japanese', 'ShortNameFriendly': 'HarukaRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ja-JP, Ichiro, Apollo)', 'ShortName': 'ja-JP-Ichiro-Apollo', 'Gender': 'Male', 'Locale': 'ja-JP', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Japanese', 'ShortNameFriendly': 'Ichiro,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ja-JP, NanamiNeural)', 'ShortName': 'ja-JP-NanamiNeural', 'Gender': 'Female', 'Locale': 'ja-JP', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Japanese', 'ShortNameFriendly': 'NanamiNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ko-KR, HeamiRUS)', 'ShortName': 'ko-KR-HeamiRUS', 'Gender': 'Female', 'Locale': 'ko-KR', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Korean', 'ShortNameFriendly': 'HeamiRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ko-KR, SunHiNeural)', 'ShortName': 'ko-KR-SunHiNeural', 'Gender': 'Female', 'Locale': 'ko-KR', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Korean', 'ShortNameFriendly': 'SunHiNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ms-MY, Rizwan)', 'ShortName': 'ms-MY-Rizwan', 'Gender': 'Male', 'Locale': 'ms-MY', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Malay', 'ShortNameFriendly': 'Rizwan'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (nb-NO, HuldaRUS)', 'ShortName': 'nb-NO-HuldaRUS', 'Gender': 'Female', 'Locale': 'nb-NO', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Norwegian', 'ShortNameFriendly': 'HuldaRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (nb-NO, IselinNeural)', 'ShortName': 'nb-NO-IselinNeural', 'Gender': 'Female', 'Locale': 'nb-NO', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Norwegian', 'ShortNameFriendly': 'IselinNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (nl-NL, HannaRUS)', 'ShortName': 'nl-NL-HannaRUS', 'Gender': 'Female', 'Locale': 'nl-NL', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Dutch', 'ShortNameFriendly': 'HannaRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (pl-PL, PaulinaRUS)', 'ShortName': 'pl-PL-PaulinaRUS', 'Gender': 'Female', 'Locale': 'pl-PL', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Polish', 'ShortNameFriendly': 'PaulinaRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (pt-BR, Daniel, Apollo)', 'ShortName': 'pt-BR-Daniel-Apollo', 'Gender': 'Male', 'Locale': 'pt-BR', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Portuguese (Brazil)', 'ShortNameFriendly': 'Daniel,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (pt-BR, FranciscaNeural)', 'ShortName': 'pt-BR-FranciscaNeural', 'Gender': 'Female', 'Locale': 'pt-BR', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Portuguese (Brazil)', 'ShortNameFriendly': 'FranciscaNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (pt-BR, HeloisaRUS)', 'ShortName': 'pt-BR-HeloisaRUS', 'Gender': 'Female', 'Locale': 'pt-BR', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Portuguese (Brazil)', 'ShortNameFriendly': 'HeloisaRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (pt-PT, HeliaRUS)', 'ShortName': 'pt-PT-HeliaRUS', 'Gender': 'Female', 'Locale': 'pt-PT', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Portuguese (Portugal)', 'ShortNameFriendly': 'HeliaRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ro-RO, Andrei)', 'ShortName': 'ro-RO-Andrei', 'Gender': 'Male', 'Locale': 'ro-RO', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Romanian', 'ShortNameFriendly': 'Andrei'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ru-RU, EkaterinaRUS)', 'ShortName': 'ru-RU-EkaterinaRUS', 'Gender': 'Female', 'Locale': 'ru-RU', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Russian', 'ShortNameFriendly': 'EkaterinaRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ru-RU, Irina, Apollo)', 'ShortName': 'ru-RU-Irina-Apollo', 'Gender': 'Female', 'Locale': 'ru-RU', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Russian', 'ShortNameFriendly': 'Irina,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ru-RU, Pavel, Apollo)', 'ShortName': 'ru-RU-Pavel-Apollo', 'Gender': 'Male', 'Locale': 'ru-RU', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Russian', 'ShortNameFriendly': 'Pavel,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (sk-SK, Filip)', 'ShortName': 'sk-SK-Filip', 'Gender': 'Male', 'Locale': 'sk-SK', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Slovak', 'ShortNameFriendly': 'Filip'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (sl-SI, Lado)', 'ShortName': 'sl-SI-Lado', 'Gender': 'Male', 'Locale': 'sl-SI', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Slovenian', 'ShortNameFriendly': 'Lado'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (sv-SE, HedvigRUS)', 'ShortName': 'sv-SE-HedvigRUS', 'Gender': 'Female', 'Locale': 'sv-SE', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Swedish', 'ShortNameFriendly': 'HedvigRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ta-IN, Valluvar)', 'ShortName': 'ta-IN-Valluvar', 'Gender': 'Male', 'Locale': 'ta-IN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Tamil (India)', 'ShortNameFriendly': 'Valluvar'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (te-IN, Chitra)', 'ShortName': 'te-IN-Chitra', 'Gender': 'Female', 'Locale': 'te-IN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Telugu (India)', 'ShortNameFriendly': 'Chitra'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (th-TH, Pattara)', 'ShortName': 'th-TH-Pattara', 'Gender': 'Male', 'Locale': 'th-TH', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Thai', 'ShortNameFriendly': 'Pattara'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (tr-TR, EmelNeural)', 'ShortName': 'tr-TR-EmelNeural', 'Gender': 'Female', 'Locale': 'tr-TR', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Turkish (Turkey)', 'ShortNameFriendly': 'EmelNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (tr-TR, SedaRUS)', 'ShortName': 'tr-TR-SedaRUS', 'Gender': 'Female', 'Locale': 'tr-TR', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Turkish (Turkey)', 'ShortNameFriendly': 'SedaRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (vi-VN, An)', 'ShortName': 'vi-VN-An', 'Gender': 'Male', 'Locale': 'vi-VN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Vietnamese', 'ShortNameFriendly': 'An'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-CN, HuihuiRUS)', 'ShortName': 'zh-CN-HuihuiRUS', 'Gender': 'Female', 'Locale': 'zh-CN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Chinese (Mandarin, simplified)', 'ShortNameFriendly': 'HuihuiRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-CN, Kangkang, Apollo)', 'ShortName': 'zh-CN-Kangkang-Apollo', 'Gender': 'Male', 'Locale': 'zh-CN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Chinese (Mandarin, simplified)', 'ShortNameFriendly': 'Kangkang,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoxiaoNeural)', 'ShortName': 'zh-CN-XiaoxiaoNeural', 'Gender': 'Female', 'Locale': 'zh-CN', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Chinese (Mandarin, simplified)', 'ShortNameFriendly': 'XiaoxiaoNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoyouNeural)', 'ShortName': 'zh-CN-XiaoyouNeural', 'Gender': 'Female', 'Locale': 'zh-CN', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Chinese (Mandarin, simplified)', 'ShortNameFriendly': 'XiaoyouNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-CN, Yaoyao, Apollo)', 'ShortName': 'zh-CN-Yaoyao-Apollo', 'Gender': 'Female', 'Locale': 'zh-CN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Chinese (Mandarin, simplified)', 'ShortNameFriendly': 'Yaoyao,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-CN, YunyangNeural)', 'ShortName': 'zh-CN-YunyangNeural', 'Gender': 'Male', 'Locale': 'zh-CN', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Chinese (Mandarin, simplified)', 'ShortNameFriendly': 'YunyangNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-CN, YunyeNeural)', 'ShortName': 'zh-CN-YunyeNeural', 'Gender': 'Male', 'Locale': 'zh-CN', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Chinese (Mandarin, simplified)', 'ShortNameFriendly': 'YunyeNeural'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-HK, Danny, Apollo)', 'ShortName': 'zh-HK-Danny-Apollo', 'Gender': 'Male', 'Locale': 'zh-HK', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Chinese (Cantonese, Traditional)', 'ShortNameFriendly': 'Danny,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-HK, Tracy, Apollo)', 'ShortName': 'zh-HK-Tracy-Apollo', 'Gender': 'Female', 'Locale': 'zh-HK', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Chinese (Cantonese, Traditional)', 'ShortNameFriendly': 'Tracy,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-HK, TracyRUS)', 'ShortName': 'zh-HK-TracyRUS', 'Gender': 'Female', 'Locale': 'zh-HK', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Chinese (Cantonese, Traditional)', 'ShortNameFriendly': 'TracyRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-TW, HanHanRUS)', 'ShortName': 'zh-TW-HanHanRUS', 'Gender': 'Female', 'Locale': 'zh-TW', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Chinese (Taiwanese Mandarin)', 'ShortNameFriendly': 'HanHanRUS'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-TW, Yating, Apollo)', 'ShortName': 'zh-TW-Yating-Apollo', 'Gender': 'Female', 'Locale': 'zh-TW', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Chinese (Taiwanese Mandarin)', 'ShortNameFriendly': 'Yating,  Apollo'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-TW, Zhiwei, Apollo)', 'ShortName': 'zh-TW-Zhiwei-Apollo', 'Gender': 'Male', 'Locale': 'zh-TW', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Chinese (Taiwanese Mandarin)', 'ShortNameFriendly': 'Zhiwei,  Apollo'}
]


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

class Azure(Service):
    """
    Provides a Service-compliant implementation for Microsoft Azure Text To Speech.
    """

    __slots__ = [
        'access_token'
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

    def get_voice_list(self):
        """
        present the list of voices in a tuple, the first element being a key, the second one
        is a human-readable value
        """
        processed_voice_list = []
        for voice in VOICE_LIST:
            key = voice['Name']
            value = f"{voice['Language']}, {voice['Gender']}, {voice['VoiceType']}, {voice['ShortNameFriendly']}"
            processed_voice_list.append((key, value))

        # sort by human description order
        processed_voice_list.sort(key=lambda x: x[1])

        return processed_voice_list

    def get_language_for_voice(self, voice):
        for voice_entry in VOICE_LIST:
            if voice_entry['Name'] == voice:
                return voice_entry['Locale']
        raise ValueError(f'Voice not found: {voice}')

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
                 transform=lambda value: value)
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

    def run(self, text, options, path):
        """Downloads from Azure API directly to an MP3."""

        region = options['region']
        subscription_key = options['key']
        if self.access_token == None:
            self.get_token(subscription_key, region)

        voice = options['voice']
        voice_name = voice
        language = self.get_language_for_voice(voice)

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

        voice.text = text
        body = ElementTree.tostring(xml_body)

        response = requests.post(constructed_url, headers=headers, data=body)
        if response.status_code == 200:
            with open(path, 'wb') as audio:
                audio.write(response.content)
        else:
            error_message = f"Status code: {response.status_code} reason: {response.reason} voice: [{voice_name}] language: [{language} subscription key: [{subscription_key}]]"
            raise ValueError(error_message)



