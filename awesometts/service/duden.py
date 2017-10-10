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

from .base import Service
from .common import Trait

__all__ = ['Duden']


INPUT_MAXIMUM = 100
IGNORE_ARTICLES = ['der', 'das', 'die']
CASE_MATTERS = ['Weg']

SEARCH_FORM = 'http://www.duden.de/suchen/dudenonline'
RE_DETAIL = re(r'href="(https?://www\.duden\.de/rechtschreibung/(.+?))"')
RE_MP3 = re(r'(Betonung:|Bei der Schreibung) .*?'
            r'(<em>|&raquo;)(.+?)(</em>|&laquo;).+?'
            r'<a .*? href="(https?://www\.duden\.de/_media_/audio/.+?\.mp3)"')

HTML_PARSER = HTMLParser()


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
        """
        Modifies the input text as follows:

        1. drops characters that are not alphabetic, spaces, or dashes
        2. ASCIIizes any eszett (i.e. to "sz") and any vowel with
           umlauts (e.g. a-umlaut to "ae")
        3. extra whitespace around each word is dropped
        4. for each word, strip any leading or trailing dash (e.g.
           "ueber-" becomes just "ueber")
        5. any word that is entirely dashes is dropped
        6. for each word, unless it is an uppercase word where being
           uppercase matters (e.g. "Weg" instead of "weg", see
           `CASE_MATTERS`), lowercase it
        7. if the input is at least two words long and the first word
           is one of the articles that a user might use on a note to
           indicate gender (i.e. nominative definite articles, see
           `IGNORE_ARTICLES`), remove it
        """

        text = ''.join('Ae' if char == '\u00c4'
                       else 'Oe' if char == '\u00d6'
                       else 'Ue' if char == '\u00dc'
                       else 'sz' if char == '\u00df'
                       else 'ae' if char == '\u00e4'
                       else 'oe' if char == '\u00f6'
                       else 'ue' if char == '\u00fc'
                       else char
                       for char in text
                       if char.isalpha() or char == ' ' or char == '-')

        words = text.split()
        words = [word.strip('-') for word in words]
        words = [word if word in CASE_MATTERS else word.lower()
                 for word in words if word]

        if not words:
            return ''

        if len(words) > 1 and words[0] in IGNORE_ARTICLES:
            words.pop(0)

            # special case: if because the first word was an article, we know
            # that the next word *should* be a noun, and if by capitalizing it
            # we realize it is a case-matters noun, make it capitalized (this
            # makes, e.g., an input of "der weg" become "Weg")
            first_word_capitalized = words[0].capitalize()
            if first_word_capitalized in CASE_MATTERS:
                words[0] = first_word_capitalized

        text = ' '.join(words)

        return text

    def run(self, text, options, path):
        """
        Search the dictionary, walk the returned articles, then download
        articles that look like a match, and find MP3s in those articles
        that match the original input.
        """

        assert options['voice'] == 'de', "Only German is supported."

        if len(text) > INPUT_MAXIMUM:
            raise IOError("Your input text is too long for Duden.")

        try:
            text.encode('us-ascii')
        except UnicodeEncodeError:
            raise IOError("Your input text uses characters that cannot be "
                          "accurately searched for in the Duden.")

        text_search = text.replace('sz', '\u00df')
        self._logger.debug('Duden: Searching on "%s"', text_search)
        try:
            search_html = self.net_stream((SEARCH_FORM, dict(s=text_search)),
                                          require=dict(mime='text/html')).decode()
        except IOError as io_error:
            if getattr(io_error, 'code', None) == 404:
                raise IOError("Duden does not recognize this input.")
            else:
                raise

        text_lower = text.lower()
        text_lower_underscored_trailing = text_lower. \
            replace(' ', '_').replace('-', '_') + '_'
        text_compressed = text.replace(' ', '').replace('-', '')
        text_lower_compressed = text_compressed.lower()
        text_deumlauted_compressed = text_compressed.replace('ae', 'a'). \
            replace('oe', 'o').replace('ue', 'u')
        self._logger.debug('Got a search response; will follow links whose '
                           'lowercased+compressed article segment equals "%s" '
                           'or whose lowercased-but-still-underscored article '
                           'segment begins with "%s"; looking for MP3s whose '
                           'compressed guide says "%s" or "%s"',
                           text_lower_compressed,
                           text_lower_underscored_trailing,
                           text_compressed,
                           text_deumlauted_compressed)

        seen_article_urls = {}

        for article_match in RE_DETAIL.finditer(search_html):
            article_url = article_match.group(1)

            if article_url in seen_article_urls:
                continue
            seen_article_urls[article_url] = True

            segment = article_match.group(2)
            segment_lower = segment.lower()
            segment_lower_compressed = segment_lower.replace('_', '')

            if segment_lower_compressed == text_lower_compressed:
                self._logger.debug('Duden: lowered+compressed article segment '
                                   'for %s are same ("%s")',
                                   article_url, segment_lower_compressed)

            elif segment_lower.startswith(text_lower_underscored_trailing):
                self._logger.debug('Duden: lowered segment "%s" for %s begins '
                                   'with "%s"',
                                   segment_lower, article_url,
                                   text_lower_underscored_trailing)

            else:
                self._logger.debug('Duden: article segment for %s does not '
                                   'match; skipping', article_url)
                continue

            article_html = self.net_stream(article_url).decode()

            for mp3_match in RE_MP3.finditer(article_html):
                guide = mp3_match.group(3)
                guide = ''.join(HTML_PARSER.unescape(node)
                                for node
                                in BeautifulSoup(guide, 'html.parser').findAll(text=True))
                guide_normalized = unicode_normalize(
                    'NFKD',
                    self.modify(guide).replace('-', '').replace(' ', ''),
                ).encode('ASCII', 'ignore').decode()

                mp3_url = mp3_match.group(5)

                if guide_normalized == text_compressed or \
                        guide_normalized == text_deumlauted_compressed:

                    self._logger.debug('Duden: found MATCHING MP3 at %s for '
                                       '"%s", which normalized to "%s" and '
                                       'matches our input',
                                       mp3_url, guide, guide_normalized)

                    self.net_download(path, mp3_url,
                                      require=dict(mime='audio/mpeg'))
                    return

                else:
                    self._logger.debug('Duden: found non-matching MP3 at %s '
                                       'for "%s", which normalized to "%s" '
                                       'and does not match our input',
                                       mp3_url, guide, guide_normalized)

        raise IOError("Duden does not have recorded audio for this word.")
