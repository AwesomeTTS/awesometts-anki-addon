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
Service implementation for Cambridge Dictionary
"""

import re
from html.parser import HTMLParser
from urllib.parse import quote

from .base import Service
from .common import Trait

__all__ = ['Cambridge']


class CambridgeLister(HTMLParser):
    """Accumulate all found MP3s into `sounds` member."""

    def __init__(self, initial_class):
        self.initial_class = initial_class # should be something like 'uk dpron-i' for UK, or 'us dpron-i' for US
        self.capture_sound = False
        self.sound_file = None
        super().__init__()

    def reset(self):
        HTMLParser.reset(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'span' and len(attrs) == 1 and attrs[0] == ('class', self.initial_class):
            #print(f'*** found wanted initial class span, attrs: {attrs}')
            self.capture_sound = True
        if tag == 'source' and self.capture_sound and attrs[0] == ('type', 'audio/mpeg'):
            #print(f'found tag source: attrs: {attrs}')
            (tag_key, sound_file) = attrs[1]
            self.sound_file = sound_file
            self.capture_sound = False

class Cambridge(Service):
    """
    Provides a Service-compliant implementation for Cambridge Dictionary.
    """

    __slots__ = []

    NAME = "Cambridge Dictionary"

    TRAITS = [Trait.INTERNET]

    def desc(self):
        """
        Returns a short, static description.
        """

        return "Cambridge Dictionary (British and American English)"

    def options(self):
        """
        Provides access to voice.
        """

        voice_lookup = dict([
            # aliases for English, American
            (self.normalize(alias), 'en-US')
            for alias in ['American', 'American English', 'English, American',
                          'US']
        ] + [
            # aliases for English, British ("default" for the OED)
            (self.normalize(alias), 'en-GB')
            for alias in ['British', 'British English', 'English, British',
                          'English', 'en', 'en-EU', 'en-UK', 'EU', 'GB', 'UK']
        ])

        def transform_voice(value):
            """Normalize and attempt to convert to official code."""

            normalized = self.normalize(value)
            if normalized in voice_lookup:
                return voice_lookup[normalized]
            return value

        return [
            dict(
                key='voice',
                label="Voice",
                values=[('en-US', "English, American (en-US)"),
                        ('en-GB', "English, British (en-GB)")],
                default='en-GB',
                transform=transform_voice,
            ),
        ]

    def run(self, text, options, path):
        """
        Downloads from Cambridge Dictionary directly to an MP3.
        """

        dict_url = 'https://dictionary.cambridge.org/de/worterbuch/englisch/%s' % (
            quote(text.encode('utf-8'))
        )
        html_payload = self.net_stream(dict_url)

        if options['voice'] == 'en-US':
            initial_class = 'us dpron-i '
        else:
            initial_class = 'uk dpron-i '

        parser = CambridgeLister(initial_class)
        parser.feed(html_payload.decode('utf-8'))
        parser.close()

        if parser.sound_file != None:
            sound_url = 'https://dictionary.cambridge.org' + parser.sound_file
            #print(f'sound_url: {sound_url}')

            self.net_download(
                path,
                sound_url,
                add_padding=True,
                require=dict(mime='audio/mpeg', size=1024),
            )
            parser.reset()
        else:
            raise IOError(f"Could not extract audio for voice {options['voice']} from Cambridge dictionary on page {dict_url}. You can try the en-US voice.")
