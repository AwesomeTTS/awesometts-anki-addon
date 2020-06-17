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
Service implementation for Duden
"""

from bs4 import BeautifulSoup
from html.parser import HTMLParser
from re import compile as re
from unicodedata import normalize as unicode_normalize
import urllib

from .base import Service
from .common import Trait

__all__ = ['Duden']


INPUT_MAXIMUM = 100

IGNORE_ARTICLES = ['der', 'das', 'die']


class Duden(Service):
    """
    Provides a Service-compliant implementation for Duden.
    """

    __slots__ = []

    NAME = "Duden"

    TRAITS = [Trait.INTERNET, Trait.DICTIONARY]

    def desc(self):
        """
        Returns a short, static description.
        """

        return "Duden (German only, single words and short phrases only)"

    def options(self):
        """
        Advertises German, but does not allow any configuration.
        """

        return [
            dict(
                key='voice',
                label="Voice",
                values=[('de', "German (de)")],
                transform=lambda value: (
                    'de' if self.normalize(value).startswith('de')
                    else value
                ),
                default='de',
            ),
        ]

    def modify(self, text):
        components = text.split(' ')
        if len(components) > 1:
            components_filtered = [x for x in components if x.lower() not in IGNORE_ARTICLES]
            components = components_filtered
        result = ' '.join(components)
        # is there a final comma ?
        if result[-1] == ',':
            result = result[0:-1]
        return result

    def run(self, text, options, path):
        """
        Search the dictionary, walk the returned articles, then download
        articles that look like a match, and find MP3s in those articles
        that match the original input.
        """

        assert options['voice'] == 'de', "Only German is supported."

        if len(text) > INPUT_MAXIMUM:
            raise IOError("Your input text is too long for Duden.")

        # step 1: do a search , which will lead to multiple results
        # =========================================================

        encoded_text = encoded_text = urllib.parse.quote(text)
        search_url = f'https://www.duden.de/suchen/dudenonline/{encoded_text}'

        self._logger.debug(f'opening search url {search_url}')

        payload = self.net_stream(search_url)
        soup = BeautifulSoup(payload, 'html.parser')

        # collect all the candidates, which look like this:
        # <a class="vignette__label" href="/rechtschreibung/Groesze"> <strong>Grö­ße</strong> </a>
        definition_entries = soup.find_all('a', {"class":'vignette__label'})
        definition_candidates = []
        for entry in definition_entries:
            definition_url = entry['href']
            definition_word = entry.find('strong').string
            definition_candidates.append({'url': definition_url, 'word': definition_word})
            self._logger.debug(f'found {entry}, definition_url: {definition_url} definition_word: {definition_word}')

        # step 2: identify the correct candidate
        # ======================================

        def process_candidate_definition(input):
            input = input.replace('\u00AD', '')
            return input

        self._logger.debug(f'found candidates: {definition_candidates}')
        # self._logger.debug(f"first entry: {definition_candidates[0]}  matches: {definition_candidates[0]['word'] == text} text={text}")

        # simple strategy, lower-cased words should match.
        correct_candidates = [x for x in definition_candidates if process_candidate_definition(x['word']) == text]
        if len(correct_candidates) == 0:
            error_message = f"Couldn't find definition for {text} on page {search_url}"
            raise IOError(error_message)

        # pick the first one
        candidate = correct_candidates[0]

        # step 3: open definition url
        # ===========================

        # build the final URL
        definition_url = 'https://www.duden.de' + candidate['url']
        self._logger.debug(f'opening definition_url: {definition_url}')

        payload = self.net_stream(definition_url)
        soup = BeautifulSoup(payload, 'html.parser')
        #print(payload)

        # step 4: download pronounciation mp3 file
        # ========================================

        sound_element = soup.find('a', {'class':'pronunciation-guide__sound'})
        if sound_element == None:
            error_message = f"Couldn't find pronunciation for word [{text}] on page {definition_url}"
            raise IOError(error_message)

        self._logger.debug(f'sound_element: {sound_element}')
        mp3_url = sound_element['href']

        self.net_download(path, mp3_url,
                        require=dict(mime='audio/mpeg'))
        return

