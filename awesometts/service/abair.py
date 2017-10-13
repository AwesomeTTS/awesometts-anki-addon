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
Service implementation for abair.ie's Irish language synthesiser
"""

from re import compile as re_compile

from .base import Service
from .common import Trait

__all__ = ['Abair']


VOICES = [('gd', "Gweedore"), ('cm_V2', "Connemara"), ('hts', "Connemara HTS"),
          ('ga_MU_nnc_exthts', "Dingle Pen. HTS")]

SPEEDS = ["Very slow", "Slower", "Normal", "Faster", "Very fast"]
DEFAULT_SPEED = "Normal"
assert DEFAULT_SPEED in SPEEDS

TEXT_LENGTH_LIMIT = 2000
FORM_ENDPOINT = 'http://www.abair.tcd.ie/index.php'
RE_FILENAME = re_compile(r'name="filestozip" type="hidden" value="([\d_]+)"')
AUDIO_URL = 'http://www.abair.tcd.ie/audio/%s.mp3'
REQUIRE_MP3 = dict(mime='audio/mpeg', size=256)


class Abair(Service):
    """Provides a Service-compliant implementation for abair.ie."""

    __slots__ = []

    NAME = "abair.ie"

    TRAITS = [Trait.INTERNET]

    def desc(self):
        """Returns a short, static description."""

        return "abair.ie's Irish language synthesiser"

    def options(self):
        """Provides access to voice and speed."""

        voice_lookup = {self.normalize(value): value for value, _ in VOICES}
        speed_lookup = {self.normalize(value): value for value in SPEEDS}

        return [
            dict(
                key='voice',
                label="Voice",
                values=VOICES,
                transform=lambda value: voice_lookup.get(self.normalize(value),
                                                         value),
            ),

            dict(
                key='speed',
                label="Speed",
                values=[(value, value) for value in SPEEDS],
                transform=lambda value: speed_lookup.get(self.normalize(value),
                                                         value),
                default=DEFAULT_SPEED,
            ),
        ]

    def run(self, text, options, path):
        """Find audio filename and then download it."""

        if len(text) > TEXT_LENGTH_LIMIT:
            raise IOError("abair.ie only supports input up to %d characters." %
                          TEXT_LENGTH_LIMIT)

        payload = self.net_stream(
            (
                FORM_ENDPOINT,
                dict(
                    input=text,
                    speed=options['speed'],
                    synth=options['voice'],
                ),
            ),
            method='POST',
        ).decode()

        match = RE_FILENAME.search(payload)
        if not match:
            raise IOError("Cannot find sound file in response from abair.ie")

        self.net_download(
            path,
            AUDIO_URL % match.group(1),
            require=REQUIRE_MP3,
        )
