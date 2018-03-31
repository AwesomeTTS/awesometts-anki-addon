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
Service implementation for Amazon Polly
"""

from re import compile as re_compile

from .base import Service
from .common import Trait

import sys

__all__ = ['Amazon']

sys.path.append("/usr/lib/python3.6")
sys.path.append("/usr/local/lib/python3.5/dist-packages")
print(sys.path)
print(sys.version)
import boto3

print(dir(boto3)) # Find functions of interest.


LANGUAGES = {
"Turkish (tr-TR)": ["Filiz (Female)"],
"Swedish (sv-SE)": ["Astrid (Female)"],
"Russian (ru-RU)": ["Tatyana (Female)", "Maxim (Male)"],
"Romanian (ro-RO)": ["Carmen (Female)"],
"Portuguese (pt-PT)": ["Ines (Female)", "Cristiano (Male)"],
"Brazilian Portuguese (pt-BR)": ["Vitoria (Female)", "Ricardo (Male)"],
"Polish (pl-PL)": ["Maja (Female)", "Jan (Male)", "Jacek (Male)", "Ewa (Female)"],
"Dutch (nl-NL)": ["Ruben (Male)", "Lotte (Female)"],
"Norwegian (nb-NO)": ["Liv (Female)"],
"Korean (ko-KR)": ["Seoyeon (Female)"],
"Japanese (ja-JP)": ["Takumi (Male)", "Mizuki (Female)"],
"Italian (it-IT)": ["Giorgio (Male)", "Carla (Female)"],
"Icelandic (is-IS)": ["Karl (Male)", "Dora (Female)"],
"French (fr-FR)": ["Mathieu (Male)", "Celine (Female)"],
"Canadian French (fr-CA)": ["Chantal (Female)"],
"US Spanish (es-US)": ["Penelope (Female)", "Miguel (Male)"],
"Castilian Spanish (es-ES)": ["Enrique (Male)", "Conchita (Female)"],
"Welsh English (en-GB-WLS)": ["Geraint (Male)"],
"US English (en-US)": ["Salli (Female)", "Matthew (Male)", "Kimberly (Female)", "Kendra (Female)", "Justin (Male)", "Joey (Male)", "Joanna (Female)", "Ivy (Female)"],
"Indian English (en-IN)": ["Raveena (Female)", "Aditi (Female)"],
"British English (en-GB)": ["Emma (Female)", "Brian (Male)", "Amy (Female)"],
"Australian English (en-AU)": ["Russell (Male)", "Nicole (Female)"],
"German (de-DE)": ["Vicki (Female)", "Marlene (Female)", "Hans (Male)"],
"Danish (da-DK)": ["Naja (Female)", "Mads (Male)"],
"Welsh (cy-GB": ["Gwyneth (Female)"]
}

LANGUAGES_LIST = list(LANGUAGES.keys())
VOICES_LIST =  list()
for voices_for_lang in LANGUAGES.values():
    for voice in voices_for_lang:
        VOICES_LIST.append(voice)
CURRENT_LANGUAGE = "US English (en-US)"

assert CURRENT_LANGUAGE in LANGUAGES_LIST

RE_FILENAME = re_compile(r'name="filestozip" type="hidden" value="([\d_]+)"')
REQUIRE_MP3 = dict(mime='audio/mpeg', size=256)


class Amazon(Service):
    """Provides a Service-compliant implementation for Amazon polly."""

    __slots__ = []

    NAME = "AmazonPolly"

    TRAITS = [Trait.INTERNET]

    def desc(self):
        """Returns a short, static description."""

        return "Amazon polly voice synthesiser"

    def options(self):
        """Provides access to language and voice."""

        language_lookup = {self.normalize(value): value for value in LANGUAGES_LIST}
        voice_lookup = {self.normalize(value): value for value in VOICES_LIST}

        return [
            dict(
                key='language',
                label="Language",
                values=[(value, value) for value in LANGUAGES_LIST],
                transform=lambda value: language_lookup.get(self.normalize(value),
                                                         value),
                default=CURRENT_LANGUAGE,
            ),

            dict(
                key='voice',
                label="Voice",
                values=[(value, value) for value in VOICES_LIST],
                transform=lambda value: voice_lookup.get(self.normalize(value),
                                                         value),
            ),
        ]
    
    def extras(self):
        return [
            dict(
                key='dropdownmapper',
                label="Dropdown Mapper",
                values=LANGUAGES,
            )
        ]

    def run(self, text, options, path):
        """Send request to AWS API and then download mp3."""

        response=boto3.client('polly').synthesize_speech(
            OutputFormat='mp3',
            Text=text,
            VoiceId=options['voice'].split(' ')[0],
        )
        if response and response['AudioStream']:
            with open(path, 'wb') as response_output:
                response_output.write(response['AudioStream'].read())
