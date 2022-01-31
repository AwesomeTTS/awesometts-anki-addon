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
Basic manipulation and sanitization of input text
"""

import re
from io import StringIO

from bs4 import BeautifulSoup
import html
import anki

clozeReg = r"(?si)\{\{(?P<tag>c)%s::(?P<content>.*?)(::(?P<hint>.*?))?\}\}"

__all__ = ['RE_CLOZE_BRACED', 'RE_CLOZE_RENDERED', 'RE_ELLIPSES',
           'RE_ELLIPSES_LEADING', 'RE_ELLIPSES_TRAILING', 'RE_FILENAMES',
           'RE_HINT_LINK', 'RE_LINEBREAK_HTML', 'RE_NEWLINEISH', 'RE_SOUNDS',
           'RE_WHITESPACE', 'STRIP_HTML', 'Sanitizer']


RE_CLOZE_BRACED = re.compile(clozeReg % r'\d+')
RE_CLOZE_RENDERED = re.compile(
    # see anki.template.template.clozeText; n.b. the presence of the brackets
    # in the pattern means that this will only match and replace on the
    # question side of cards
    r'<span class=.?cloze.?>\[(.+?)\]</span>'
)
RE_ELLIPSES = re.compile(r'\s*(\.\s*){3,}')
RE_ELLIPSES_LEADING = re.compile(r'^\s*(\.\s*){3,}')
RE_ELLIPSES_TRAILING = re.compile(r'\s*(\.\s*){3,}$')
RE_FILENAMES = re.compile(r'([a-z\d]+(-[a-f\d]{8}){5}|ATTS .+)'
                          r'( \(\d+\))?\.mp3')
RE_HINT_LINK = re.compile(r'<a[^>]+class=.?hint.?[^>]*>[^<]+</a>')
RE_LINEBREAK_HTML = re.compile(r'<\s*/?\s*(br|div|p)(\s+[^>]*)?\s*/?\s*>',
                               re.IGNORECASE)
RE_NEWLINEISH = re.compile(r'(\r|\n|<\s*/?\s*(br|div|p)(\s+[^>]*)?\s*/?\s*>)+',
                           re.IGNORECASE)
RE_SOUNDS = re.compile(r'\[sound:(.*?)\]')  # see also anki.sound._soundReg
RE_WHITESPACE = re.compile(r'[\0\s]+', re.UNICODE)

STRIP_HTML = anki.utils.stripHTML  # this also converts character entities


class Sanitizer(object):  # call only, pylint:disable=too-few-public-methods
    """Once instantiated, provides a callable to sanitize text."""

    # _rule_xxx() methods are in-class for getattr, pylint:disable=no-self-use

    __slots__ = [
        '_config',  # dict-like interface for looking up config conditionals
        '_logger',  # logger-like interface for debugging the Sanitizer
        '_rules',   # list of rules that this instance's callable will process
    ]

    def __init__(self, rules, config=None, logger=None):
        self._rules = rules
        self._config = config
        self._logger = logger

    def __call__(self, text):
        """Apply the initialized rules against the text and return."""

        self._logger.debug(f'input text: [{text}]')

        applied = []

        for rule in self._rules:
            self._logger.debug(f'evaluating rule: {rule}')

            if not text:
                self._log(applied + ["early exit"], '')
                return ''

            if isinstance(rule, str):  # always run these rules
                applied.append(rule)
                text = getattr(self, '_rule_' + rule)(text)

            elif isinstance(rule, tuple):  # rule that depends on config
                try:
                    addl = rule[2]
                except IndexError:
                    addl = None
                key = rule[1]
                rule = rule[0]

                # if the "key" is actually a list, then we will return True
                # for `value` if ANY key in the list yields a truthy config
                value = (next((True for k in key if self._config[k]),
                              False) if isinstance(key, list)
                         else self._config[key])

                if value is True:  # basic on/off config flag
                    if addl:
                        addl = self._config[addl]
                        applied.append((rule, addl))
                        text = getattr(self, '_rule_' + rule)(text, addl)

                    else:
                        applied.append(rule)
                        text = getattr(self, '_rule_' + rule)(text)

                elif value:  # some other truthy value that drives the rule
                    if addl:
                        addl = self._config[addl]
                        applied.append((rule, value, addl))
                        text = getattr(self, '_rule_' + rule)(text, value,
                                                              addl)

                    else:
                        applied.append((rule, value))
                        text = getattr(self, '_rule_' + rule)(text, value)

            else:
                raise AssertionError("bad rule given to Sanitizer instance")

        self._log(applied, text)
        return text

    def _log(self, method, result):
        """If we have a logger, send debug line for transformation."""

        if self._logger:
            self._logger.debug("Transformation using %s: %s", method,
                               "(empty string)" if result == '' else result)

    def _rule_char_ellipsize(self, text, chars):
        """Ellipsizes given chars from the text."""

        return ''.join(
            ('...' if char in chars else char)
            for char in text
        )

    def _rule_char_remove(self, text, chars):
        """Removes given chars from the text."""

        return ''.join(char for char in text if char not in chars)

    def _rule_clozes_braced(self, text, mode):
        """
        Given a braced cloze placeholder in a note, examine the option
        mode and return an appropriate replacement.
        """

        return RE_CLOZE_BRACED.sub(
            '...' if mode == 'ellipsize'
            else '' if mode == 'remove'
            else self._rule_clozes_braced.wrapper if mode == 'wrap'
            else self._rule_clozes_braced.deleter if mode == 'deleted'
            else self._rule_clozes_braced.ankier,  # mode == 'anki'

            text,
        )

    _rule_clozes_braced.wrapper = lambda match: (
        '... %s ...' % match.group(4).strip('.') if (match.group(4) and
                                                     match.group(4).strip('.'))
        else '...'
    )

    _rule_clozes_braced.deleter = lambda match: (
        match.group(2) if match.group(2)
        else '...'
    )

    _rule_clozes_braced.ankier = lambda match: (
        match.group(4) if match.group(4)
        else '...'
    )

    def _rule_clozes_rendered(self, text, mode):
        """
        Given a rendered cloze HTML tag, examine the option mode and
        return an appropriate replacement.
        """

        return RE_CLOZE_RENDERED.sub(
            '...' if mode == 'ellipsize'
            else '' if mode == 'remove'
            else self._rule_clozes_rendered.wrapper if mode == 'wrap'
            else self._rule_clozes_rendered.ankier,  # mode == 'anki'

            text,
        )

    _rule_clozes_rendered.wrapper = lambda match: (
        '... %s ...' % match.group(1).strip('.')
        if match.group(1).strip('.')
        else match.group(1)
    )

    _rule_clozes_rendered.ankier = lambda match: match.group(1)

    def _rule_clozes_revealed(self, text):
        """
        Given text that has a revealed cloze span, return only the
        contents of that span.
        """

        revealed_tags = BeautifulSoup(text, features="html.parser")('span', attrs={'class': 'cloze'})

        return ' ... '.join(
            ''.join(
                str(content)
                for content in tag.contents
            )
            for tag in revealed_tags
        ) if revealed_tags else text

    def _rule_counter(self, text, characters, wrap):
        """
        Upon encountering the given characters, replace with the number
        of those characters that were encountered.
        """

        return re.sub(
            r'[' + re.escape(characters) + ']{2,}',

            self._rule_counter.wrapper if wrap
            else self._rule_counter.spacer,

            text,
        )

    _rule_counter.wrapper = lambda match: (' ... ' + str(len(match.group(0))) +
                                           ' ... ')

    _rule_counter.spacer = lambda match: (' ' + str(len(match.group(0))) + ' ')

    def _rule_custom_sub(self, text, rules):
        """
        Upon encountering text that matches one of the user's compiled
        rules, make a replacement. Run whitespace and ellipsis rules
        before each one.
        """

        self._logger.debug(f'running _rule_custom_sub')

        for rule in rules:
            self._logger.debug(f'evaluating {rule}')

            text = self._rule_whitespace(self._rule_ellipses(text))
            if not text:
                return ''

            text = rule['compiled'].sub(rule['replace'], text)
            if not text:
                return ''

        return text

    def _rule_ellipses(self, text):
        """
        Given at least three periods, separated by whitespace or not,
        collapse down to three consecutive periods padded on both sides.

        Additionally, drop any leading or trailing ellipses entirely.
        """

        text = RE_ELLIPSES.sub(' ... ', text)
        text = RE_ELLIPSES_LEADING.sub(' ', text)
        text = RE_ELLIPSES_TRAILING.sub(' ', text)
        return text

    def _rule_filenames(self, text):
        """
        Removes any filenames that appear to be from AwesomeTTS.
        """

        return RE_FILENAMES.sub('', text)

    def _rule_hint_content(self, text):
        """
        Removes hint content from the use of a {{hint:xxx}} field.
        """

        soup = BeautifulSoup(text, 'html.parser')
        hints = soup.findAll('div', attrs={'class': 'hint'})
        while hints:
            hints.pop().extract()

        return str(soup)

    def _rule_hint_links(self, text):
        """
        Removes hint links from the use of a {{hint:XXX}} field.
        """

        return RE_HINT_LINK.sub('', text)

    def _rule_html(self, text):
        """
        Removes any HTML, including converting character entities.
        """

        text = RE_LINEBREAK_HTML.sub(' ', text)
        return STRIP_HTML(text)

    def _rule_newline_ellipsize(self, text):
        """
        Replaces linefeeds, newlines, and things that look like that
        (e.g. paragraph tags, div containers) with an ellipsis.
        """

        return RE_NEWLINEISH.sub(' ... ', text)

    def _rule_sounds_ours(self, text):
        """
        Removes sound tags that appear to be from AwesomeTTS.
        """

        return RE_SOUNDS.sub(
            lambda match: (
                '' if RE_FILENAMES.match(match.group(1))
                else match.group(0)
            ),
            text,
        )

    def _rule_sounds_theirs(self, text):
        """
        Removes sound tags that appear to NOT be from AwesomeTTS.
        """

        return RE_SOUNDS.sub(
            lambda match: (
                match.group(0) if RE_FILENAMES.match(match.group(1))
                else ''
            ),
            text,
        )

    def _rule_sounds_univ(self, text):
        """
        Removes sound tags, regardless of origin.
        """

        return RE_SOUNDS.sub('', text)

    def _rule_whitespace(self, text):
        """
        Collapses all whitespace down to a single space and strips
        off any leading or trailing whitespace.
        """

        return RE_WHITESPACE.sub(' ', text).strip()

    def _rule_within_braces(self, text):
        """Removes text within curly braces."""
        return _aux_within(text, '{', '}')

    def _rule_within_brackets(self, text):
        """Removes text within square brackets."""
        return _aux_within(text, '[', ']')

    def _rule_within_parens(self, text):
        """Removes text within parentheses."""
        return _aux_within(text, '(', ')')

    def _rule_ruby_tags(self, text):
        self._logger.debug(f'looking for ruby tags')
        if 'ruby' in text:
            self._logger.debug(f'found ruby tags, processing')
            soup = BeautifulSoup(text, features="html.parser")
            rt_tags = soup.find_all('rt')
            for rt_tag in rt_tags:
                self._logger.debug(f'found rt tag {rt_tag}')
                rt_tag.string = ''
            return str(soup)
        return text

    def _rule_xml_entities(self, text):
        # not all html entities should be replaced, so we can maintain a map here
        SSML_CONVERSION_MAP ={
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '，': ',', # chinese comma
        }
        for pattern, replace in SSML_CONVERSION_MAP.items():
            text = text.replace(pattern, replace)        
        return text


def _aux_within(text, begin_char, end_char):
    """
    Removes any substring of text that starts with begin_char and
    ends with end_char.
    """

    changed = False
    result = StringIO()
    sequences = []

    for char in text:
        if char == begin_char:  # begins new level of text to possibly cut
            sequence = StringIO()
            sequence.write(char)
            sequences.append(sequence)

        elif char == end_char:
            if sequences:  # match the last opening char and cut this text
                changed = True
                sequences.pop().close()

            else:  # include closing chars w/o matching opening in result
                result.write(char)

        elif sequences:  # write regular chars to current sequence level
            sequences[-1].write(char)

        else:  # write top-level regular chars to the result
            result.write(char)

    if changed:  # replace passed text object with the buffer
        for sequence in sequences:  # include stuff lacking a closing char
            result.write(sequence.getvalue())
        text = result.getvalue()

    result.close()
    while sequences:
        sequences.pop().close()

    return text
