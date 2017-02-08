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
Service implementation for Oxford Dictionary
"""

import re
from HTMLParser import HTMLParser

from .base import Service
from .common import Trait

__all__ = ['Oxford']


RE_WHITESPACE = re.compile(r'[-\0\s_]+', re.UNICODE)

# n.b. The OED has words with periods (e.g. "Capt."), so we preserve those,
# but other punctuation can generally be dropped. The re.UNICODE flag here is
# important so that accented characters are not filtered out.
RE_DISCARD = re.compile(r'[^-.\s\w]+', re.UNICODE)


class OxfordLister(HTMLParser):
    """Accumulate all found MP3s into `sounds` member."""

    def reset(self):
        HTMLParser.reset(self)
        self.sounds = []
        self.prev_tag = ""

    def handle_starttag(self, tag, attrs):
        if tag == "audio" and self.prev_tag == "a":
            snd = [v for k, v in attrs if k == "src"]
            if snd:
                self.sounds.extend(snd)
        if tag == "a" and ("class", "speaker") in attrs:
            self.prev_tag = tag


class Oxford(Service):
    """
    Provides a Service-compliant implementation for Oxford Dictionary.
    """

    __slots__ = []

    NAME = "Oxford Dictionary"

    TRAITS = [Trait.INTERNET, Trait.DICTIONARY]

    def desc(self):
        """
        Returns a short, static description.
        """

        return "Oxford Dictionary (British and American English); " \
            "dictionary words only with fuzzy matching"

    def options(self):
        """
        Provides access to voice only.
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

    def modify(self, text):
        """
        OED generally represents words with spaces using a dash between
        the words. Case usually doesn't matter, but sometimes it does,
        so we do not normalize it (e.g. "United-Kingdom" works but
        "united-kingdom" does not).
        """

        return RE_WHITESPACE.sub('-', RE_DISCARD.sub('', text)).strip('-')

    def run(self, text, options, path):
        """
        Download wep page for given word
        Then extract mp3 path and download it
        """

        if len(text) > 100:
            raise IOError("Input text is too long for the Oxford Dictionary")

        from urllib2 import quote
        dict_url = 'https://en.oxforddictionaries.com/definition/%s%s' % (
            'us/' if options['voice'] == 'en-US' else '',
            quote(text.encode('utf-8'))
        )

        try:
            html_payload = self.net_stream(dict_url)
        except IOError as io_error:
            if getattr(io_error, 'code', None) == 404:
                raise IOError(
                    "The Oxford Dictionary does not recognize this phrase. "
                    "While most single words are recognized, many multi-word "
                    "phrases are not."
                    if text.count('-')
                    else "The Oxford Dictionary does not recognize this word."
                )
            else:
                raise

        parser = OxfordLister()
        parser.feed(html_payload.decode('utf-8'))
        parser.close()

        if len(parser.sounds) > 0:
            sound_url = parser.sounds[0]

            self.net_download(
                path,
                sound_url,
                require=dict(mime='binary/octet-stream', size=1024),
            )
        else:
            raise IOError(
                "The Oxford Dictionary does not currently seem to be "
                "advertising American English pronunciation. You may want to "
                "consider either using a different service or switching to "
                "British English."
                if options['voice'] == 'en-US'

                else
                "The Oxford Dictionary has no recorded audio for your input."
            )
