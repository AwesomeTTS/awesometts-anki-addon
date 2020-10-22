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
GUI classes for AwesomeTTS
"""

from .common import (
    Action,
    Button,
    Filter,
    ICON,
    ICON_FILE
)

from .configurator import Configurator

from .generator import (
    BrowserGenerator,
    EditorGenerator,
)

from .stripper import BrowserStripper

from .templater import Templater

from .homescreen import makeDeckBrowserRenderContent
from .homescreen import makeLinkHandler

__all__ = [
    # common
    'Action',
    'Button',
    'Filter',
    'ICON',
    'ICON_FILE'

    # dialog windows
    'Configurator',
    'BrowserGenerator',
    'EditorGenerator',
    'BrowserStripper',
    'Templater',
    'makeDeckBrowserRenderContent'
    'makeLinkHandler'

]
