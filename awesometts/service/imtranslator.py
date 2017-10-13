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
Service implementation for ImTranslator's text-to-speech portal
"""

import re
from socket import error as SocketError  # non-caching error class

from .base import Service
from .common import Trait

__all__ = ['ImTranslator']


URL = 'http://imtranslator.net/translate-and-speak/sockets/tts.asp'


class ImTranslator(Service):
    """
    Provides a Service-compliant implementation for ImTranslator.
    """

    __slots__ = []

    NAME = "ImTranslator"

    TRAITS = [Trait.INTERNET, Trait.TRANSCODING]

    _VOICES = [('Stefan', 'de', 'male'), ('VW Paul', 'en', 'male'),
               ('VW Kate', 'en', 'female'), ('Jorge', 'es', 'male'),
               ('Florence', 'fr', 'female'), ('Matteo', 'it', 'male'),
               ('VW Misaki', 'ja', 'female'), ('VW Yumi', 'ko', 'female'),
               ('Gabriela', 'pt', 'female'), ('Olga', 'ru', 'female'),
               ('VW Lily', 'zh', 'female')]

    _RE_SWF = re.compile(r'https?:[\w:/\.]+\.swf\?\w+=\w+', re.IGNORECASE)

    def __init__(self, *args, **kwargs):
        if self.IS_MACOSX:
            raise EnvironmentError(
                "ImTranslator cannot be used on Mac OS X due to mplayer "
                "crashes while dumping the audio. If you are able to fix "
                "this, please send a pull request."
            )

        super(ImTranslator, self).__init__(*args, **kwargs)

    def desc(self):
        """
        Returns a short, static description.
        """

        return "ImTranslator text-to-speech web portal (%d voices)" % \
               len(self._VOICES)

    def options(self):
        """
        Provides access to voice and speed.
        """

        voice_lookup = dict([
            # language codes with full genders
            (self.normalize(code + gender), name)
            for name, code, gender in self._VOICES
        ] + [
            # language codes with first character of genders
            (self.normalize(code + gender[0]), name)
            for name, code, gender in self._VOICES
        ] + [
            # bare language codes
            (self.normalize(code), name)
            for name, code, gender in self._VOICES
        ] + [
            # official voice names
            (self.normalize(name), name)
            for name, code, gender in self._VOICES
        ])

        def transform_voice(value):
            """Normalize and attempt to convert to official name."""

            normalized = self.normalize(value)
            if normalized in voice_lookup:
                return voice_lookup[normalized]

            # if input is more than two characters, maybe the user was trying
            # a country-specific code (e.g. en-US); chop it off and try again
            if len(normalized) > 2:
                normalized = normalized[0:2]
                if normalized in voice_lookup:
                    return voice_lookup[normalized]

            return value

        def transform_speed(value):
            """Return the speed value closest to one of the user's."""
            value = float(value)
            return min([10, 6, 3, 0, -3, -6, -10],
                       key=lambda i: abs(i - value))

        return [
            dict(
                key='voice',
                label="Voice",
                values=[
                    (name, "%s (%s %s)" % (name, gender, code))
                    for name, code, gender in self._VOICES
                ],
                transform=transform_voice,
            ),

            dict(
                key='speed',
                label="Speed",
                values=[(10, "fastest"), (6, "faster"), (3, "fast"),
                        (0, "normal"),
                        (-3, "slow"), (-6, "slower"), (-10, "slowest")],
                transform=transform_speed,
                default=0,
            ),
        ]

    def run(self, text, options, path):
        """
        Sends the TTS request to ImTranslator, captures the audio from
        the returned SWF, and transcodes to MP3.

        Because ImTranslator sometimes raises various errors, both steps
        of this (i.e. downloading the page and dumping the audio) may be
        retried up to three times.
        """

        output_wavs = []
        output_mp3s = []
        require = dict(size_in=4096)

        logger = self._logger

        try:
            for subtext in self.util_split(text, 400):
                for i in range(1, 4):
                    try:
                        logger.info("ImTranslator net_stream: attempt %d", i)
                        result = self.net_stream(
                            (URL,
                             dict(text=subtext, vc=options['voice'],
                                  speed=options['speed'], FA=1)),
                            require=dict(mime='text/html', size=256),
                            method='POST',
                            custom_headers={'Referer': URL}
                        ).decode()

                        result = self._RE_SWF.search(result)
                        if not result or not result.group():
                            raise EnvironmentError('500b', "cannot find SWF"
                                                           "path in payload")
                        result = result.group()
                    except (EnvironmentError, IOError) as error:
                        if getattr(error, 'code', None) == 500:
                            logger.warn("ImTranslator net_stream: got 500")
                        elif getattr(error, 'errno', None) == '500b':
                            logger.warn("ImTranslator net_stream: no SWF path")
                        elif 'timed out' in format(error):
                            logger.warn("ImTranslator net_stream: timeout")
                        else:
                            logger.error("ImTranslator net_stream: %s", error)
                            raise
                    else:
                        logger.info("ImTranslator net_stream: success")
                        break
                else:
                    logger.error("ImTranslator net_stream: exhausted")
                    raise SocketError("unable to fetch page from ImTranslator "
                                      "even after multiple attempts")

                output_wav = self.path_temp('wav')
                output_wavs.append(output_wav)

                for i in range(1, 4):
                    try:
                        logger.info("ImTranslator net_dump:   attempt %d", i)
                        self.net_dump(output_wav, result)
                    except RuntimeError:
                        logger.warn("ImTranslator net_dump:   failure")
                    else:
                        logger.info("ImTranslator net_dump:   success")
                        break
                else:
                    logger.error("ImTranslator net_dump:   exhausted")
                    raise SocketError("unable to dump audio from ImTranslator "
                                      "even after multiple attempts")

            if len(output_wavs) > 1:
                for output_wav in output_wavs:
                    output_mp3 = self.path_temp('mp3')
                    output_mp3s.append(output_mp3)
                    self.cli_transcode(output_wav, output_mp3, require=require)

                self.util_merge(output_mp3s, path)

            else:
                self.cli_transcode(output_wavs[0], path, require=require)

        finally:
            self.path_unlink(output_wavs, output_mp3s)
