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
Interaction with the Anki reviewer

This module is mostly headless. It lives in the "gui" package, however,
because interacts with the GUI components of Anki and it also spawns
alert windows. It also may have more visual components in the future.
"""

import re

from BeautifulSoup import BeautifulSoup
from PyQt4.QtCore import Qt

from .common import key_event_combo

__all__ = ['Reviewer']

X_FOR_THIS_TAG_MSG = 'The "%s" %s specified by this tag does not exist:\n' \
                     "\n" \
                     "%s\n" \
                     "\n" \
                     "If you are using a different computer or have " \
                     "re-installed Anki/AwesomeTTS, you can recreate it in " \
                     "Tools > AwesomeTTS > Advanced."


# n.b. Previously, before playing handlers, these event handlers checked to
# make sure that 'not sound.hasSound()'. I am guessing that this was done
# because AwesomeTTS did not know how to properly deal with multiple sounds
# at the time and they would play simultaneously.
#
# FIXME. It is possible, I suppose, that people might have the exact same
# audio file on a card via a [sound:xxx] tag as they do as a <tts> template
# tag. We can probably detect this by seeing if two of the same hashed
# filename end up in the queue (and I say "filename" because one would be
# coming from the media directory and another would be coming from the cache
# directory). This would probably need to be fixed in the router by having the
# router examine whether the exact same hashed filename is in the Anki
# playback queue already or looking at any [sound:xxx] tags on the card before
# playing back the on-the-fly sound.
#
# A similar problem probably exists in reviewer_key_handler for folks who
# includes their question card template within their answer card template and
# whose tts_key_q == tts_key_a.
#
# Unfortunately, it looks like inspecting anki.sound.mplayerQueue won't work
# out on Windows because the path gets blown away by the temporary file
# creation code.
#
# ALTERNATIVELY, if examination of the tag or playback queue turns out to not
# work out so well, checking sound.hasSound() could become two checkbox
# options on the "On-the-Fly Mode" tab for both question and answer sides.
#
# TODO. Add a configuration option like this:
#
#     Questions / Fronts of Cards
#         [ ] Automatically play on-the-fly <tts> tags
#             [ ] ... unless a [sound] is present


class Reviewer(object):
    """
    Provides interaction for on-the-fly functionality and Anki's
    reviewer mode.
    """

    RE_LEGACY_TAGS = re.compile(
        r'\[\s*(\w?)\s*tts\s*:([^\[\]]+)',
        re.MULTILINE | re.IGNORECASE,
    )

    RE_ANSWER_DIVIDER = re.compile(
        # allows extra whitespace, optional quotes, and optional self-closing
        r'<\s*hr\s+id\s*=\s*.?\s*answer\s*.?\s*/?\s*>',
        re.IGNORECASE,
    )

    __slots__ = [
        '_addon',
        '_alerts',
        '_mw',
    ]

    def __init__(self, addon, alerts, mw):
        self._addon = addon
        self._alerts = alerts
        self._mw = mw

    def card_handler(self, state, card):
        """
        Examines the state the of the reviewer and whether automatic
        questions or answers are enabled, passing off to the internal
        playback method if so.
        """

        config = self._addon.config

        if state == 'question' and config['automatic_questions']:
            self._play_html('front', card.q(),
                            self._addon.player.otf_question, self._mw,
                            show_errors=config['automatic_questions_errors'])

        elif state == 'answer' and config['automatic_answers']:
            self._play_html('back', self._get_answer(card),
                            self._addon.player.otf_answer, self._mw,
                            show_errors=config['automatic_answers_errors'])

    def key_handler(self, key_event, state, card, replay_audio):
        """
        Examines the key event to see if the user has triggered one of
        the shortcut options.

        If we do not handle the key here, then it is passed through to
        the normal Anki Reviewer implementation.

        As a special case, if the user sets his/her shortcut to one of
        the built-in audio shorts (i.e. R, F5), will play ALL sounds,
        starting with the built-in ones.
        """

        if state not in ['answer', 'question']:
            return False

        combo = key_event_combo(key_event)
        if not combo:
            return False

        handled = False

        if combo in [Qt.Key_R, Qt.Key_F5]:
            replay_audio()
            handled = True

        question_combo = self._addon.config['tts_key_q']
        if question_combo and combo == question_combo:
            self._play_html('front', card.q(),
                            self._addon.player.otf_shortcut, self._mw)
            handled = True

        answer_combo = self._addon.config['tts_key_a']
        if state == 'answer' and answer_combo and combo == answer_combo:
            self._play_html('back', self._get_answer(card),
                            self._addon.player.otf_shortcut, self._mw)
            handled = True

        return handled

    def _get_answer(self, card):
        """
        Attempts to strip out the question side of the card in the blob
        of HTML we get as the "answer" HTML.

        This is done in three ways:
            - remove question HTML (verbatim)
            - remove question HTML (with any [sound:xxx] tags stripped),
              which is how Anki does {{FrontSide}} on the answer side
            - find any <hr id=answer> tag, and chop off anything leading
              up to the first such tag
        """

        question_html = card.q()

        answer_html = self.RE_ANSWER_DIVIDER.split(
            card.a().
            replace(question_html, '').
            replace(self._addon.strip.sounds.anki(question_html), ''),

            1,  # remove at most one segment in the event of multiple dividers
        ).pop().strip()

        self._addon.logger.debug("Reinterpreted answer HTML as:\n%s" % (
            "\n".join("<<< " + line for line in answer_html.split("\n"))
        ))

        return answer_html

    def _play_html(self, side, html, playback, parent, show_errors=True):
        """
        Read in the passed HTML, attempt to discover <tts> tags in it,
        and pass them to the router for processing.

        Additionally, old-style [GTTS], [TTS], and [ATTS] tags are
        detected and played back, e.g.

            - [GTTS:voice:text] or [TTS:g:voice:text] for Yandex (the
              "G" here is for Google TTS, but that service is no longer
              functional as of December 2015)
            - [TTS:espeak:voice:text] for eSpeak
        """

        assert side in ['front', 'back'], "invalid 'side' passed"
        from_template = (self._addon.strip.from_template_back if side == 'back'
                         else self._addon.strip.from_template_front)

        # when running in review mode, avoid doing playback of a card that is
        # no longer on-screen

        skip_check = True
        try:
            parent_state = parent.state
            reviewer_state = parent.reviewer.state
            card_id = parent.reviewer.card.id
        except AttributeError:
            pass
        else:
            skip_check = False

        def playback_wrapper(*args, **kwargs):
            """Play audio contingent on matching state."""

            if skip_check:
                self._addon.logger.info("No previous state; playing audio")
                playback(*args, **kwargs)

            elif (parent_state == parent.state and
                  reviewer_state == parent.reviewer.state and
                  card_id == parent.reviewer.card.id):
                self._addon.logger.info("Previous state same; playing audio")
                playback(*args, **kwargs)

            else:
                self._addon.logger.warn("State changed; not playing audio")

        try:
            tags = BeautifulTTS(html)('tts')
        except ValueError:
            if '<tts' in html:
                self._alerts("The TTS cannot be played on this card because "
                             "the HTML cannot be parsed (is it valid?)")
            return

        for tag in tags:
            self._play_html_tag(tag, from_template, playback_wrapper,
                                parent, show_errors)

        for legacy in self.RE_LEGACY_TAGS.findall(html):
            self._play_html_legacy(legacy, from_template, playback_wrapper,
                                   parent, show_errors)

    def _play_html_tag(self, tag, from_template, playback, parent,
                       show_errors=True):
        """Helper method for _play_html()."""

        text = from_template(unicode(tag))
        if not text:
            return

        attr = dict(tag.attrs)
        config = self._addon.config

        if 'group' in attr:
            try:
                group = lax_dict_lookup(config['groups'], attr['group'])
            except KeyError:
                if show_errors:
                    self._alerts(
                        X_FOR_THIS_TAG_MSG % (attr['group'], "group",
                                              tag.prettify().decode('utf-8')),
                        parent,
                    )
            else:
                self._addon.router.group(
                    text=text,
                    group=group,
                    presets=config['presets'],
                    callbacks=dict(
                        okay=playback,
                        fail=lambda exception: (
                            isinstance(exception,
                                       self._addon.router.BusyError) or
                            not show_errors or
                            self._alerts(
                                "Unable to play this group tag:\n%s\n\n%s" % (
                                    tag.prettify().decode('utf-8').strip(),
                                    exception.message,
                                ),
                                parent,
                            )
                        ),
                    ),
                )
            return

        if 'preset' in attr:
            try:
                attr = dict(lax_dict_lookup(config['presets'], attr['preset']))
            except KeyError:
                if show_errors:
                    self._alerts(
                        X_FOR_THIS_TAG_MSG % (attr['preset'], "preset",
                                              tag.prettify().decode('utf-8')),
                        parent,
                    )
                return

        try:
            svc_id = attr.pop('service')
        except KeyError:
            if show_errors:
                self._alerts(
                    "This tag needs a 'service' attribute:\n%s" %
                    tag.prettify().decode('utf-8'),
                    parent,
                )
            return

        self._addon.router(
            svc_id=svc_id,
            text=text,
            options=attr,
            callbacks=dict(
                okay=playback,
                fail=lambda exception: (
                    # we can safely ignore "service busy" errors in review
                    isinstance(exception, self._addon.router.BusyError) or
                    not show_errors or
                    self._alerts(
                        ("Unable to play this tag:\n%s\n\n%s\n\n"
                         "If you want AwesomeTTS to automatically fallback to "
                         "a non-dictionary service when audio is not "
                         "available, you can setup an in-order playback "
                         "group. Go to Tools > AwesomeTTS > Advanced > "
                         "Service Presets and Groups for more information."
                         if self._addon.router.has_trait(svc_id, 'DICTIONARY')
                         else "Unable to play this tag:\n%s\n\n%s")
                        % (
                            tag.prettify().decode('utf-8').strip(),
                            exception.message,
                        ),
                        parent,
                    )
                ),
            ),
        )

    def _play_html_legacy(self, legacy, from_template, playback, parent,
                          show_errors=True):
        """Helper method for _play_html()."""

        components = legacy[1].split(':')

        if legacy[0] and legacy[0].strip().lower() == 'g':
            if len(components) < 2:
                if show_errors:
                    self._play_html_legacy_bad(
                        legacy,
                        "Old-style GTTS bracket tags must specify the "
                        "voice, e.g. [GTTS:es:hola], [GTTS:es:{{Front}}], "
                        "[GTTS:en:{{text:Back}}]",
                        parent,
                    )
                return

            svc_id = 'yandex'

        else:
            if len(components) < 3:
                if show_errors:
                    self._play_html_legacy_bad(
                        legacy,
                        "Old-style TTS bracket tags must specify service and "
                        "voice, e.g. [TTS:g:es:mundo], [TTS:g:es:{{Front}}], "
                        "[TTS:g:en:{{text:Back}}]",
                        parent,
                    )
                return

            svc_id = components.pop(0)

        voice = components.pop(0)

        text = ':'.join(components)
        text = from_template(text)
        if not text:
            return

        self._addon.router(
            svc_id=svc_id,
            text=text,
            options={'voice': voice},
            callbacks=dict(
                okay=playback,
                fail=lambda exception: (
                    isinstance(exception, self._addon.router.BusyError) or
                    not show_errors or
                    self._play_html_legacy_bad(legacy, exception.message,
                                               parent)
                ),
            ),
        )

    def _play_html_legacy_bad(self, legacy, message, parent):
        """Reassembles the legacy given tag and displays an alert."""

        self._alerts(
            "Unable to play this tag:\n[%sTTS:%s]\n\n%s" %
            (legacy[0], legacy[1], message),
            parent,
        )

    def selection_handler(self, text, preset, parent):
        """Play the selected text using the preset."""

        self._addon.router(
            svc_id=preset['service'],
            text=text,
            options=preset,
            callbacks=dict(
                okay=self._addon.player.menu_click,
                fail=lambda exception: (
                    isinstance(exception, self._addon.router.BusyError) or
                    self._alerts(exception.message, parent)
                ),
            ),
        )

    def selection_handler_group(self, text, group, parent):
        """Play the selected text using the group."""

        self._addon.router.group(
            text=text,
            group=group,
            presets=self._addon.config['presets'],
            callbacks=dict(
                okay=self._addon.player.menu_click,
                fail=lambda exception: (
                    isinstance(exception, self._addon.router.BusyError) or
                    self._alerts(exception.message, parent)
                ),
            ),
        )

    def nonselection_handler(self, state, card, parent):
        """Play on-the-fly text from the specified card side."""

        if state == 'question':
            self._play_html('front', card.q(),
                            self._addon.player.menu_click, parent)

        elif state == 'answer':
            self._play_html('back', self._get_answer(card),
                            self._addon.player.menu_click, parent)

    def has_tts(self, state, card):
        """
        Does a relatively fast, but inaccurate, check to see if the
        specified card side might have playable TTS on it.
        """

        html = (card.q() if state == 'question'
                else self._get_answer(card) if state == 'answer'
                else None)

        return html and ('<tts' in html or self.RE_LEGACY_TAGS.search(html))


class BeautifulTTS(BeautifulSoup):  # pylint:disable=abstract-method
    """
    Provides a customized version of the BeautifulSoup parser that
    treats TTS tags as nestable.
    """

    NESTABLE_TAGS = dict(BeautifulSoup.NESTABLE_TAGS.items() +
                         [('tts', [])])


def lax_dict_lookup(src, key, return_none=False):
    """
    Try to get a value out of the passed source dict with the passed
    key. If unsuccessful, normalize the keys and try again.

    Raises KeyError if both attempts fail, unless return_none is set.
    """

    try:
        return src[key]
    except KeyError:
        try:
            key = key.strip().lower()
            return next(v for k, v in src.items() if k.strip().lower() == key)
        except StopIteration:
            if return_none:
                return None
            else:
                raise KeyError
