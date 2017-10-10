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
Service implementation for RHVoice
"""

from .base import Service
from .common import Trait

__all__ = ['RHVoice']


VOICES_DIRS = (prefix + '/share/RHVoice/voices'
               for prefix in ['~', '~/usr', '/usr/local', '/usr'])
INFO_FILE = 'voice.info'

NAME_KEY = 'name'
LANGUAGE_KEY = 'language'
GENDER_KEY = 'gender'

PERCENT_VALUES = (-100, +100, "%")


def decimalize(percentage_value):
    """Given an integer within [-100, 100], return a decimal."""
    return round(percentage_value / 100.0, 2)


class RHVoice(Service):
    """Provides a Service-compliant implementation for RHVoice."""

    __slots__ = [
        '_voice_list',    # sorted list of (voice value, human label) tuples
        '_backgrounded',  # True if AwesomeTTS needed to start the service
    ]

    NAME = "RHVoice"

    TRAITS = [Trait.TRANSCODING]

    def __init__(self, *args, **kwargs):
        """
        Searches the RHVoice voice path for usable voices and populates
        the voices list.
        """

        if not self.IS_LINUX:
            raise EnvironmentError("AwesomeTTS only knows how to work w/ the "
                                   "Linux version of RHVoice at this time.")

        super(RHVoice, self).__init__(*args, **kwargs)

        def get_voice_info(voice_file):
            """Given a voice.info path, return a dict of voice info."""

            try:
                lookup = {}
                with open(voice_file) as voice_info:
                    for line in voice_info:
                        tokens = line.split('=', 1)
                        lookup[tokens[0]] = tokens[1].strip()
                return lookup
            except Exception:
                return {}

        def get_voices_from(path):
            """Return a list of voices at the given path, if any."""

            from os import listdir
            from os.path import expanduser, join, isdir, isfile

            path = expanduser(path)
            self._logger.debug("Searching %s for voices", path)

            result = [
                (
                    voice_name,
                    "%s (%s, %s)" % (
                        voice_info.get(NAME_KEY, voice_name),
                        voice_info.get(LANGUAGE_KEY, "no language"),
                        voice_info.get(GENDER_KEY, "no gender"),
                    ),
                )
                for voice_name, voice_info in sorted(
                    (
                        (voice_name, get_voice_info(voice_file))
                        for (voice_name, voice_file) in (
                            (voice_name, voice_file)
                            for (voice_name, voice_file)
                            in (
                                (voice_name, join(voice_dir, INFO_FILE))
                                for (voice_name, voice_dir)
                                in (
                                    (voice_name, join(path, voice_name))
                                    for voice_name in listdir(path)
                                )
                                if isdir(voice_dir)
                            )
                            if isfile(voice_file)
                        )
                    ),
                    key=lambda voice_name_voice_info: (
                        voice_name_voice_info[1].get(LANGUAGE_KEY),
                        voice_name_voice_info[1].get(NAME_KEY, voice_name_voice_info[0]),
                    )
                )
            ]

            if not result:
                raise EnvironmentError

            return result

        for path in VOICES_DIRS:
            try:
                self._voice_list = get_voices_from(path)
                break
            except Exception:
                continue
        else:
            raise EnvironmentError("No usable voices could be found")

        dbus_check = ''.join(self.cli_output_error('RHVoice-client',
                                                   '-s', '__awesometts_check'))
        if 'ServiceUnknown' in dbus_check and 'RHVoice' in dbus_check:
            self.cli_background('RHVoice-service')
            self._backgrounded = True
        else:
            self._backgrounded = False

    def desc(self):
        """Return short description with voice count."""

        return "RHVoice synthesizer (%d voices), %s" % (
            len(self._voice_list),
            "service started by AwesomeTTS" if self._backgrounded
            else "provided by host system"
        )

    def options(self):
        """Provides access to voice, speed, pitch, and volume."""

        voice_lookup = {self.normalize(voice[0]): voice[0]
                        for voice in self._voice_list}

        def transform_voice(value):
            """Normalize and attempt to convert to official voice."""
            normalized = self.normalize(value)
            return (voice_lookup[normalized] if normalized in voice_lookup
                    else value)

        def transform_percent(user_input):
            """Given some user input, return a integer within [-100, 100]."""
            return min(max(-100, int(round(float(user_input)))), +100)

        return [
            dict(key='voice', label="Voice", values=self._voice_list,
                 transform=transform_voice),
            dict(key='speed', label="Speed", values=PERCENT_VALUES,
                 transform=transform_percent, default=0),
            dict(key='pitch', label="Pitch", values=PERCENT_VALUES,
                 transform=transform_percent, default=0),
            dict(key='volume', label="Volume", values=PERCENT_VALUES,
                 transform=transform_percent, default=0),
        ]

    def run(self, text, options, path):
        """
        Saves the incoming text into a file, and pipes it through
        RHVoice-client and back out to a temporary wave file. If
        successful, the temporary wave file will be transcoded to an MP3
        for consumption by AwesomeTTS.
        """

        try:
            input_txt = self.path_input(text)
            output_wav = self.path_temp('wav')

            self.cli_pipe(
                ['RHVoice-client',
                 '-s', options['voice'],
                 '-r', decimalize(options['speed']),
                 '-p', decimalize(options['pitch']),
                 '-v', decimalize(options['volume'])],
                input_path=input_txt,
                output_path=output_wav,
            )

            self.cli_transcode(output_wav,
                               path,
                               require=dict(size_in=4096))

        finally:
            self.path_unlink(input_txt, output_wav)
