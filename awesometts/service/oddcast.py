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
Service implementation for Oddcast text-to-speech demo
"""

from .base import Service
from .common import Trait

__all__ = ['Oddcast']


LANGUAGES = {1: 'en', 2: 'es', 3: 'de', 4: 'fr', 5: 'ca', 6: 'pt', 7: 'it',
             8: 'el', 9: 'sv', 10: 'zh', 11: 'nl', 12: 'ja', 13: 'ko',
             14: 'pl', 15: 'gl', 16: 'tr', 18: 'cs', 19: 'da', 20: 'no',
             21: 'ru', 22: 'eu', 23: 'fi', 24: 'hi', 25: 'is', 26: 'th',
             27: 'ar', 28: 'id', 29: 'hu', 30: 'ro', 31: 'eo'}

MAPPINGS = [
    # Note that some of the voices below are dummied out because of various
    # problems (e.g. jibberish output when encountering input characters with
    # diacritics despite being voices for languages where such diacritics are
    # common, producing very long stretches of silence in the output when
    # encountering the end of a sentence).
    #
    # The voices that are dummied out because they produce very long stretches
    # of silence in the output when encountering the end of a sentence *could*
    # possibly be worked around with an audio post-processing tool or by
    # recognizing the repeating `UUUU` pattern in the MP3. However, if this is
    # attempted, keep in mind that the silent stretches may appear multiple
    # times in the audio based on where the original input has sentences or
    # ellipses (i.e. not just as simple as "strip silence from the end"). Also
    # keep in mind that even if this can be worked around post-processing,
    # these voices are still problematic because they frequently time out when
    # fed multiple sentences (presumably because whatever backend system
    # generates the audio is really busy generating all that silence).

    # engine ID, language ID, voice ID, language variant, gender, name
    (2, 1, 1, 'US', 'female', "Susan"),
    (2, 1, 2, 'US', 'male', "Dave"),
    (2, 1, 4, 'GB', 'female', "Elizabeth"),
    (2, 1, 5, 'GB', 'male', "Simon"),
    (2, 1, 6, 'GB', 'female', "Catherine"),
    (2, 1, 7, 'US', 'female', "Allison"),
    (2, 1, 8, 'US', 'male', "Steven"),
    (2, 1, 9, 'AU', 'male', "Alan"),
    (2, 1, 10, 'AU', 'female', "Grace"),
    (2, 1, 11, 'IN', 'female', "Veena"),
    (2, 2, 1, 'ES', 'female', "Carmen"),
    (2, 2, 2, 'ES', 'male', "Juan"),
    (2, 2, 3, 'CL', 'female', "Francisca"),
    (2, 2, 4, 'AR', 'male', "Diego"),
    (2, 2, 5, 'MX', 'female', "Esperanza"),
    (2, 2, 6, 'ES', 'male', "Jorge"),
    (2, 2, 7, 'US', 'male', "Carlos"),
    (2, 2, 8, 'US', 'female', "Soledad"),
    (2, 2, 9, 'ES', 'female', "Leonor"),
    (2, 2, 10, None, 'female', "Ximena"),
    (2, 3, 2, None, 'male', "Stefan"),
    (2, 3, 3, None, 'female', "Katrin"),
    (2, 4, 2, None, 'male', "Bernard"),
    (2, 4, 3, None, 'female', "Jolie"),
    (2, 4, 4, None, 'female', "Florence"),
    (2, 4, 5, None, 'female', "Charlotte"),
    (2, 4, 6, None, 'male', "Olivier"),
    (2, 5, 1, None, 'female', "Montserrat"),
    (2, 5, 2, None, 'male', "Jordi"),
    (2, 5, 3, 'Valencian', 'female', "Empar"),
    (2, 6, 1, 'BR', 'female', "Gabriela"),
    (2, 6, 2, 'PT', 'female', "Amalia"),
    (2, 6, 3, 'PT', 'male', "Eusebio"),
    (2, 6, 4, 'BR', 'female', "Fernanda"),
    (2, 6, 5, 'BR', 'male', "Felipe"),
    (2, 7, 1, None, 'female', "Paola"),
    (2, 7, 2, None, 'female', "Silvana"),
    (2, 7, 3, None, 'female', "Valentina"),
    (2, 7, 5, None, 'male', "Luca"),
    (2, 7, 6, None, 'male', "Marcello"),
    (2, 7, 7, None, 'male', "Roberto"),
    (2, 7, 8, None, 'male', "Matteo"),
    (2, 7, 9, None, 'female', "Giulia"),
    (2, 7, 10, None, 'female', "Federica"),
    (2, 8, 1, None, 'female', "Afroditi"),
    (2, 8, 3, None, 'male', "Nikos"),
    (2, 9, 1, None, 'female', "Annika"),
    (2, 9, 2, None, 'male', "Sven"),
    (2, 10, 1, 'CMN', 'female', "Linlin"),
    (2, 10, 2, 'CMN', 'female', "Lisheng"),
    (2, 11, 1, None, 'male', "Willem"),
    (2, 11, 2, None, 'female', "Saskia"),
    (2, 14, 1, None, 'female', "Zosia"),
    (2, 14, 2, None, 'male', "Krzysztof"),
    (2, 15, 1, None, 'female', "Carmela"),
    (2, 16, 1, None, 'male', "Kerem"),
    (2, 16, 2, None, 'female', "Zeynep"),
    (2, 16, 3, None, 'female', "Selin"),
    (2, 19, 1, None, 'female', "Frida"),
    (2, 19, 2, None, 'male', "Magnus"),
    (2, 20, 1, None, 'female', "Vilde"),
    (2, 20, 2, None, 'male', "Henrik"),
    (2, 21, 1, None, 'female', "Olga"),
    (2, 21, 2, None, 'male', "Dmitri"),
    (2, 23, 1, None, 'female', "Milla"),
    (2, 23, 2, None, 'male', "Marko"),
    (2, 27, 1, None, 'male', "Tarik"),
    (2, 27, 2, None, 'female', "Laila"),
    (2, 30, 1, None, 'female', "Ioana"),
    (2, 31, 1, None, 'male', "Ludoviko"),
    (3, 1, 1, 'US', 'female', "Kate"),
    (3, 1, 2, 'US', 'male', "Paul"),
    (3, 1, 3, 'US', 'female', "Julie"),
    (3, 1, 4, 'GB', 'female', "Bridget"),
    (3, 1, 5, 'GB', 'male', "Hugh"),
    (3, 1, 6, 'US', 'female', "Ashley"),
    (3, 1, 7, 'US', 'male', "James"),
    # accents trigger jibberish: (3, 2, 1, None, 'female', "Violeta"),
    # accents trigger jibberish: (3, 2, 2, 'MX', 'male', "Francisco"),
    (3, 4, 1, 'CA', 'female', "Chloe"),
    (3, 10, 1, 'CMN', 'female', "Lily"),
    (3, 10, 3, 'CMN', 'female', "Hui"),
    (3, 10, 4, 'CMN', 'male', "Liang"),
    (3, 12, 2, None, 'male', "Show"),
    (3, 12, 3, None, 'female', "Misaki"),
    (3, 13, 1, None, 'female', "Yumi"),
    (3, 13, 2, None, 'male', "Junwoo"),
    (4, 1, 1, 'US', 'female', "Jennifer"),
    (4, 1, 2, 'US', 'female', "Jill"),
    (4, 1, 3, 'US', 'male', "Tom"),
    (4, 1, 4, 'AU', 'female', "Karen"),
    (4, 1, 5, 'GB', 'male', "Daniel"),
    # outputs a ton of silence: (4, 1, 6, 'GB', 'female', "Emily"),
    (4, 1, 7, 'GB', 'female', "Serena"),
    (4, 1, 8, 'IE', 'female', "Moira"),
    (4, 1, 9, 'IN', 'female', "Sangeeta"),
    (4, 1, 10, 'AU', 'male', "Lee"),
    (4, 1, 11, 'US', 'female', "Samantha"),
    (4, 1, 12, 'Scottish', 'female', "Fiona"),
    (4, 1, 13, 'ZA', 'female', "Tessa"),
    (4, 2, 1, None, 'male', "Duardo"),
    # outputs a ton of silence: (4, 2, 2, None, 'female', "Isabel"),
    (4, 2, 3, None, 'female', "Monica"),
    (4, 2, 4, 'MX', 'female', "Paulina"),
    (4, 2, 5, 'MX', 'male', "Javier"),
    (4, 3, 1, None, 'female', "Steffi"),
    (4, 3, 2, None, 'male', "Yannick"),
    (4, 3, 3, None, 'female', "Anna"),
    (4, 4, 1, 'CA', 'male', "Felix"),
    (4, 4, 2, 'CA', 'female', "Julie"),
    (4, 4, 3, None, 'male', "Sebastien"),
    (4, 4, 4, None, 'female', "Virginie"),
    (4, 4, 5, None, 'male', "Thomas"),
    (4, 5, 1, None, 'female', "Nuria"),
    # outputs a ton of silence: (4, 6, 1, 'PT', 'female', "Madalena"),
    (4, 6, 2, 'BR', 'female', "Raquel"),
    (4, 6, 3, 'PT', 'female', "Joana"),
    (4, 7, 1, None, 'male', "Paolo"),
    (4, 7, 2, None, 'female', "Silvia"),
    (4, 8, 1, None, 'male', "Alexandros"),
    (4, 9, 1, None, 'male', "Alva"),
    # outputs a ton of silence: (4, 9, 2, None, 'female', "Ingrid"),
    (4, 9, 3, None, 'male', "Oskar"),
    (4, 10, 1, 'YUE', 'female', "Sin-Ji"),
    (4, 10, 2, 'TW', 'female', "Ya-Ling"),
    # outputs a ton of silence: (4, 10, 3, 'CMN', 'female', "Mei-Ling"),
    (4, 10, 4, 'CMN', 'female', "Ting-Ting"),
    (4, 11, 1, 'BE', 'female', "Ellen"),
    (4, 11, 2, 'NL', 'female', "Claire"),
    (4, 11, 3, 'NL', 'female', "Laura"),
    (4, 11, 4, 'NL', 'male', "Xander"),
    (4, 12, 1, None, 'female', "Kyoko"),
    (4, 13, 1, None, 'female', "Narae"),
    (4, 14, 1, None, 'female', "Agata"),
    (4, 16, 1, None, 'female', "Aylin"),
    (4, 18, 1, None, 'female', "Zuzana"),
    (4, 19, 1, None, 'female', "Ida"),
    (4, 19, 2, None, 'female', "Nanna"),
    (4, 20, 1, None, 'female', "Nora"),
    (4, 20, 2, None, 'female', "Stine"),
    # outputs a ton of silence: (4, 21, 1, None, 'female', "Katerina"),
    (4, 21, 2, None, 'female', "Milena"),
    (4, 22, 1, None, 'female', "Arantxa"),
    (4, 23, 1, None, 'male', "Mikko"),
    (4, 24, 1, None, 'female', "Lekha"),
    # outputs a ton of silence: (4, 25, 1, None, 'female', "Ragga"),
    (4, 26, 1, None, 'female', "Narisa"),
    (4, 27, 1, None, 'male', "Maged"),
    (4, 28, 1, None, 'female', "Damayanti"),
    (4, 29, 1, None, 'female', "Eszter"),
    (4, 30, 1, None, 'female', "Simona"),
]

VOICES = {'%s/%s' % (LANGUAGES[mapping[1]], mapping[5].lower()): mapping
          for mapping in MAPPINGS}


class Oddcast(Service):
    """
    Provides a Service-compliant implementation for Oddcast's
    text-to-speech demo.
    """

    __slots__ = []

    NAME = "Oddcast"

    TRAITS = [Trait.INTERNET]

    def desc(self):
        """Returns name with a voice count."""

        return "Oddcast Demo (%d voices)" % len(VOICES)

    def options(self):
        """Provides access to voice only."""

        voice_lookup = {self.normalize(key): key for key in VOICES.keys()}

        def transform_voice(value):
            """Fixes whitespace and casing errors only."""
            normal = self.normalize(value)
            return voice_lookup[normal] if normal in voice_lookup else value

        def voice_sorter(voice_item):
            """Returns a tuple of language, country, gender, name."""
            _, voice_def = voice_item
            _, lang_id, _, country, gender, name = voice_def
            return LANGUAGES[lang_id], country or '', gender, name

        return [
            dict(
                key='voice',
                label="Voice",
                values=[
                    (
                        key,
                        "%s (%s %s)" % (name, gend,
                                        "%s-%s" % (LANGUAGES[lang_id], variant)
                                        if variant else LANGUAGES[lang_id]),
                    )
                    for key, (_, lang_id, _, variant, gend, name)
                    in sorted(VOICES.items(), key=voice_sorter)
                ],
                transform=transform_voice,
            ),
        ]

    def run(self, text, options, path):
        """Downloads from Oddcast directly to an MP3."""

        eng_id, lang_id, vo_id, _, _, _ = VOICES[options['voice']]

        from hashlib import md5

        def get_md5(subtext):
            """Generates the filename."""

            return md5(
                (
                    f'<engineID>{eng_id}</engineID><voiceID>{vo_id}</voiceID>'
                    f'<langID>{lang_id}</langID><ext>mp3</ext>{subtext}'
                ).encode()
            ).hexdigest()

        self.net_download(
            path,
            [
                ('http://cache-a.oddcast.com/c_fs/%s.mp3' % get_md5(subtext),
                 dict(engine=eng_id, language=lang_id, voice=vo_id,
                      text=subtext, useUTF8=1))
                for subtext in self.util_split(text, 180)  # see site maxlength
            ],
            require=dict(mime='audio/mpeg', size=256),
            add_padding=True,
        )
