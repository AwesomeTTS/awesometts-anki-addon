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

TRANSLATE_INIT = 'http://translate.naver.com/getVcode.dic'
TRANSLATE_ENDPOINT = 'http://translate.naver.com/tts'
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
                """Request a vcode and download the MP3."""

                vcode = self.net_stream(
                    (TRANSLATE_INIT, dict(text=subtext)),
                    method='POST',
                ).decode()
                vcode = ''.join(char for char in vcode if char.isdigit())

                self.net_download(
                    output_mp3,
                    (
                        TRANSLATE_ENDPOINT,
                        dict(
                            TRANSLATE_CONFIG +
                            config +
                            [
                                ('text', subtext),
                                ('vcode', vcode),
                            ]
                        ),
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
