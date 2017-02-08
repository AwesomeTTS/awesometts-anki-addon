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
Service implementation for eSpeak text-to-speech engine
"""

from .base import Service
from .common import Trait

__all__ = ['ESpeak']


class ESpeak(Service):
    """
    Provides a Service-compliant implementation for eSpeak.
    """

    __slots__ = [
        '_binary',  # name of or path to the eSpeak binary
        '_lookup',  # dict mapping 'voices' and 'variant' lists
    ]

    NAME = "eSpeak"

    TRAITS = [Trait.TRANSCODING]

    def __init__(self, *args, **kwargs):
        """
        Attempts to locate the eSpeak binary and read the list of voices
        from the `espeak --voices` output. If running on Windows, the
        registry will be searched to attempt to locate the eSpeak binary
        if it is not already in the path.

        eSpeak is a little unique in that it will accept a wide array of
        things with its --voices parameter, such as language (e.g. es),
        country-specific language (e.g. es-mx), or a specific voice file
        name (e.g. mexican-mbrola-1). It is also unique in that it has
        one list of native voices and another list of MBROLA voices.

        For our purposes, we use the file name as the official driver of
        the 'voice' option, but we accept and remap the top-level and
        country-specific language codes to the "official" voice names.
        """

        super(ESpeak, self).__init__(*args, **kwargs)

        try:
            self._binary = 'espeak'
            output = {'native': self.cli_output(self._binary, '--voices')}

        except OSError:
            if self.IS_WINDOWS:
                self._binary = r'%s\command_line\%s.exe' % (
                    self.reg_hklm(
                        r'Software\Microsoft\Speech\Voices\Tokens\eSpeak',
                        'Path',
                    ),
                    self._binary,
                )
                output = {'native': self.cli_output(self._binary, '--voices')}

            else:
                raise

        for alt in ['mbrola', 'variant']:
            try:
                output[alt] = self.cli_output(self._binary, '--voices=' + alt)
            except Exception:  # catch-all, pylint:disable=broad-except
                output[alt] = []

        import re
        from os.path import basename

        re_voice = re.compile(
            r'\s*(\d+)'               # priority; lower numbers preferred
            r'\s+([-\w]+)'            # language code (or "variant")
            r'\s+(\d+)?([-\w])'       # age, gender
            r'\s+([-\w]+)'            # voice name
            r'\s+([-!/\\\w]+)'        # file name
            r'(\s+\(([- ()\w]+)\))?'  # other languages
        )

        re_lang_filter = re.compile(r'[^-a-z]', re.IGNORECASE)

        self._lookup = {
            key: [
                {
                    'type': key,
                    'priority': int(match.group(1)),
                    'code': match.group(2),
                    'age': int(match.group(3)) if match.group(3) else None,
                    'gender': match.group(4).upper(),
                    'name': match.group(5),
                    'file': (basename(match.group(6)) if key == 'variant'
                             else match.group(6)),
                    'others': [
                        code
                        for code in [
                            re_lang_filter.sub('', code)
                            for code in match.group(8).split(')(')
                        ]
                        if code
                    ] if match.group(8) else [],
                }
                for match in [re_voice.match(line) for line in lines]
                if match
            ]
            for key, lines in output.items()
        }

        self._lookup['voices'] = (
            # this puts this list into a "last one wins" ordering where native
            # voices are preferred over MBROLA ones and where lesser priority
            # numbers win out over greater ones (native voices are preferred
            # over MBROLA ones since the MBROLA ones do not always work)

            sorted(self._lookup['mbrola'],
                   key=lambda voice: -voice['priority']) +
            sorted(self._lookup['native'],
                   key=lambda voice: -voice['priority'])
        )

        del self._lookup['mbrola']
        del self._lookup['native']

        if not self._lookup['voices']:
            raise EnvironmentError("No usable output from `espeak --voices`")

    def desc(self):
        """
        Returns a version string, terse description, and the TTS data
        location from `espeak --version`.
        """

        return "%s (%d voices)" % (
            self.cli_output(self._binary, '--version').pop(0),
            len(self._lookup['voices']),
        )

    def options(self):
        """
        Provides access to voice, speed, word gap, pitch, and volume.
        """

        lookup = self._lookup

        voice_lookup = dict([
            # language codes from each "others" list
            (self.normalize(other), voice['file'])
            for voice in lookup['voices']
            for other in voice['others']
        ] + [
            # language code listed as the primary for each
            (self.normalize(voice['code']), voice['file'])
            for voice in lookup['voices']
        ] + [
            # voice name given for each
            (self.normalize(voice['name']), voice['file'])
            for voice in lookup['voices']
        ] + [
            # official file name for each
            (self.normalize(voice['file']), voice['file'])
            for voice in lookup['voices']
        ])

        variant_lookup = dict([
            # variant name given for each
            (self.normalize(variant['name']), variant['file'])
            for variant in lookup['variant']
        ] + [
            # official file name for each
            (self.normalize(variant['file']), variant['file'])
            for variant in lookup['variant']
        ] + [
            # helpful aliases for "normal"
            ('', 'normal'),
            ('none', 'normal'),
        ])

        def transform_voice(value):
            """Normalize and attempt to convert to official voice."""

            normalized = self.normalize(value)
            if normalized in voice_lookup:
                return voice_lookup[normalized]

            # if input is more than two characters, maybe the user was trying
            # a country-specific code (e.g. es-mx); chop it off and try again
            if len(normalized) > 2:
                if len(normalized) > 3:  # try the 3-character version first
                    normalized = normalized[0:3]
                    if normalized in voice_lookup:
                        return voice_lookup[normalized]

                normalized = normalized[0:2]
                if normalized in voice_lookup:
                    return voice_lookup[normalized]

            return value

        def transform_variant(value):
            """Normalize and attempt to convert to official variant."""

            normalized = self.normalize(value)
            return (
                variant_lookup[normalized] if normalized in variant_lookup
                else value
            )

        return [
            dict(
                key='voice',
                label="Voice",
                values=[
                    (
                        voice['file'],
                        "%s (%s%s%s)" % (
                            voice['name'],

                            str(voice['age']) + "-year-old " if
                            voice['age'] else "",

                            "male " if voice['gender'] == 'M'
                            else "female " if voice['gender'] == 'F'
                            else "",

                            voice['code'],
                        ),
                    )
                    for voice in sorted(
                        lookup['voices'],
                        key=lambda voice: (voice['code'],
                                           voice['type'] == 'mbrola',
                                           voice['gender'] not in 'MF',
                                           voice['gender'] == 'F',
                                           voice['name']),
                    )
                ],
                transform=transform_voice,
            ),

            dict(
                key='variant',
                label="Variant",
                values=[('normal', "normal")] + [
                    (
                        variant['file'],
                        "%s (%s%s)" % (
                            variant['name'],

                            str(variant['age']) + "-year-old " if
                            variant['age'] else "",

                            "male" if variant['gender'] == 'M'
                            else "female" if variant['gender'] == 'F'
                            else "other",
                        ),
                    )
                    for variant in sorted(
                        lookup['variant'],
                        key=lambda variant: (variant['gender'] not in 'MF',
                                             variant['gender'] == 'F',
                                             variant['name']),
                    )
                ],
                transform=transform_variant,
                default="normal"
            ),

            dict(
                key='speed',
                label="Speed",
                values=(80, 450, "wpm"),
                transform=int,
                default=175,
            ),

            dict(
                key='gap',
                label="Word Gap",
                values=(0.0, 5.0, "seconds"),
                transform=float,
                default=0.0,
            ),

            dict(
                key='pitch',
                label="Pitch",
                values=(0, 99, "%"),
                transform=int,
                default=50,
            ),

            dict(
                key='volume',
                label="Volume",
                values=(0, 200),
                transform=int,
                default=100,
            ),
        ]

    def run(self, text, options, path):
        """
        Checks for unicode workaround on Windows, writes a temporary
        wave file, and then transcodes to MP3.
        """

        input_file = self.path_workaround(text)
        output_wav = self.path_temp('wav')

        voice = ('+'.join([options['voice'], options['variant']])
                 if options['variant'] and options['variant'] != "normal"
                 else options['voice'])

        try:
            self.cli_call(
                [
                    self._binary,
                    '-v', voice,
                    '-s', options['speed'],
                    '-g', int(options['gap'] * 100.0),
                    '-p', options['pitch'],
                    '-a', options['volume'],
                    '-w', output_wav,
                ] + (
                    ['-f', input_file] if input_file
                    else ['--', text]
                )
            )

            self.cli_transcode(
                output_wav,
                path,
                require=dict(
                    size_in=4096,
                ),
                add_padding=True,
            )

        finally:
            self.path_unlink(input_file, output_wav)
