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
HMAC_KEY = 'v1.5.4_5e97b423d4'
UUID = str(uuid.uuid4())


# This function implements function I(a,t) found at
# https://papago.naver.com/main.87cbe57a9fc46d3db5c1.chunk.js

def _generate_headers():
    timestamp = str(int(time.time()))
    msg = UUID + '\n' + TRANSLATE_MKID + '\n' + timestamp
    signature = hmac.new(bytes(HMAC_KEY, 'ascii'), bytes(msg, 'ascii'),
                         hashlib.md5).digest()
    signature = base64.b64encode(signature).decode()
    auth = 'PPG ' + UUID + ':' + signature

    return {'Authorization': auth, 'timestamp': timestamp,
            'Content-Type': 'application/x-www-form-urlencoded'}




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

        def process_subtext(output_mp3, subtext):
            params = dict(
                config +
                [
                    ('text', subtext),
                ]
            )
            resp = self.net_stream(
                (
                    TRANSLATE_MKID,
                    params
                ),
                method='POST',
                custom_headers=_generate_headers()
            )

            sound_id = json.loads(resp)['id']

            self.net_download(
                output_mp3,
                (
                    TRANSLATE_ENDPOINT + sound_id,
                    dict()
                ),
                require=dict(mime='audio/mpeg', size=256),
            )

        subtexts = self.util_split(text, 1000)

        if len(subtexts) == 1:
            process_subtext(path, subtexts[0])

        else:
            try:
                output_mp3s = []

                for subtext in subtexts:
                    output_mp3 = self.path_temp('mp3')
                    output_mp3s.append(output_mp3)
                    process_subtext(output_mp3, subtext)

                self.util_merge(output_mp3s, path)

            finally:
                self.path_unlink(output_mp3s)
