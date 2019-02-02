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
import base64

from .base import Service
from .common import Trait

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

TRANSLATE_INIT = 'https://papago.naver.com/apis/tts/makeID'
TRANSLATE_ENDPOINT = 'https://papago.naver.com/apis/tts'
TRANSLATE_CONFIG = [
    ('from', 'translate'),
    ('service', 'translate'),
    ('speech_fmt', 'mp3'),
]

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
                """Request file id and download the MP3."""
                #Build Up provided by sjhuang26 @ https://github.com/AwesomeTTS/awesometts-anki-addon/issues/61
                prefix = b'\xaeU\xae\xa1C\x9b,Uzd\xf8\xef'
                speed = str(config[1][1]) if len(config) > 1 else '0'

                json = 'pitch":0,"speaker":"' + config[0][1].encode('utf-8') + '","speed": "' + speed + '","text":"' + subtext.encode('utf-8') + '"}'
                data = base64.b64encode(prefix + json)

                responseJson = self.net_stream(
                    (TRANSLATE_INIT, dict(data=data)),
                    method='POST',
                )
                import json
                id = json.loads(responseJson)['id']

                self.net_download(
                    output_mp3,
                    (
                        TRANSLATE_ENDPOINT + "/" + id
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
