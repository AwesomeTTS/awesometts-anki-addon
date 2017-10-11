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
Service implementation for the iSpeech API
"""

from .base import Service

__all__ = ['ISpeech']


VOICES = {
    'auenglishfemale': ('en-AU', 'female'),
    'brportuguesefemale': ('pr-BR', 'female'),
    'caenglishfemale': ('en-CA', 'female'),
    'cafrenchfemale': ('fr-CA', 'female'),
    'cafrenchmale': ('fr-CA', 'male'),
    'chchinesefemale': ('zh-CMN', 'female'),
    'chchinesemale': ('zh-CMN', 'male'),
    'eurcatalanfemale': ('ca', 'female'),
    'eurczechfemale': ('cs', 'female'),
    'eurdanishfemale': ('da', 'female'),
    'eurdutchfemale': ('nl', 'female'),
    'eurfinnishfemale': ('fi', 'female'),
    'eurfrenchfemale': ('fr-FR', 'female'),
    'eurfrenchmale': ('fr-FR', 'male'),
    'eurgermanfemale': ('de', 'female'),
    'eurgermanmale': ('de', 'male'),
    'euritalianfemale': ('it', 'female'),
    'euritalianmale': ('it', 'male'),
    'eurnorwegianfemale': ('no', 'female'),
    'eurpolishfemale': ('pl', 'female'),
    'eurportuguesefemale': ('pt-PT', 'female'),
    'eurportuguesemale': ('pt-PT', 'male'),
    'eurspanishfemale': ('es-ES', 'female'),
    'eurspanishmale': ('es-ES', 'male'),
    'eurturkishfemale': ('tr', 'female'),
    'eurturkishmale': ('tr', 'male'),
    'hkchinesefemale': ('zh-YUE', 'female'),
    'huhungarianfemale': ('hu', 'female'),
    'jpjapanesefemale': ('jp', 'female'),
    'jpjapanesemale': ('jp', 'male'),
    'krkoreanfemale': ('ko', 'female'),
    'krkoreanmale': ('ko', 'male'),
    'rurussianfemale': ('ru', 'female'),
    'rurussianmale': ('ru', 'male'),
    'swswedishfemale': ('sv', 'female'),
    'twchinesefemale': ('zh-TW', 'female'),
    'ukenglishfemale': ('en-GB', 'female'),
    'ukenglishmale': ('en-GB', 'male'),
    'usenglishfemale': ('en-US', 'female'),
    'usenglishmale': ('en-US', 'male'),
    'usspanishfemale': ('es-US', 'female'),
    'usspanishmale': ('es-US', 'male'),
}


class ISpeech(Service):
    """
    Provides a Service-compliant implementation for iSpeech.
    """

    __slots__ = [
    ]

    NAME = "iSpeech"

    # Although iSpeech is an Internet service, we do not mark it with
    # Trait.INTERNET, as it is a paid-for-by-the-user API, and we do not want
    # to rate-limit it or trigger error caching behavior
    TRAITS = []

    def desc(self):
        """Returns name with a voice count."""

        return "iSpeech API (%d voices)" % len(VOICES)

    def extras(self):
        """The iSpeech API requires an API key."""

        return [dict(key='key', label="API Key", required=True)]

    def options(self):
        """Provides access to voice only."""

        voice_lookup = {self.normalize(api_name): api_name
                        for api_name in VOICES.keys()}

        def transform_voice(user_value):
            """Fixes whitespace and casing only."""
            normalized_value = self.normalize(user_value)
            return (voice_lookup[normalized_value]
                    if normalized_value in voice_lookup else user_value)

        return [
            dict(key='voice',
                 label="Voice",
                 values=[(api_name, f"{api_name} ({gender} {language})")
                         for api_name, (language, gender)
                         in sorted(VOICES.items(),
                                   key=lambda item: (item[1][0],
                                                     item[1][1]))],
                 transform=transform_voice),

            dict(key='speed',
                 label="Speed",
                 values=(-10, +10),
                 transform=lambda i: min(max(-10, int(round(float(i)))), +10),
                 default=0),

            dict(key='pitch',
                 label="Pitch",
                 values=(0, +200),
                 transform=lambda i: min(max(0, int(round(float(i)))), +200),
                 default=100),
        ]

    def run(self, text, options, path):
        """Downloads from iSpeech API directly to an MP3."""

        try:
            self.net_download(
                path,
                [
                    ('http://api.ispeech.org/api/rest',
                     dict(apikey=options['key'], action='convert',
                          text=subtext, voice=options['voice'],
                          speed=options['speed'], pitch=options['pitch']))
                    for subtext in self.util_split(text, 250)
                ],
                require=dict(mime='audio/mpeg', size=256),
                add_padding=True,
            )
        except ValueError as error:
            try:
                from urllib.parse import parse_qs
                error = ValueError(parse_qs(error.payload)['message'][0])
            except Exception:
                pass
            raise error

        self.net_reset()  # no throttle; FIXME should be controlled by trait
