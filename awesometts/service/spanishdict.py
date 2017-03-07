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
Service implementation for SpanishDict's text-to-speech API
"""

from .base import Service
from .common import Trait

__all__ = ['SpanishDict']


class SpanishDict(Service):
    """
    Provides a Service-compliant implementation for SpanishDict.
    """

    __slots__ = []

    NAME = "SpanishDict"

    TRAITS = [Trait.INTERNET]

    def desc(self):
        """
        Returns a short, static description.
        """

        return "SpanishDict.com (English and Spanish)"

    def options(self):
        """
        Provides access to voice only.
        """

        def transform_voice(value):
            """Returns normalized code if valid, otherwise value."""

            normalized = self.normalize(value)
            if len(normalized) > 2:
                normalized = normalized[0:2]

            return normalized if normalized in ['en', 'es'] else value

        return [
            dict(
                key='voice',
                label="Voice",
                values=[
                    ('en', "English (en)"),
                    ('es', "Spanish (es)"),
                ],
                transform=transform_voice,
                default='es',
            ),
        ]

    def run(self, text, options, path):
        """
        Downloads from SpanishDict directly to an MP3.
        """

        self.net_download(
            path,
            [
                ('https://audio1.spanishdict.com/audio', dict(
                    lang=options['voice'],
                    text=subtext,
                ))

                for subtext in self.util_split(text, 200)
            ],
            add_padding=True,
            require=dict(mime='audio/mpeg', size=1024),
        )
