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

        self._anki.native(path)

    def menu_click(self, path):
        """Play path with no delay, from context menu."""

        self._anki.native(path)


