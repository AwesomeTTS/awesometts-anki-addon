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


VOICES = {
    'Microsoft Server Speech Text to Speech Voice (ar-EG, Hoda)': ('ar-EG', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (ar-SA, Naayf)': ('ar-SA', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (bg-BG, Ivan)': ('bg-BG', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (ca-ES, HerenaRUS)': ('ca-ES', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (cs-CZ, Jakub)': ('cs-CZ', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (da-DK, HelleRUS)': ('da-DK', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (de-AT, Michael)': ('de-AT', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (de-CH, Karsten)': ('de-CH', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (de-DE, Hedda)': ('de-DE', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (de-DE, HeddaRUS)': ('de-DE', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (de-DE, KatjaNeural)': ('de-DE', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (de-DE, Stefan, Apollo)': ('de-DE', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (el-GR, Stefanos)': ('el-GR', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (en-AU, Catherine)': ('en-AU', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (en-AU, HayleyRUS)': ('en-AU', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (en-CA, HeatherRUS)': ('en-CA', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (en-CA, Linda)': ('en-CA', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (en-GB, George, Apollo)': ('en-GB', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (en-GB, HazelRUS)': ('en-GB', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (en-GB, Susan, Apollo)': ('en-GB', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (en-IE, Sean)': ('en-IE', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (en-IN, Heera, Apollo)': ('en-IN', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (en-IN, PriyaRUS)': ('en-IN', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (en-IN, Ravi, Apollo)': ('en-IN', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (en-US, BenjaminRUS)': ('en-US', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (en-US, Guy24kRUS)': ('en-US', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (en-US, GuyNeural)': ('en-US', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (en-US, Jessa24kRUS)': ('en-US', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (en-US, JessaNeural)': ('en-US', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (en-US, JessaRUS)': ('en-US', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (en-US, ZiraRUS)': ('en-US', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (es-ES, HelenaNeural)': ('es-ES', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (es-ES, HelenaRUS)': ('es-ES', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (es-ES, Laura, Apollo)': ('es-ES', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (es-ES, Pablo, Apollo)': ('es-ES', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (es-MX, HildaNeural)': ('es-MX', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (es-MX, HildaRUS)': ('es-MX', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (es-MX, Raul, Apollo)': ('es-MX', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (fi-FI, HeidiRUS)': ('fi-FI', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (fr-CA, Caroline)': ('fr-CA', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (fr-CA, HarmonieRUS)': ('fr-CA', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (fr-CH, Guillaume)': ('fr-CH', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (fr-FR, HortenseRUS)': ('fr-FR', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (fr-FR, Julie, Apollo)': ('fr-FR', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (fr-FR, Paul, Apollo)': ('fr-FR', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (he-IL, Asaf)': ('he-IL', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (hi-IN, Hemant)': ('hi-IN', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (hi-IN, Kalpana)': ('hi-IN', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (hi-IN, Kalpana, Apollo)': ('hi-IN', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (hr-HR, Matej)': ('hr-HR', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (hu-HU, Szabolcs)': ('hu-HU', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (id-ID, Andika)': ('id-ID', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (it-IT, Cosimo, Apollo)': ('it-IT', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (it-IT, ElsaNeural)': ('it-IT', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (it-IT, LuciaRUS)': ('it-IT', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (ja-JP, Ayumi, Apollo)': ('ja-JP', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (ja-JP, HarukaRUS)': ('ja-JP', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (ja-JP, Ichiro, Apollo)': ('ja-JP', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (ko-KR, HeamiRUS)': ('ko-KR', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (ms-MY, Rizwan)': ('ms-MY', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (nb-NO, HuldaRUS)': ('nb-NO', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (nl-NL, HannaRUS)': ('nl-NL', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (pl-PL, PaulinaRUS)': ('pl-PL', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (pt-BR, Daniel, Apollo)': ('pt-BR', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (pt-BR, HeloisaNeural)': ('pt-BR', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (pt-BR, HeloisaRUS)': ('pt-BR', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (pt-PT, HeliaRUS)': ('pt-PT', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (ro-RO, Andrei)': ('ro-RO', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (ru-RU, EkaterinaRUS)': ('ru-RU', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (ru-RU, Irina, Apollo)': ('ru-RU', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (ru-RU, Pavel, Apollo)': ('ru-RU', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (sk-SK, Filip)': ('sk-SK', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (sl-SI, Lado)': ('sl-SI', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (sv-SE, HedvigRUS)': ('sv-SE', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (ta-IN, Valluvar)': ('ta-IN', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (te-IN, Chitra)': ('te-IN', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (th-TH, Pattara)': ('th-TH', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (tr-TR, SedaRUS)': ('tr-TR', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (vi-VN, An)': ('vi-VN', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (zh-CN, HuihuiRUS)': ('zh-CN', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (zh-CN, Kangkang, Apollo)': ('zh-CN', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoxiaoNeural)': ('zh-CN', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (zh-CN, Yaoyao, Apollo)': ('zh-CN', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (zh-HK, Danny, Apollo)': ('zh-HK', 'Male'),
    'Microsoft Server Speech Text to Speech Voice (zh-HK, Tracy, Apollo)': ('zh-HK', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (zh-HK, TracyRUS)': ('zh-HK', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (zh-TW, HanHanRUS)': ('zh-TW', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (zh-TW, Yating, Apollo)': ('zh-TW', 'Female'),
    'Microsoft Server Speech Text to Speech Voice (zh-TW, Zhiwei, Apollo)': ('zh-TW', 'Male')
}


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

    #def __init__(self, temp_dir, lame_flags, normalize, logger, ecosystem):
    #    super(Azure, self).__init__(temp_dir, lame_flags, normalize, logger, ecosystem)
    #    self.access_token = None


    def desc(self):
        """Returns name with a voice count."""

        return "Azure API (%d voices)" % len(VOICES)

    def extras(self):
        """The Azure API requires an API key."""

        return [dict(key='key', label="API Key", required=True)]

    def options(self):
        """Provides access to voice only."""

        # make sure access token is requested when retrieving audio
        self.access_token = None

        def transform_voice(user_value):
            return user_value

        def get_voice_choices():
            result = []
            for voice_name, attributes in VOICES.items():
                entry = (voice_name, voice_name)
                result.append(entry)
            return result

        return [
            dict(key='voice',
                 label="Voice",
                 values=get_voice_choices(),
                 transform=transform_voice)
        ]

    def get_token(self, subscription_key):
        if len(subscription_key) == 0:
            raise ValueError("subscription key required")

        fetch_token_url = "https://eastus.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        self.access_token = str(response.text)

    def run(self, text, options, path):
        """Downloads from Azure API directly to an MP3."""

        subscription_key = options['key']
        if self.access_token == None:
            self.get_token(subscription_key)

        voice = options['voice']
        voice_name = voice
        language = VOICES[voice_name][0]

        base_url = 'https://eastus.tts.speech.microsoft.com/'
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



