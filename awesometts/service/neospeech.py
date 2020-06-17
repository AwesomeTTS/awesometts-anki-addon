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
Service implementation for NeoSpeech's text-to-speech demo engine
"""

import json
from threading import Lock

from .base import Service
from .common import Trait

__all__ = ['NeoSpeech']


VOICES = [('en-GB', 'male', "Hugh", 33), ('en-GB', 'female', "Bridget", 4),
          ('en-US', 'male', "James", 10), ('en-US', 'male', "Paul", 1),
          ('en-US', 'female', "Ashley", 14), ('en-US', 'female', "Beth", 35), ('en-US', 'female', "Julie", 3), ('en-US', 'female', "Kate", 2), 
		  ('de', 'male', "Tim", 44), ('de', 'female', "Lena", 43),											#Tim 44, Lena 43
		  ('fr-EU', 'male', "Louis", 50), ('fr-EU', 'female', "Roxane", 49),								#Louis 50, Roxane 49
		  ('fr-CA', 'female', "Chloe", 13), ('fr-CA', 'male', "Leo", 34), 									#Leo 34
		  ('es-EU', 'male', "Manuel", 46), ('es-EU', 'female', "Lola", 45),									#Manuel 46, Lola 45
		  ('es-MX', 'male', "Francisco", 31), ('es-MX', 'female', "Gloria", 32), ('es-MX', 'female', "Violeta", 5),
		  ('it', 'male', "Roberto", 48), ('it', 'female', "Elisa", 47),										#Roberto 48, Elisa 47
          ('pt-BR', 'male', "Rafael", 42), ('pt-BR', 'female', "Helena", 41),								#Rafael 42, Helena 41
		  ('ja', 'male', "Ryo", 28), ('ja', 'male', "Show", 8), ('ja', 'male', "Takeru", 30),
          ('ja', 'female', "Haruka", 26), ('ja', 'female', "Hikari", 29),
          ('ja', 'female', "Misaki", 9), ('ja', 'female', "Sayaka", 27),
          ('ko', 'male', "Jihun", 21), ('ko', 'male', "Junwoo", 6),
          ('ko', 'female', "Dayoung", 17), ('ko', 'female', "Hyeryun", 18),
          ('ko', 'female', "Hyuna", 19), ('ko', 'female', "Jimin", 20),
          ('ko', 'female', "Sena", 22), ('ko', 'female', "Yumi", 7),
          ('ko', 'female', "Yura", 23), ('zh', 'male', "Liang", 12),
          ('zh', 'male', "Qiang", 25), ('zh', 'female', "Hong", 24), ('zh', 'female', "Hui", 11),
		  ('zh-TW', 'female', "Yafang", 36),																#Yafang 36
		  ('zh-CA', 'male', "Kano", 37), ('zh-CA', 'female', "Kayan", 38),									#Kano 37, Kayan 38
		  ('th', 'male', "Sarawut", 39), ('th', 'female', "Somsi", 40),										#Sarawut 39, Somsi 40
		  ('aa', 'female', "Test51", 51), ('aa', 'male', "Test52", 52)]

MAP = {name: api_id for language, gender, name, api_id in VOICES}


BASE_URL = 'http://neospeech.com'

DEMO_URL = BASE_URL + '/service/demo'

REQUIRE_MP3 = dict(mime='audio/mpeg', size=256)


class NeoSpeech(Service):
    """
    Provides a Service-compliant implementation for NeoSpeech.
    """

    __slots__ = [
        '_lock',         # download URL is tied to cookie; force serial runs
        '_cookies',      # used for all NeoSpeech requests in this Anki session
        '_last_phrase',  # last subtext we sent to NeoSpeech
        '_last_stream',  # last download we got from NeoSpeech
    ]

    NAME = "NeoSpeech"

    TRAITS = [Trait.INTERNET]

    def __init__(self, *args, **kwargs):
        self._lock = Lock()
        self._cookies = None
        self._last_phrase = None
        self._last_stream = None
        super(NeoSpeech, self).__init__(*args, **kwargs)

    def desc(self):
        """Returns name with a voice count."""

        return "NeoSpeech Demo (%d voices)" % len(VOICES)

    def options(self):
        """Provides access to voice only."""

        voice_lookup = {self.normalize(name): name
                        for language, gender, name, api_id in VOICES}

        def transform_voice(value):
            """Fixes whitespace and casing errors only."""
            normal = self.normalize(value)
            return voice_lookup[normal] if normal in voice_lookup else value

        return [dict(key='voice',
                     label="Voice",
                     values=[(name, "%s (%s %s)" % (name, gender, language))
                             for language, gender, name, _ in VOICES],
                     transform=transform_voice)]

    def run(self, text, options, path):
        """Requests MP3 URLs and then downloads them."""

        with self._lock:
            if not self._cookies:
                headers = self.net_headers(BASE_URL)
                self._cookies = ';'.join(
                    cookie.split(';')[0]
                    for cookie in headers['Set-Cookie'].split(',')
                )
                self._logger.debug("NeoSpeech cookies are %s", self._cookies)
            headers = {'Cookie': self._cookies}

            voice_id = MAP[options['voice']]

            def fetch_piece(subtext, subpath):
                """Fetch given phrase from the API to the given path."""

                payload = self.net_stream((DEMO_URL, dict(content=subtext,
                                                          voiceId=voice_id)),
                                          custom_headers=headers)

                try:
                    data = json.loads(payload)
                except ValueError:
                    raise ValueError("Unable to interpret the response from "
                                     "the NeoSpeech service")

                try:
                    url = data['audioUrl']
                except KeyError:
                    raise KeyError("Cannot find the audio URL in the response "
                                   "from the NeoSpeech service")
                assert isinstance(url, str) and len(url) > 2 and \
                    url[0] == '/' and url[1].isalnum(), \
                    "The audio URL from NeoSpeech does not seem to be valid"

                mp3_stream = self.net_stream(BASE_URL + url,
                                             require=REQUIRE_MP3,
                                             custom_headers=headers)
                if self._last_phrase != subtext and \
                        self._last_stream == mp3_stream:
                    raise IOError("NeoSpeech seems to be returning the same "
                                  "MP3 file twice in a row; it may be having "
                                  "service problems.")
                self._last_phrase = subtext
                self._last_stream = mp3_stream
                with open(subpath, 'wb') as mp3_file:
                    mp3_file.write(mp3_stream)

            subtexts = self.util_split(text, 200)  # see `maxlength` on site
            if len(subtexts) == 1:
                fetch_piece(subtexts[0], path)
            else:
                intermediate_mp3s = []
                try:
                    for subtext in subtexts:
                        intermediate_mp3 = self.path_temp('mp3')
                        intermediate_mp3s.append(intermediate_mp3)
                        fetch_piece(subtext, intermediate_mp3)
                    self.util_merge(intermediate_mp3s, path)
                finally:
                    self.path_unlink(intermediate_mp3s)
