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
Bundling
"""

__all__ = ['Bundle']


class Bundle(object):  # exposes attributes, not methods, pylint:disable=R0903
    """
    Exposes a class that can be used for bundling some objects together.
    This can be used as an alternative to a dict, and will have a syntax
    that is cleaner and shorter.

    Example

        >>> from bundle import Bundle
        >>> things = Bundle(a=1, b=2, c=3)
        >>> things.a
        1
        >>> things.b
        2
        >>> things.c
        3
    """

    def __init__(self, **kwargs):
        """
        Make each of the named keyword arguments available as an
        attribute on the instance.
        """

        for key, value in kwargs.items():
            setattr(self, key, value)
