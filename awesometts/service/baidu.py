# -*- coding: utf-8 -*-

# AwesomeTTS text-to-speech add-on for Anki
# Copyright (C) 2010-Present  Anki AwesomeTTS Development Team
# Copyright (C) 2020 Christopher J. Howard
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
Service implementation for Baidu Speech API
"""

from .base import Service
from .common import Trait
from urllib.parse import quote_plus
from urllib.parse import urlencode
from urllib.request import Request
from urllib.request import urlopen
import datetime
import json

__all__ = ['Baidu']

class Baidu(Service):
    """
    Provides a Service-compliant implementation for Baidu Speech.
    """

    __slots__ = [
        'access_token',
        'token_expiration_date'
    ]

    NAME = "Baidu Speech"
    
    TRAITS = [Trait.INTERNET, Trait.TRANSCODING]
    
    VOICE_CODES = [
        (0, "Chinese (Mandarin), Standard Female, Du Xiaomei (度小美)"),
        (1, "Chinese (Mandarin), Standard Male, Du Xiaoyu (度小宇)"),
        (3, "Chinese (Mandarin), Expressive Male, Du Xiaoyao (度逍遥)"),
        (4, "Chinese (Mandarin), Expressive Child, Du Yaya (度丫丫)"),
    ]
    
    AUDIO_ENCODINGS = [
        (3, "MP3"),
        (6, "WAV (PCM-16K)"),
    ]

    def desc(self):
        """
        Returns a short, static description.
        """
        
        return "Baidu Speech (%d voices)" % len(self.VOICE_CODES)

    def extras(self):
        """
        Baidu Speech requires an API key and secret key.
        """
        
        return [
            dict(key='api', label="API Key", required=True),
            dict(key='secret', label="Secret Key", required=True),
        ]

    def options(self):
        """
        Provides access to voice only.
        """
        
        self.access_token = None

        return [
            dict(
                key='voice',
                label="Voice",
                values=self.VOICE_CODES,
                transform=lambda value: value,
                default=0,
            ),

            dict(
                key='speed',
                label="Speed",
                values=(0, 15),
                transform=int,
                default=5,
            ),

            dict(
                key='pitch',
                label="Pitch",
                values=(0, 15),
                transform=int,
                default=5,
            ),
            
            dict(
                key='volume',
                label="Volume",
                values=(0, 15),
                transform=int,
                default=5,
            ),
            
            dict(
                key='encoding',
                label="Source Encoding",
                values=self.AUDIO_ENCODINGS,
                transform=lambda value: value,
                default=3,
            ),
        ]
    
    def token_invalid(self):
        if self.access_token is None:
            return True
        if (datetime.datetime.now() - self.token_expiration_date).total_seconds() >= 0:
            return True
        return False
    
    def fetch_token(self, api_key, secret_key):
        """
        Requests an access token from Baidu
        """
    
        if len(api_key) == 0:
            raise ValueError("API key required")
        elif len(secret_key) == 0:
            raise ValueError("Secret key required")
        
        params = {
            'grant_type': 'client_credentials',
            'client_id': api_key,
            'client_secret': secret_key
        }
        
        post_data = urlencode(params).encode('utf-8')
        
        req = Request('http://openapi.baidu.com/oauth/2.0/token', post_data)
        result = json.loads(urlopen(req, timeout=5).read().decode())
        
        if 'access_token' in result.keys() and 'scope' in result.keys():
            if not 'audio_tts_post' in result['scope'].split(' '):
                raise ValueError("Denied permission to access TTS service")
        else:
            raise ValueError("Invalid API key or secret key")
        
        self.access_token = result['access_token']
        self.token_expiration_date = datetime.datetime.now() + datetime.timedelta(seconds=int(result['expires_in']))
    
    def run(self, text, options, path):
        """
        Sends a synthesis request to the Baidu Speech API and saves the returned audio data.
        """
        
        if self.token_invalid():
            self.fetch_token(options['api'], options['secret'])
        
        params = {
            'tok': self.access_token,
            'tex': quote_plus(text),
            'per': options['voice'],
            'spd': options['speed'],
            'pit': options['pitch'],
            'vol': options['volume'],
            'aue': options['encoding'],
            'cuid': "123456PYTHON",
            'lan': 'zh',
            'ctp': 1
        }
        
        post_data = urlencode(params).encode('utf-8')
        req = Request('http://tsn.baidu.com/text2audio', post_data)
        audio_content = urlopen(req).read()
        
        if options['encoding'] == 3:
            # Write MP3 audio content direct to file
            with open(path, 'wb') as response_output:
                response_output.write(audio_content)
        else:
            # Transcode WAV to MP3
            try:
                temp_file = self.path_temp('wav')
                
                with open(temp_file, 'wb') as file:
                    file.write(audio_content)
                
                self.cli_transcode(
                    temp_file,
                    path,
                    require=dict(
                        size_in=4096,
                    ),
                )

            finally:
                self.path_unlink(temp_file)

