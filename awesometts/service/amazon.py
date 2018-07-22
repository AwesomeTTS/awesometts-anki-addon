# -*- coding: utf-8 -*-

# AWS Polly service for AwesomeTTS text-to-speech add-on
# Copyright (C) 2018-Present Artem Yefimenko
# Copyright (C) 2018-Present Edu Zamora
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
import os
import sys

__all__ = ['Amazon']

PATH_TO_BOTO3 = os.path.realpath(__file__).replace("service/amazon.py", "dependencies")
sys.path.append(PATH_TO_BOTO3)

import boto3

VOICES = [('cy-GB', 'female', 'Gwyneth'),
          ('da-DK', 'female', 'Naja'),
          ('da-DK', 'male', 'Mads'),
          ('de-DE', 'female', 'Vicki'),
          ('de-DE', 'female', 'Marlene'),
          ('de-DE', 'male', 'Hans'),
          ('en-AU', 'female', 'Nicole'),
          ('en-AU', 'male', 'Russell'),
          ('en-GB', 'female', 'Emma'),
          ('en-GB', 'female', 'Amy'),
          ('en-GB', 'male', 'Brian'),
          ('en-GB-WLS', 'male', 'Geraint'),
          ('en-IN', 'female', 'Aditi'),
          ('en-IN', 'female', 'Raveena'),
          ('en-US', 'female', 'Ivy'),
          ('en-US', 'female', 'Joanna'),
          ('en-US', 'female', 'Kendra'),
          ('en-US', 'female', 'Kimberly'),
          ('en-US', 'female', 'Salli'),
          ('en-US', 'male', 'Joey'),
          ('en-US', 'male', 'Justin'),
          ('en-US', 'male', 'Matthew'),
          ('es-ES', 'female', 'Conchita'),
          ('es-ES', 'male', 'Enrique'),
          ('es-US', 'female', 'Penelope'),
          ('es-US', 'male', 'Miguel'),
          ('fr-FR', 'female', 'Celine'),
          ('fr-FR', 'male', 'Mathieu'),
          ('fr-CA', 'female', 'Chantal'),
          ('is-IS', 'female', 'Dora'),
          ('is-IS', 'male', 'Karl'),
          ('it-IT', 'female', 'Carla'),
          ('it-IT', 'male', 'Giorgio'),
          ('ja-JP', 'female', 'Mizuki'),
          ('ja-JP', 'male', 'Takumi'),
          ('ko-KR', 'female', 'Seoyeon'),
          ('nb-NO', 'female', 'Liv'),
          ('nl-NL', 'female', 'Lotte'),
          ('nl-NL', 'male', 'Ruben'),
          ('pl-PL', 'female', 'Ewa'),
          ('pl-PL', 'female', 'Maja'),
          ('pl-PL', 'male', 'Jacek'),
          ('pl-PL', 'male', 'Jan'),
          ('pt-BR', 'female', 'Vitoria'),
          ('pt-BR', 'male', 'Ricardo'),
          ('pt-PT', 'female', 'Ines'),
          ('pt-PT', 'male', 'Cristiano'),
          ('ro-RO', 'female', 'Carmen'),
          ('ru-RU', 'female', 'Tatyana'),
          ('ru-RU', 'male',   'Maxim'),
          ('sv-SE', 'female', 'Astrid'),
          ('tr-TR', 'female', 'Filiz')]

RE_FILENAME = re_compile(r'name="filestozip" type="hidden" value="([\d_]+)"')
REQUIRE_MP3 = dict(mime='audio/mpeg', size=256)


class Amazon(Service):
    """Provides a Service-compliant implementation for Amazon polly."""

    __slots__ = []

    NAME = "Amazon Polly"

    TRAITS = [Trait.INTERNET]

    def desc(self):
        """Returns a short, static description."""

        return "Amazon Polly (%d voices)" % len(VOICES)

    def options(self):
        """Provides access to voice only."""

        voice_lookup = {self.normalize(name): name
                        for language, gender, name in VOICES}

        def transform_voice(value):
            """Fixes whitespace and casing errors only."""
            normal = self.normalize(value)
            return voice_lookup[normal] if normal in voice_lookup else value

        return [dict(key='voice',
                     label="Voice",
                     values=[(name, "%s (%s %s)" % (name, gender, language))
                             for language, gender, name in VOICES],
                     transform=transform_voice)]
    
    def extras(self):
        """Provides input for AWS credentials and lexicon names."""
        return [dict(key='accesskey', label="AWS Access Key"), dict(key='secretkey', label="AWS Secret Key"),
                dict(key='lexicons', label="Lexicons")]

    def run(self, text, options, path):
        """Send request to AWS API and then download mp3."""
        if not text:
            raise IOError("Please provide some text for record!")
        if options['accesskey'] and options['secretkey']:
            boto3_client = boto3.client('polly', aws_access_key_id=options['accesskey'], aws_secret_access_key=options['secretkey'])
        else:
            boto3_client = boto3.client('polly')
        lexicons = []
        if options['lexicons']:
            lexicons = options['lexicons'].split(", ")
        response=boto3_client.synthesize_speech(
            OutputFormat='mp3',
            Text=text,
            VoiceId=options['voice'],
            LexiconNames=lexicons
        )
        if response and response['AudioStream']:
            with open(path, 'wb') as response_output:
                response_output.write(response['AudioStream'].read())