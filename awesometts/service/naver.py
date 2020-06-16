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

"""NAVER Translate"""

from .base import Service
from .common import Trait

import base64
import json

__all__ = ['Naver']


CNDIC_ENDPOINT = 'http://tts.cndic.naver.com/tts/mp3ttsV1.cgi'
CNDIC_CONFIG = [
    ('enc', 0),
    ('pitch', 100),
    ('speed', 80),
    ('text_fmt', 0),
    ('volume', 100),
    ('wrapper', 0),
]

TRANSLATE_ENDPOINT = 'https://papago.naver.com/apis/tts/'
TRANSLATE_MKID = TRANSLATE_ENDPOINT + 'makeID'

VOICE_CODES = [
    ('ko', (
        "Korean",
        False,
        [
            ('speaker', 'mijin'),
        ],
    )),

    ('en', (
        "English",
        False,
        [
            ('speaker', 'clara'),
        ],
    )),

    ('ja', (
        "Japanese",
        False,
        [
            ('alpha', 0),
            ('pitch', 0),
            ('speaker', 'yuri'),
            ('speed', 2),
        ],
    )),

    ('zh', (
        "Chinese",
        True,
        [
            ('spk_id', 250),
        ],
    )),
]

VOICE_LOOKUP = dict(VOICE_CODES)


def _quote_all(input_string,
               *args, **kwargs):  # pylint:disable=unused-argument
    """NAVER Translate needs every character quoted."""
    return ''.join('%%%x' % ord(char) for char in input_string)


# These functions implement the obfuscation functions found at
# https://papago.naver.com/main.7909bf415016e805e81b.chunk.js under
# "obfuscate.ts".

def _swap(input_str, index):
    return input_str[index:] + input_str[0:index]

def _scramble(input_str):
    output_str = ''
    for c in input_str:
        ci = c.lower()
        if ci >= 'a' and ci <= 'm':
            output_str += chr(ord(c) + 13)
        elif ci >= 'n' and ci <= 'z':
            output_str += chr(ord(c) - 13)
        else:
            output_str += c
    return output_str

def _generate_data(input_str):
    extra = len(input_str) % 6

    if extra > 0:
        padded_str = input_str + ('a' * (6 - extra))
    else:
        padded_str = input_str
    
    base64ed = base64.b64encode(padded_str.encode('utf-8')).decode('utf-8')

    header = 'a'
    output = header + _swap(base64ed, ord(header[0]) % (len(base64ed) - 2) + 1)

    return _scramble(output)


class Naver(Service):
    """Provides a Service implementation for NAVER Translate."""

    __slots__ = []

    NAME = "NAVER Translate"

    TRAITS = [Trait.INTERNET]

    def desc(self):
        """Returns a static description."""

        return "NAVER Translate (%d voices)" % len(VOICE_CODES)

    def options(self):
        """Returns an option to select the voice."""

        return [
            dict(
                key='voice',
                label="Voice",
                values=[(key, description)
                        for key, (description, _, _) in VOICE_CODES],
                transform=lambda str: self.normalize(str)[0:2],
                default='ko',
                test_default='en'
            ),
        ]

    def run(self, text, options, path):
        """Downloads from Internet directly to an MP3."""

        _, is_cndic_api, config = VOICE_LOOKUP[options['voice']]

        if is_cndic_api:
            self.net_download(
                path,
                [
                    (
                        CNDIC_ENDPOINT,
                        dict(
                            CNDIC_CONFIG +
                            config +
                            [
                                ('text', subtext),
                            ]
                        )
                    )
                    for subtext in self.util_split(text, 250)
                ],
                require=dict(mime='audio/mpeg', size=256),
                custom_quoter=dict(text=_quote_all),
            )

        else:
            def process_subtext(output_mp3, subtext):
                param_str = json.dumps(dict(
                    config +
                    [
                        ('text', subtext),
                    ]
                ))
                resp = self.net_stream(
                    (
                        TRANSLATE_MKID,
                        {
                            'data': _generate_data(param_str)
                        }
                    ),
                    method='POST',
                )

                sound_id = json.loads(resp)['id']

                self.net_download(
                    output_mp3,
                    (
                        TRANSLATE_ENDPOINT + sound_id,
                        dict()
                    ),
                    require=dict(mime='audio/mpeg', size=256),
                    custom_quoter=dict(text=_quote_all),
                )

            subtexts = self.util_split(text, 250)

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
