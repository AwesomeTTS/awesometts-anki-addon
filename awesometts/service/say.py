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
Service implementation for OS X's say command
"""

from .base import Service
from .common import Trait

__all__ = ['Say']


class Say(Service):
    """
    Provides a Service-compliant implementation for OS X's say command.
    """

    __slots__ = [
        '_binary',        # path to the eSpeak binary
        '_voice_list',    # list of installed voices as a list of tuples
    ]

    NAME = "OS X Speech Synthesis"

    TRAITS = [Trait.TRANSCODING]

    def __init__(self, *args, **kwargs):
        """
        Attempts to read the list of voices from `say -v ?`.

        However, if not running on Mac OS X, no environment inspection
        is attempted and an exception is immediately raised.
        """

        if not self.IS_MACOSX:
            raise EnvironmentError("Say is only available on Mac OS X")

        super(Say, self).__init__(*args, **kwargs)

        # n.b. voices *may* have spaces but *must* have a language code (the
        # language code used to be optional, but because very long voice names
        # will only have one space between the voice name and the language
        # code, it is not possible to reliably tell the difference between a
        # language code and a successive word in a voice name... as far as I
        # know, the `say -v ?` output always includes something in the
        # language code column, so this should be fine)
        import re
        re_voice = re.compile(r'^\s*([-\w]+( [-\w]+)*)\s+([-\w]+)')

        self._voice_list = [
            (name, "%s (%s)" % (name, code.replace('_', '-')))
            for code, name in sorted(
                (match.group(3), match.group(1))
                for match in [re_voice.match(line)
                              for line in self.cli_output('say', '-v', '?')]
                if match
            )
        ]

        if not self._voice_list:
            raise EnvironmentError("No usable output from call to `say -v ?`")

    def desc(self):
        """
        Returns a short, static description.
        """

        return "say CLI command (%d voices)" % len(self._voice_list)

    def options(self):
        """
        Provides access to voice and speed.
        """

        voice_lookup = {
            self.normalize(voice[0]): voice[0]
            for voice in self._voice_list
        }

        def transform_voice(value):
            """Normalize and attempt to convert to official voice."""

            normalized = self.normalize(value)

            return (
                voice_lookup[normalized] if normalized in voice_lookup
                else value
            )

        return [
            dict(
                key='voice',
                label="Voice",
                values=self._voice_list,
                transform=transform_voice,
            ),

            dict(
                key='speed',
                label="Speed",
                values=(10, 500, "wpm"),
                transform=int,
                default=175,
            ),
        ]

    def run(self, text, options, path):
        """
        Writes a temporary AIFF file and then transcodes to MP3.
        """

        output_aiff = self.path_temp('aiff')

        try:
            self.cli_call(
                'say',
                '-v', options['voice'],
                '-r', options['speed'],
                '-o', output_aiff,
                '--', text,
            )

            self.cli_transcode(
                output_aiff,
                path,
                require=dict(
                    size_in=4096,
                ),
            )

        finally:
            self.path_unlink(output_aiff)
