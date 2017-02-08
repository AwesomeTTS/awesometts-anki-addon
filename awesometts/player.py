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
Playback interface, providing user-configured delays
"""

import inspect

from .text import RE_FILENAMES

__all__ = ['Player']


class Player(object):
    """Once instantiated, provides interfaces for playing audio."""

    __slots__ = [
        '_anki',    # bundle with mw, native (play function), sound (module)
        '_blank',   # path to a blank 1-second MP3
        '_config',  # dict-like interface for looking up user configuration
        '_logger',  # logger-like interface for debugging the Player instance
    ]

    def __init__(self, anki, blank, config, logger=None):
        self._anki = anki
        self._blank = blank
        self._config = config
        self._logger = logger

    def preview(self, path):
        """Play path with no delay, from preview button."""

        self._insert_blanks(0, "preview mode", path)
        self._anki.native(path)

    def menu_click(self, path):
        """Play path with no delay, from context menu."""

        self._insert_blanks(0, "context menu", path)
        self._anki.native(path)

    def otf_question(self, path):
        """
        Plays path after the configured 'delay_questions_onthefly'
        seconds.
        """

        self._insert_blanks(self._config['delay_questions_onthefly'],
                            "on-the-fly automatic question",
                            path)
        self._anki.native(path)

    def otf_answer(self, path):
        """
        Plays path after the configured 'delay_answers_onthefly'
        seconds.
        """

        self._insert_blanks(self._config['delay_answers_onthefly'],
                            "on-the-fly automatic answer",
                            path)
        self._anki.native(path)

    def otf_shortcut(self, path):
        """Play path with no delay."""

        self._insert_blanks(0, "on-the-fly shortcut", path)
        self._anki.native(path)

    def native_wrapper(self, path):
        """
        Provides a function that can be used as a wrapper around the
        native Anki playback interface. This is used in order to impose
        playback delays on [sound] tags while in review mode.
        """

        if self._anki.mw.state != 'review':
            self._insert_blanks(0, "wrapped, non-review", path)

        elif next((True
                   for frame in inspect.stack()
                   if frame[3] in self.native_wrapper.BLACKLISTED_FRAMES),
                  False):
            self._insert_blanks(0, "wrapped, blacklisted caller", path)

        elif self._anki.mw.reviewer.state == 'question':
            if RE_FILENAMES.search(path):
                self._insert_blanks(
                    self._config['delay_questions_stored_ours'],
                    "wrapped, AwesomeTTS sound on question side",
                    path,
                )

            else:
                self._insert_blanks(
                    self._config['delay_questions_stored_theirs'],
                    "wrapped, non-AwesomeTTS sound on question side",
                    path,
                )

        elif self._anki.mw.reviewer.state == 'answer':
            if RE_FILENAMES.search(path):
                self._insert_blanks(
                    self._config['delay_answers_stored_ours'],
                    "wrapped, AwesomeTTS sound on answer side",
                    path,
                )

            else:
                self._insert_blanks(
                    self._config['delay_answers_stored_theirs'],
                    "wrapped, non-AwesomeTTS sound on answer side",
                    path,
                )

        else:
            self._insert_blanks(0, "wrapped, unknown review state", path)

        self._anki.native(path)

    native_wrapper.BLACKLISTED_FRAMES = [
        'addMedia',     # if the user adds media in review
        'replayAudio',  # if the user strikes R or F5
    ]

    def _insert_blanks(self, seconds, reason, path):
        """
        Insert silence of the given seconds, unless Anki's queue has
        items in it already.
        """

        if self._anki.sound.mplayerQueue:
            if self._logger:
                self._logger.debug("Ignoring %d-second delay (%s) because of "
                                   "queue: %s", seconds, reason, path)
            return

        if self._logger:
            self._logger.debug("Need %d-second delay (%s): %s",
                               seconds, reason, path)
        for _ in range(seconds):
            self._anki.native(self._blank)
