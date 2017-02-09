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
Service implementation for Yandex.Translate's text-to-speech API
"""

from .base import Service
from .common import Trait

__all__ = ['Yandex']


class Yandex(Service):
    """
    Provides a Service-compliant implementation for Yandex.Translate.
    """

    __slots__ = [
    ]

    NAME = "Yandex.Translate"

    TRAITS = [Trait.INTERNET]

    _VOICE_CODES = {
        # n.b. The aliases code below assumes that no languages have any
        # variants and is therefore safe to always alias to the full
        # code from the two-character language code. If, in the future,
        # there are two kinds of any particular language, the alias list
        # logic will have to be reworked.

        'ar_AE': "Arabic", 'ca_ES': "Catalan", 'cs_CZ': "Czech",
        'da_DK': "Danish", 'de_DE': "German", 'el_GR': "Greek",
        'en_GB': "English, British", 'es_ES': "Spanish, European",
        'fi_FI': "Finnish", 'fr_FR': "French", 'it_IT': "Italian",
        'nl_NL': "Dutch", 'no_NO': "Norwegian", 'pl_PL': "Polish",
        'pt_PT': "Portuguese, European", 'ru_RU': "Russian",
        'sv_SE': "Swedish", 'tr_TR': "Turkish",
    }

    def desc(self):
        """
        Returns a short, static description.
        """

        return "Yandex.Translate text-to-speech web API " \
            "(%d voices)" % len(self._VOICE_CODES)

    def options(self):
        """
        Provides access to voice and quality.
        """

        voice_lookup = dict([
            # two-character language codes
            (self.normalize(code[:2]), code)
            for code in self._VOICE_CODES.keys()
        ] + [
            # aliases for Spanish, European
            (self.normalize(alias), 'es_ES')
            for alias in ['es_EU']
        ] + [
            # aliases for English, British
            (self.normalize(alias), 'en_GB')
            for alias in ['en_EU', 'en_UK']
        ] + [
            # aliases for Portuguese, European
            (self.normalize(alias), 'pt_PT')
            for alias in ['pt_EU']
        ] + [
            # then add/override for full names (e.g. Spanish, European)
            (self.normalize(name), code)
            for code, name in self._VOICE_CODES.items()
        ] + [
            # then add/override for shorter names (e.g. Spanish)
            (self.normalize(name.split(',')[0]), code)
            for code, name in self._VOICE_CODES.items()
        ] + [
            # then add/override for official voices (e.g. es_ES)
            (self.normalize(code), code)
            for code in self._VOICE_CODES.keys()
        ])

        def transform_voice(value):
            """Normalize and attempt to convert to official code."""

            normalized = self.normalize(value)
            if normalized in voice_lookup:
                return voice_lookup[normalized]

            return value

        return [
            dict(
                key='voice',
                label="Voice",
                values=[(code, "%s (%s)" % (name, code.replace('_', '-')))
                        for code, name in sorted(self._VOICE_CODES.items())],
                transform=transform_voice,
            ),
            dict(
                key='quality',
                label="Quality",
                values=[
                    ('lo', 'low'),
                    ('hi', 'high'),
                ],
                default='hi',
                transform=lambda value: value.lower().strip()[:2],
            ),
        ]

    def run(self, text, options, path):
        """
        Downloads from Yandex directly to an MP3.
        """

        self.net_download(
            path,
            [
                ('http://tts.voicetech.yandex.net/tts', dict(
                    format='mp3',
                    quality=options['quality'],
                    lang=options['voice'],
                    text=subtext,
                ))

                # n.b. limit seems to be much higher than 750, but this is
                # a safe place to start (the web UI limits the user to 100)
                for subtext in self.util_split(text, 750)
            ],
            require=dict(mime='audio/mpeg', size=1024),
            add_padding=True,
        )
