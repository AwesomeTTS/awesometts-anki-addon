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
Service implementation for Howjsay
"""

from .base import Service
from .common import Trait

__all__ = ['Howjsay']


class Howjsay(Service):
    """
    Provides a Service-compliant implementation for Howjsay.
    """

    __slots__ = [
    ]

    NAME = "Howjsay"

    TRAITS = [Trait.INTERNET, Trait.DICTIONARY]

    def __init__(self, *args, **kwargs):
        super(Howjsay, self).__init__(*args, **kwargs)

    def desc(self):
        """
        Returns a short, static description.
        """

        return "Howjsay (English only, single words and short phrases only)"

    def options(self):
        """
        Advertises English, but does not allow any configuration.
        """

        return [
            dict(
                key='voice',
                label="Voice",
                values=[
                    ('en', "English (en)"),
                ],
                transform=lambda value: (
                    'en' if self.normalize(value).startswith('en')
                    else value
                ),
                default='en',
            ),
        ]

    def modify(self, text):
        """
        Approximate all accented characters as ASCII ones and then drop
        non-alphanumeric characters (except certain symbols).
        """

        return ''.join(
            char
            for char in self.util_approx(text)
            if char.isalpha() or char.isdigit() or char in " '-.@"
        ).lower().strip()

    def run(self, text, options, path):
        """
        Downloads from howjsay.com directly to an MP3.
        """

        assert options['voice'] == 'en', "Only English is supported"

        if len(text) > 100:
            raise IOError("Input text is too long for Howjsay")

        from urllib.parse import quote

        try:
            self.net_download(
                path,
                'http://www.howjsay.com/mp3/' + quote(text) + '.mp3',
                require=dict(mime='audio/mpeg', size=512),
            )

        except (ValueError, IOError) as error:
            if getattr(error, 'code', None) == 404 or \
                    getattr(error, 'got_mime', None) == 'text/html':
                raise IOError(
                    "Howjsay does not have recorded audio for this phrase. "
                    "While most words have recordings, most phrases do not."
                    if text.count(' ')
                    else "Howjsay does not have recorded audio for this word."
                )
            else:
                raise
