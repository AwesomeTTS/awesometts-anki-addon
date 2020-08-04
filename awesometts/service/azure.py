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

__all__ = ['Azure']

# generated using tools/service_azure_voicelist.py
VOICE_LIST = [
{'Name': 'Microsoft Server Speech Text to Speech Voice (ar-EG, Hoda)', 'DisplayName': 'Hoda', 'LocalName': 'هدى', 'ShortName': 'ar-EG-Hoda', 'Gender': 'Female', 'Locale': 'ar-EG', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Arabic (Egypt)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ar-EG, SalmaNeural)', 'DisplayName': 'Salma', 'LocalName': 'سلمى', 'ShortName': 'ar-EG-SalmaNeural', 'Gender': 'Female', 'Locale': 'ar-EG', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Arabic (Egypt)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ar-SA, Naayf)', 'DisplayName': 'Naayf', 'LocalName': 'نايف', 'ShortName': 'ar-SA-Naayf', 'Gender': 'Male', 'Locale': 'ar-SA', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Arabic (Saudi Arabia)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ar-SA, ZariyahNeural)', 'DisplayName': 'Zariyah', 'LocalName': 'زارية', 'ShortName': 'ar-SA-ZariyahNeural', 'Gender': 'Female', 'Locale': 'ar-SA', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Arabic (Saudi Arabia)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (bg-BG, Ivan)', 'DisplayName': 'Ivan', 'LocalName': 'Ivan', 'ShortName': 'bg-BG-Ivan', 'Gender': 'Male', 'Locale': 'bg-BG', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Bulgarian'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ca-ES, AlbaNeural)', 'DisplayName': 'Alba', 'LocalName': 'Alba', 'ShortName': 'ca-ES-AlbaNeural', 'Gender': 'Female', 'Locale': 'ca-ES', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Catalan'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ca-ES, HerenaRUS)', 'DisplayName': 'Herena', 'LocalName': 'Herena', 'ShortName': 'ca-ES-HerenaRUS', 'Gender': 'Female', 'Locale': 'ca-ES', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Catalan'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (cs-CZ, Jakub)', 'DisplayName': 'Jakub', 'LocalName': 'Jakub', 'ShortName': 'cs-CZ-Jakub', 'Gender': 'Male', 'Locale': 'cs-CZ', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Czech'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (da-DK, ChristelNeural)', 'DisplayName': 'Christel', 'LocalName': 'Christel', 'ShortName': 'da-DK-ChristelNeural', 'Gender': 'Female', 'Locale': 'da-DK', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Danish'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (da-DK, HelleRUS)', 'DisplayName': 'Helle', 'LocalName': 'Helle', 'ShortName': 'da-DK-HelleRUS', 'Gender': 'Female', 'Locale': 'da-DK', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Danish'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (de-AT, Michael)', 'DisplayName': 'Michael', 'LocalName': 'Michael', 'ShortName': 'de-AT-Michael', 'Gender': 'Male', 'Locale': 'de-AT', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'German (Austria)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (de-CH, Karsten)', 'DisplayName': 'Karsten', 'LocalName': 'Karsten', 'ShortName': 'de-CH-Karsten', 'Gender': 'Male', 'Locale': 'de-CH', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'German (Switzerland)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (de-DE, HeddaRUS)', 'DisplayName': 'Hedda', 'LocalName': 'Hedda', 'ShortName': 'de-DE-HeddaRUS', 'Gender': 'Female', 'Locale': 'de-DE', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'German (Germany)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (de-DE, KatjaNeural)', 'DisplayName': 'Katja', 'LocalName': 'Katja', 'ShortName': 'de-DE-KatjaNeural', 'Gender': 'Female', 'Locale': 'de-DE', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'German (Germany)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (de-DE, Stefan, Apollo)', 'DisplayName': 'Stefan', 'LocalName': 'Stefan', 'ShortName': 'de-DE-Stefan-Apollo', 'Gender': 'Male', 'Locale': 'de-DE', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'German (Germany)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (el-GR, Stefanos)', 'DisplayName': 'Stefanos', 'LocalName': 'Stefanos', 'ShortName': 'el-GR-Stefanos', 'Gender': 'Male', 'Locale': 'el-GR', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Greek'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-AU, Catherine)', 'DisplayName': 'Catherine', 'LocalName': 'Catherine', 'ShortName': 'en-AU-Catherine', 'Gender': 'Female', 'Locale': 'en-AU', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (Australia)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-AU, HayleyRUS)', 'DisplayName': 'Hayley', 'LocalName': 'Hayley', 'ShortName': 'en-AU-HayleyRUS', 'Gender': 'Female', 'Locale': 'en-AU', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (Australia)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-AU, NatashaNeural)', 'DisplayName': 'Natasha', 'LocalName': 'Natasha', 'ShortName': 'en-AU-NatashaNeural', 'Gender': 'Female', 'Locale': 'en-AU', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'English (Australia)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-CA, ClaraNeural)', 'DisplayName': 'Clara', 'LocalName': 'Clara', 'ShortName': 'en-CA-ClaraNeural', 'Gender': 'Female', 'Locale': 'en-CA', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'English (Canada)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-CA, HeatherRUS)', 'DisplayName': 'Heather', 'LocalName': 'Heather', 'ShortName': 'en-CA-HeatherRUS', 'Gender': 'Female', 'Locale': 'en-CA', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (Canada)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-CA, Linda)', 'DisplayName': 'Linda', 'LocalName': 'Linda', 'ShortName': 'en-CA-Linda', 'Gender': 'Female', 'Locale': 'en-CA', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (Canada)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-GB, George, Apollo)', 'DisplayName': 'George', 'LocalName': 'George', 'ShortName': 'en-GB-George-Apollo', 'Gender': 'Male', 'Locale': 'en-GB', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (UK)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-GB, HazelRUS)', 'DisplayName': 'Hazel', 'LocalName': 'Hazel', 'ShortName': 'en-GB-HazelRUS', 'Gender': 'Female', 'Locale': 'en-GB', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (UK)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-GB, LibbyNeural)', 'DisplayName': 'Libby', 'LocalName': 'Libby', 'ShortName': 'en-GB-LibbyNeural', 'Gender': 'Female', 'Locale': 'en-GB', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'English (UK)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-GB, MiaNeural)', 'DisplayName': 'Mia', 'LocalName': 'Mia', 'ShortName': 'en-GB-MiaNeural', 'Gender': 'Female', 'Locale': 'en-GB', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'English (UK)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-GB, Susan, Apollo)', 'DisplayName': 'Susan', 'LocalName': 'Susan', 'ShortName': 'en-GB-Susan-Apollo', 'Gender': 'Female', 'Locale': 'en-GB', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (UK)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-IE, Sean)', 'DisplayName': 'Sean', 'LocalName': 'Sean', 'ShortName': 'en-IE-Sean', 'Gender': 'Male', 'Locale': 'en-IE', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (Ireland)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-IN, Heera, Apollo)', 'DisplayName': 'Heera', 'LocalName': 'Heera', 'ShortName': 'en-IN-Heera-Apollo', 'Gender': 'Female', 'Locale': 'en-IN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (India)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-IN, NeerjaNeural)', 'DisplayName': 'Neerja', 'LocalName': 'Neerja', 'ShortName': 'en-IN-NeerjaNeural', 'Gender': 'Female', 'Locale': 'en-IN', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'English (India)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-IN, PriyaRUS)', 'DisplayName': 'Priya', 'LocalName': 'Priya', 'ShortName': 'en-IN-PriyaRUS', 'Gender': 'Female', 'Locale': 'en-IN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (India)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-IN, Ravi, Apollo)', 'DisplayName': 'Ravi', 'LocalName': 'Ravi', 'ShortName': 'en-IN-Ravi-Apollo', 'Gender': 'Male', 'Locale': 'en-IN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (India)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-US, Aria24kRUS)', 'DisplayName': 'Aria', 'LocalName': 'Aria', 'ShortName': 'en-US-Aria24kRUS', 'Gender': 'Female', 'Locale': 'en-US', 'SampleRateHertz': '24000', 'VoiceType': 'Standard', 'Language': 'English (US)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-US, AriaNeural)', 'DisplayName': 'Aria', 'LocalName': 'Aria', 'ShortName': 'en-US-AriaNeural', 'Gender': 'Female', 'Locale': 'en-US', 'StyleList': ['newscast', 'customerservice', 'chat', 'cheerful', 'empathetic'], 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'English (US)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-US, BenjaminRUS)', 'DisplayName': 'Benjamin', 'LocalName': 'Benjamin', 'ShortName': 'en-US-BenjaminRUS', 'Gender': 'Male', 'Locale': 'en-US', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (US)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24kRUS)', 'DisplayName': 'Guy', 'LocalName': 'Guy', 'ShortName': 'en-US-Guy24kRUS', 'Gender': 'Male', 'Locale': 'en-US', 'SampleRateHertz': '24000', 'VoiceType': 'Standard', 'Language': 'English (US)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-US, GuyNeural)', 'DisplayName': 'Guy', 'LocalName': 'Guy', 'ShortName': 'en-US-GuyNeural', 'Gender': 'Male', 'Locale': 'en-US', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'English (US)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (en-US, ZiraRUS)', 'DisplayName': 'Zira', 'LocalName': 'Zira', 'ShortName': 'en-US-ZiraRUS', 'Gender': 'Female', 'Locale': 'en-US', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'English (US)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (es-ES, ElviraNeural)', 'DisplayName': 'Elvira', 'LocalName': 'Elvira', 'ShortName': 'es-ES-ElviraNeural', 'Gender': 'Female', 'Locale': 'es-ES', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Spanish (Spain)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (es-ES, HelenaRUS)', 'DisplayName': 'Helena', 'LocalName': 'Helena', 'ShortName': 'es-ES-HelenaRUS', 'Gender': 'Female', 'Locale': 'es-ES', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Spanish (Spain)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (es-ES, Laura, Apollo)', 'DisplayName': 'Laura', 'LocalName': 'Laura', 'ShortName': 'es-ES-Laura-Apollo', 'Gender': 'Female', 'Locale': 'es-ES', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Spanish (Spain)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (es-ES, Pablo, Apollo)', 'DisplayName': 'Pablo', 'LocalName': 'Pablo', 'ShortName': 'es-ES-Pablo-Apollo', 'Gender': 'Male', 'Locale': 'es-ES', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Spanish (Spain)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (es-MX, DaliaNeural)', 'DisplayName': 'Dalia', 'LocalName': 'Dalia', 'ShortName': 'es-MX-DaliaNeural', 'Gender': 'Female', 'Locale': 'es-MX', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Spanish (Mexico)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (es-MX, HildaRUS)', 'DisplayName': 'Hilda', 'LocalName': 'Hilda', 'ShortName': 'es-MX-HildaRUS', 'Gender': 'Female', 'Locale': 'es-MX', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Spanish (Mexico)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (es-MX, Raul, Apollo)', 'DisplayName': 'Raul', 'LocalName': 'Raúl', 'ShortName': 'es-MX-Raul-Apollo', 'Gender': 'Male', 'Locale': 'es-MX', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Spanish (Mexico)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fi-FI, HeidiRUS)', 'DisplayName': 'Heidi', 'LocalName': 'Heidi', 'ShortName': 'fi-FI-HeidiRUS', 'Gender': 'Female', 'Locale': 'fi-FI', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Finnish'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fi-FI, NooraNeural)', 'DisplayName': 'Noora', 'LocalName': 'Noora', 'ShortName': 'fi-FI-NooraNeural', 'Gender': 'Female', 'Locale': 'fi-FI', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Finnish'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fr-CA, Caroline)', 'DisplayName': 'Caroline', 'LocalName': 'Caroline', 'ShortName': 'fr-CA-Caroline', 'Gender': 'Female', 'Locale': 'fr-CA', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'French (Canada)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fr-CA, HarmonieRUS)', 'DisplayName': 'Harmonie', 'LocalName': 'Harmonie', 'ShortName': 'fr-CA-HarmonieRUS', 'Gender': 'Female', 'Locale': 'fr-CA', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'French (Canada)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fr-CA, SylvieNeural)', 'DisplayName': 'Sylvie', 'LocalName': 'Sylvie', 'ShortName': 'fr-CA-SylvieNeural', 'Gender': 'Female', 'Locale': 'fr-CA', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'French (Canada)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fr-CH, Guillaume)', 'DisplayName': 'Guillaume', 'LocalName': 'Guillaume', 'ShortName': 'fr-CH-Guillaume', 'Gender': 'Male', 'Locale': 'fr-CH', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'French (Switzerland)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fr-FR, DeniseNeural)', 'DisplayName': 'Denise', 'LocalName': 'Denise', 'ShortName': 'fr-FR-DeniseNeural', 'Gender': 'Female', 'Locale': 'fr-FR', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'French (France)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fr-FR, HortenseRUS)', 'DisplayName': 'Hortense', 'LocalName': 'Hortense', 'ShortName': 'fr-FR-HortenseRUS', 'Gender': 'Female', 'Locale': 'fr-FR', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'French (France)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fr-FR, Julie, Apollo)', 'DisplayName': 'Julie', 'LocalName': 'Julie', 'ShortName': 'fr-FR-Julie-Apollo', 'Gender': 'Female', 'Locale': 'fr-FR', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'French (France)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (fr-FR, Paul, Apollo)', 'DisplayName': 'Paul', 'LocalName': 'Paul', 'ShortName': 'fr-FR-Paul-Apollo', 'Gender': 'Male', 'Locale': 'fr-FR', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'French (France)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (he-IL, Asaf)', 'DisplayName': 'Asaf', 'LocalName': 'אסף', 'ShortName': 'he-IL-Asaf', 'Gender': 'Male', 'Locale': 'he-IL', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Hebrew (Israel)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (hi-IN, Hemant)', 'DisplayName': 'Hemant', 'LocalName': 'हेमन्त', 'ShortName': 'hi-IN-Hemant', 'Gender': 'Male', 'Locale': 'hi-IN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Hindi (India)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (hi-IN, Kalpana)', 'DisplayName': 'Kalpana', 'LocalName': 'कल्पना', 'ShortName': 'hi-IN-Kalpana', 'Gender': 'Female', 'Locale': 'hi-IN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Hindi (India)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (hi-IN, SwaraNeural)', 'DisplayName': 'Swara', 'LocalName': 'Swara', 'ShortName': 'hi-IN-SwaraNeural', 'Gender': 'Female', 'Locale': 'hi-IN', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Hindi (India)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (hr-HR, Matej)', 'DisplayName': 'Matej', 'LocalName': 'Matej', 'ShortName': 'hr-HR-Matej', 'Gender': 'Male', 'Locale': 'hr-HR', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Croatian'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (hu-HU, Szabolcs)', 'DisplayName': 'Szabolcs', 'LocalName': 'Szabolcs', 'ShortName': 'hu-HU-Szabolcs', 'Gender': 'Male', 'Locale': 'hu-HU', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Hungarian'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (id-ID, Andika)', 'DisplayName': 'Andika', 'LocalName': 'Andika', 'ShortName': 'id-ID-Andika', 'Gender': 'Male', 'Locale': 'id-ID', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Indonesian'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (it-IT, Cosimo, Apollo)', 'DisplayName': 'Cosimo', 'LocalName': 'Cosimo', 'ShortName': 'it-IT-Cosimo-Apollo', 'Gender': 'Male', 'Locale': 'it-IT', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Italian'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (it-IT, ElsaNeural)', 'DisplayName': 'Elsa', 'LocalName': 'Elsa', 'ShortName': 'it-IT-ElsaNeural', 'Gender': 'Female', 'Locale': 'it-IT', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Italian'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (it-IT, LuciaRUS)', 'DisplayName': 'Lucia', 'LocalName': 'Lucia', 'ShortName': 'it-IT-LuciaRUS', 'Gender': 'Female', 'Locale': 'it-IT', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Italian'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ja-JP, Ayumi, Apollo)', 'DisplayName': 'Ayumi', 'LocalName': '歩美', 'ShortName': 'ja-JP-Ayumi-Apollo', 'Gender': 'Female', 'Locale': 'ja-JP', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Japanese'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ja-JP, HarukaRUS)', 'DisplayName': 'Haruka', 'LocalName': '春香', 'ShortName': 'ja-JP-HarukaRUS', 'Gender': 'Female', 'Locale': 'ja-JP', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Japanese'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ja-JP, Ichiro, Apollo)', 'DisplayName': 'Ichiro', 'LocalName': '一郎', 'ShortName': 'ja-JP-Ichiro-Apollo', 'Gender': 'Male', 'Locale': 'ja-JP', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Japanese'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ja-JP, NanamiNeural)', 'DisplayName': 'Nanami', 'LocalName': '七海', 'ShortName': 'ja-JP-NanamiNeural', 'Gender': 'Female', 'Locale': 'ja-JP', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Japanese'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ko-KR, HeamiRUS)', 'DisplayName': 'Heami', 'LocalName': '해 미', 'ShortName': 'ko-KR-HeamiRUS', 'Gender': 'Female', 'Locale': 'ko-KR', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Korean'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ko-KR, SunHiNeural)', 'DisplayName': 'Sun-Hi', 'LocalName': '선히', 'ShortName': 'ko-KR-SunHiNeural', 'Gender': 'Female', 'Locale': 'ko-KR', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Korean'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ms-MY, Rizwan)', 'DisplayName': 'Rizwan', 'LocalName': 'Rizwan', 'ShortName': 'ms-MY-Rizwan', 'Gender': 'Male', 'Locale': 'ms-MY', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Malay'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (nb-NO, HuldaRUS)', 'DisplayName': 'Hulda', 'LocalName': 'Hulda', 'ShortName': 'nb-NO-HuldaRUS', 'Gender': 'Female', 'Locale': 'nb-NO', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Norwegian'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (nb-NO, IselinNeural)', 'DisplayName': 'Iselin', 'LocalName': 'Iselin', 'ShortName': 'nb-NO-IselinNeural', 'Gender': 'Female', 'Locale': 'nb-NO', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Norwegian'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (nl-NL, ColetteNeural)', 'DisplayName': 'Colette', 'LocalName': 'Colette', 'ShortName': 'nl-NL-ColetteNeural', 'Gender': 'Female', 'Locale': 'nl-NL', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Dutch'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (nl-NL, HannaRUS)', 'DisplayName': 'Hanna', 'LocalName': 'Hanna', 'ShortName': 'nl-NL-HannaRUS', 'Gender': 'Female', 'Locale': 'nl-NL', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Dutch'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (pl-PL, PaulinaRUS)', 'DisplayName': 'Paulina', 'LocalName': 'Paulina', 'ShortName': 'pl-PL-PaulinaRUS', 'Gender': 'Female', 'Locale': 'pl-PL', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Polish'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (pl-PL, ZofiaNeural)', 'DisplayName': 'Zofia', 'LocalName': 'Zofia', 'ShortName': 'pl-PL-ZofiaNeural', 'Gender': 'Female', 'Locale': 'pl-PL', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Polish'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (pt-BR, Daniel, Apollo)', 'DisplayName': 'Daniel', 'LocalName': 'Daniel', 'ShortName': 'pt-BR-Daniel-Apollo', 'Gender': 'Male', 'Locale': 'pt-BR', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Portuguese (Brazil)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (pt-BR, FranciscaNeural)', 'DisplayName': 'Francisca', 'LocalName': 'Francisca', 'ShortName': 'pt-BR-FranciscaNeural', 'Gender': 'Female', 'Locale': 'pt-BR', 'StyleList': ['cheerful', 'calm'], 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Portuguese (Brazil)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (pt-BR, HeloisaRUS)', 'DisplayName': 'Heloisa', 'LocalName': 'Heloisa', 'ShortName': 'pt-BR-HeloisaRUS', 'Gender': 'Female', 'Locale': 'pt-BR', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Portuguese (Brazil)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (pt-PT, FernandaNeural)', 'DisplayName': 'Fernanda', 'LocalName': 'Fernanda', 'ShortName': 'pt-PT-FernandaNeural', 'Gender': 'Female', 'Locale': 'pt-PT', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Portuguese (Portugal)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (pt-PT, HeliaRUS)', 'DisplayName': 'Helia', 'LocalName': 'Hélia', 'ShortName': 'pt-PT-HeliaRUS', 'Gender': 'Female', 'Locale': 'pt-PT', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Portuguese (Portugal)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ro-RO, Andrei)', 'DisplayName': 'Andrei', 'LocalName': 'Andrei', 'ShortName': 'ro-RO-Andrei', 'Gender': 'Male', 'Locale': 'ro-RO', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Romanian'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ru-RU, DariyaNeural)', 'DisplayName': 'Dariya', 'LocalName': 'Дария', 'ShortName': 'ru-RU-DariyaNeural', 'Gender': 'Female', 'Locale': 'ru-RU', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Russian'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ru-RU, EkaterinaRUS)', 'DisplayName': 'Ekaterina', 'LocalName': 'Екатерина', 'ShortName': 'ru-RU-EkaterinaRUS', 'Gender': 'Female', 'Locale': 'ru-RU', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Russian'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ru-RU, Irina, Apollo)', 'DisplayName': 'Irina', 'LocalName': 'Ирина', 'ShortName': 'ru-RU-Irina-Apollo', 'Gender': 'Female', 'Locale': 'ru-RU', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Russian'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ru-RU, Pavel, Apollo)', 'DisplayName': 'Pavel', 'LocalName': 'Павел', 'ShortName': 'ru-RU-Pavel-Apollo', 'Gender': 'Male', 'Locale': 'ru-RU', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Russian'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (sk-SK, Filip)', 'DisplayName': 'Filip', 'LocalName': 'Filip', 'ShortName': 'sk-SK-Filip', 'Gender': 'Male', 'Locale': 'sk-SK', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Slovak'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (sl-SI, Lado)', 'DisplayName': 'Lado', 'LocalName': 'Lado', 'ShortName': 'sl-SI-Lado', 'Gender': 'Male', 'Locale': 'sl-SI', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Slovenian'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (sv-SE, HedvigRUS)', 'DisplayName': 'Hedvig', 'LocalName': 'Hedvig', 'ShortName': 'sv-SE-HedvigRUS', 'Gender': 'Female', 'Locale': 'sv-SE', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Swedish'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (sv-SE, HilleviNeural)', 'DisplayName': 'Hillevi', 'LocalName': 'Hillevi', 'ShortName': 'sv-SE-HilleviNeural', 'Gender': 'Female', 'Locale': 'sv-SE', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Swedish'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (ta-IN, Valluvar)', 'DisplayName': 'Valluvar', 'LocalName': 'வள்ளுவர்', 'ShortName': 'ta-IN-Valluvar', 'Gender': 'Male', 'Locale': 'ta-IN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Tamil (India)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (te-IN, Chitra)', 'DisplayName': 'Chitra', 'LocalName': 'చిత్ర', 'ShortName': 'te-IN-Chitra', 'Gender': 'Female', 'Locale': 'te-IN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Telugu (India)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (th-TH, AcharaNeural)', 'DisplayName': 'Achara', 'LocalName': 'อัจฉรา', 'ShortName': 'th-TH-AcharaNeural', 'Gender': 'Female', 'Locale': 'th-TH', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Thai'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (th-TH, Pattara)', 'DisplayName': 'Pattara', 'LocalName': 'ภัทรา', 'ShortName': 'th-TH-Pattara', 'Gender': 'Male', 'Locale': 'th-TH', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Thai'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (tr-TR, EmelNeural)', 'DisplayName': 'Emel', 'LocalName': 'Emel', 'ShortName': 'tr-TR-EmelNeural', 'Gender': 'Female', 'Locale': 'tr-TR', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Turkish (Turkey)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (tr-TR, SedaRUS)', 'DisplayName': 'Seda', 'LocalName': 'Seda', 'ShortName': 'tr-TR-SedaRUS', 'Gender': 'Female', 'Locale': 'tr-TR', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Turkish (Turkey)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (vi-VN, An)', 'DisplayName': 'An', 'LocalName': 'An', 'ShortName': 'vi-VN-An', 'Gender': 'Male', 'Locale': 'vi-VN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Vietnamese'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-CN, HuihuiRUS)', 'DisplayName': 'Huihui', 'LocalName': '慧慧', 'ShortName': 'zh-CN-HuihuiRUS', 'Gender': 'Female', 'Locale': 'zh-CN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Chinese (Mandarin, simplified)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-CN, Kangkang, Apollo)', 'DisplayName': 'Kangkang', 'LocalName': '康康', 'ShortName': 'zh-CN-Kangkang-Apollo', 'Gender': 'Male', 'Locale': 'zh-CN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Chinese (Mandarin, simplified)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoxiaoNeural)', 'DisplayName': 'Xiaoxiao', 'LocalName': '晓晓', 'ShortName': 'zh-CN-XiaoxiaoNeural', 'Gender': 'Female', 'Locale': 'zh-CN', 'StyleList': ['lyrical', 'customerservice', 'newscast', 'assistant'], 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Chinese (Mandarin, simplified)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoyouNeural)', 'DisplayName': 'Xiaoyou', 'LocalName': '晓悠', 'ShortName': 'zh-CN-XiaoyouNeural', 'Gender': 'Female', 'Locale': 'zh-CN', 'StyleList': ['chat'], 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Chinese (Mandarin, simplified)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-CN, Yaoyao, Apollo)', 'DisplayName': 'Yaoyao', 'LocalName': '瑶瑶', 'ShortName': 'zh-CN-Yaoyao-Apollo', 'Gender': 'Female', 'Locale': 'zh-CN', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Chinese (Mandarin, simplified)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-CN, YunyangNeural)', 'DisplayName': 'Yunyang', 'LocalName': '云扬', 'ShortName': 'zh-CN-YunyangNeural', 'Gender': 'Male', 'Locale': 'zh-CN', 'StyleList': ['customerservice'], 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Chinese (Mandarin, simplified)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-CN, YunyeNeural)', 'DisplayName': 'Yunye', 'LocalName': '云野', 'ShortName': 'zh-CN-YunyeNeural', 'Gender': 'Male', 'Locale': 'zh-CN', 'StyleList': ['calm', 'sad', 'serious'], 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Chinese (Mandarin, simplified)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-HK, Danny, Apollo)', 'DisplayName': 'Danny', 'LocalName': 'Danny', 'ShortName': 'zh-HK-Danny-Apollo', 'Gender': 'Male', 'Locale': 'zh-HK', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Chinese (Cantonese, Traditional)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-HK, HiuGaaiNeural)', 'DisplayName': 'Hiugaai', 'LocalName': '曉佳', 'ShortName': 'zh-HK-HiugaaiNeural', 'Gender': 'Female', 'Locale': 'zh-HK', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Chinese (Cantonese, Traditional)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-HK, TracyRUS)', 'DisplayName': 'Tracy', 'LocalName': 'Tracy', 'ShortName': 'zh-HK-TracyRUS', 'Gender': 'Female', 'Locale': 'zh-HK', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Chinese (Cantonese, Traditional)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-TW, HanHanRUS)', 'DisplayName': 'HanHan', 'LocalName': '涵涵', 'ShortName': 'zh-TW-HanHanRUS', 'Gender': 'Female', 'Locale': 'zh-TW', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Chinese (Taiwanese Mandarin)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-TW, HsiaoYuNeural)', 'DisplayName': 'HsiaoYu', 'LocalName': '曉雨', 'ShortName': 'zh-TW-HsiaoYuNeural', 'Gender': 'Female', 'Locale': 'zh-TW', 'SampleRateHertz': '24000', 'VoiceType': 'Neural', 'Language': 'Chinese (Taiwanese Mandarin)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-TW, Yating, Apollo)', 'DisplayName': 'Yating', 'LocalName': '雅婷', 'ShortName': 'zh-TW-Yating-Apollo', 'Gender': 'Female', 'Locale': 'zh-TW', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Chinese (Taiwanese Mandarin)'},
{'Name': 'Microsoft Server Speech Text to Speech Voice (zh-TW, Zhiwei, Apollo)', 'DisplayName': 'Zhiwei', 'LocalName': '志威', 'ShortName': 'zh-TW-Zhiwei-Apollo', 'Gender': 'Male', 'Locale': 'zh-TW', 'SampleRateHertz': '16000', 'VoiceType': 'Standard', 'Language': 'Chinese (Taiwanese Mandarin)'},
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

    def get_voice_list(self):
        """
        present the list of voices in a tuple, the first element being a key, the second one
        is a human-readable value
        """
        processed_voice_list = []
        for voice in VOICE_LIST:
            key = voice['Name']
            display_name = voice['DisplayName']
            if voice['DisplayName'] != voice['LocalName']:
                display_name = f"{voice['DisplayName']}, {voice['LocalName']}"
            value = f"{voice['Language']}, {voice['Gender']}, {voice['VoiceType']}, {display_name}"
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



