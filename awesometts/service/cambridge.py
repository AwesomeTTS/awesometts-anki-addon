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

    def reset(self):
        HTMLParser.reset(self)
        self.sounds = []

    def handle_starttag(self, tag, attrs):
        class_name = 'circle circle-btn sound audio_play_button'
        if tag == "span" and ('class', class_name) in attrs:
            source_links = [
                value for attr, value in attrs
                if attr == 'data-src-mp3'
            ]
            self.sounds.extend(source_links)


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

        parser = CambridgeLister()
        parser.feed(html_payload.decode('utf-8'))
        parser.close()

        if options['voice'] == 'en-US':
            pron_lang = 'us_pron'
        else:
            pron_lang = 'uk_pron'

        if len(parser.sounds) > 0:
            for link in list(set(parser.sounds)):
                if re.search(pron_lang, link):
                    sound_url = 'https://dictionary.cambridge.org' + link
                    break

            self.net_download(
                path,
                sound_url,
                add_padding=True,
                require=dict(mime='audio/mpeg', size=1024),
            )
            parser.reset()
