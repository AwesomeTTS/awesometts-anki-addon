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
Common classes for services

Provides an enum-like Trait class for specifying the characteristics of
a service.
"""

__all__ = ['Trait']


class Trait(object):  # enum class, pylint:disable=R0903
    """
    Provides an enum-like namespace with codes that describe how a
    service works, used by concrete Service classes' TRAITS lists.

    The framework can query the registered Service classes to alter
    on-screen descriptions (e.g. inform the user which services make use
    of the LAME transcoder) or alter behavior (e.g. throttling when
    recording many media files from an online service).
    """

    INTERNET = 1     # files retrieved from Internet; use throttling
    TRANSCODING = 2  # LAME transcoder is used
    DICTIONARY = 4   # for services that have limited vocabularies
