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

"""Naver Papago"""

from .base import Service
from .common import Trait

import base64
import hashlib
import hmac
import json
import time
import uuid
import requests
import datetime


__all__ = ['Naver']


TRANSLATE_ENDPOINT = 'https://papago.naver.com/apis/tts/'
TRANSLATE_MKID = TRANSLATE_ENDPOINT + 'makeID'

VOICE_CODES = [
    ('ko', (
        "Korean",
        [
            ('alpha', 0),
            ('pitch', 0),
            ('speaker', 'kyuri'),
            ('speed', 0),
        ],
    )),

    ('en', (
        "English",
        [
            ('alpha', 0),
            ('pitch', 0),
            ('speaker', 'clara'),
            ('speed', 0),
        ],
    )),

    ('ja', (
        "Japanese",
        [
            ('alpha', 0),
            ('pitch', 0),
            ('speaker', 'yuri'),
            ('speed', 0),
        ],
    )),

    ('zh-CN', (
        "Chinese - Simplified",
        [
            ('alpha', 0),
            ('pitch', 0),
            ('speaker', 'meimei'),
            ('speed', 0),
        ],
    )),

    ('zh-TW', (
        "Chinese - Traditional",
        [
            ('alpha', 0),
            ('pitch', 0),
            ('speaker', 'chiahua'),
            ('speed', 0),
        ],
    )),

    ('es', (
        "Spanish",
        [
            ('alpha', 0),
            ('pitch', 0),
            ('speaker', 'carmen'),
            ('speed', 0),
        ],
    )),

    ('fr', (
        "French",
        [
            ('alpha', 0),
            ('pitch', 0),
            ('speaker', 'roxane'),
            ('speed', 0),
        ],
    )),

    ('de', (
        "German",
        [
            ('alpha', 0),
            ('pitch', 0),
            ('speaker', 'lena'),
            ('speed', 0),
        ],
    )),

    ('ru', (
        "Russian",
        [
            ('alpha', 0),
            ('pitch', 0),
            ('speaker', 'vera'),
            ('speed', 0),
        ],
    )),

    ('th', (
        "Thai",
        [
            ('alpha', 0),
            ('pitch', 0),
            ('speaker', 'somsi'),
            ('speed', 0),
        ],
    )),
]

VOICE_LOOKUP = dict(VOICE_CODES)
HMAC_KEY = 'v1.6.6_b84eb7dae4'
UUID = str(uuid.uuid4())


# This function implements function I(a,t) found at
# https://papago.naver.com/main.87cbe57a9fc46d3db5c1.chunk.js
# 2021/05/27 update:
# HMAC_KEY has changed, and the timestamp is now in milliseconds

def _compute_token(timestamp, uuid_str):
    msg = uuid_str + '\n' + TRANSLATE_MKID + '\n' + timestamp
    signature = hmac.new(bytes(HMAC_KEY, 'ascii'), bytes(msg, 'ascii'),
                         hashlib.md5).digest()
    signature = base64.b64encode(signature).decode()
    auth = 'PPG ' + uuid_str + ':' + signature
    return auth

def _generate_headers():
    timestamp_seconds_float = datetime.datetime.now().timestamp()
    timestamp_milliseconds = timestamp_seconds_float * 1000.0
    timestamp_str = str(int(timestamp_milliseconds))
    auth = _compute_token(timestamp_str, UUID)

    return {'authorization': auth, 
            'timestamp': timestamp_str,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'papago.naver.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
            'Accept': 'application/json',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Content-Length': '64',
            'Origin': 'https://papago.naver.com',
            'Referer': 'https://papago.naver.com/',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'TE': 'Trailers'
    }




class Naver(Service):
    """Provides a Service implementation for Naver Papago."""

    __slots__ = []

    NAME = "Naver Papago"

    TRAITS = [Trait.INTERNET]

    def desc(self):
        """Returns a static description."""

        return "Naver Papago (%d voices)" % len(VOICE_CODES)

    def options(self):
        """Returns an option to select the voice."""

        return [
            dict(
                key='voice',
                label="Voice",
                values=[(key, description)
                        for key, (description, _) in VOICE_CODES],
                transform=lambda value: value,
                default='ko',
                test_default='en'
            ),
        ]


    def run(self, text, options, path):
        """Downloads from Internet directly to an MP3."""

        _, config = VOICE_LOOKUP[options['voice']]

        # first, make a POST request to retrieve ID of the sound
        # ======================================================

        url = TRANSLATE_MKID
        params = dict(
            config +
            [
                ('text', text),
            ]
        )        
        headers = _generate_headers()
        self._logger.info(f'executing POST request on {url} with headers={headers}, data={params}')
        response = requests.post(url, headers=headers, data=params)
        if response.status_code != 200:
            raise Exception(f'got status_code {response.status_code} from {url}: {response.content} ')

        response_data = response.json()
        sound_id = response_data['id']
        self._logger.info(f'retrieved sound_id successfully: {sound_id}')

        # actually retrieve sound file
        # ============================

        final_url = TRANSLATE_ENDPOINT + sound_id
        self._logger.info(f'final_url: {final_url}')

        self.net_download(
            path,
            (
                final_url,
                dict()
            ),
            require=dict(mime='audio/mpeg', size=256),
        )