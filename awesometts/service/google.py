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
Service implementation for Google Translate's text-to-speech API
"""

from threading import Lock

from .base import Service
from .common import Trait

__all__ = ['Google']


class Google(Service):
    """
    Provides a Service-compliant implementation for Google Translate.
    """

    __slots__ = [
        '_lock',
        '_cookies',
    ]

    NAME = "Google Translate"

    TRAITS = [Trait.INTERNET]

    _VOICE_CODES = {
        # n.b. When modifying any variants, make sure that there are
        # aliases defined in the voice_lookup list below for the most
        # common alternate codes, including an alias from the base
        # language to the variant with the most native speakers.

        'af': "Afrikaans",
        'am': "Amharic",
        'ar': "Arabic",
        'as': "Assamese",
        'az': "Azerbaijani",
        'be': "Belarusian",
        'bg': "Bulgarian",
        'bn': "Bengali",
        'bo': "Tibetan",
        'bs': "Bosnian",
        'ca': "Catalan",
        'ccp': "Chakma",
        'ceb': "Cebuano",
        'chr': "Cherokee",
        'ckb': "Central Kurdish",
        'co': "Corsican",
        'cs': "Czech",
        'cy': "Welsh",
        'da': "Danish",
        'de': "German",
        'dz': "Dzongkha",
        'el': "Greek",
        'en-AU': "English, Australian",
        'en-GB': "English, British",
        'en-US': "English, American",
        'en': "English",
        'eo': "Esperanto",
        'es-419': "Spanish, Americas",
        'es-ES': "Spanish, European",
        'es': "Spanish",
        'et': "Estonian",
        'eu': "Basque",
        'fa': "Persian",
        'ff': "Fulah",
        'fi': "Finnish",
        'fil': "Filipino",
        'fr': "French",
        'fy': "Western Frisian",
        'ga': "Irish",
        'gd': "Scottish Gaelic",
        'gl': "Galician",
        'gu': "Gujarati",
        'haw': "Hawaiian",
        'he': "Hebrew",
        'hi': "Hindi",
        'hmn': "Hmong",
        'hr': "Croatian",
        'ht': "Haitian Creole",
        'hu': "Hungarian",
        'hy': "Armenian",
        'id': "Indonesian",
        'is': "Icelandic",
        'it': "Italian",
        'iu': "Inuktitut",
        'ja': "Japanese",
        'jw': "Javanese",
        'ka': "Georgian",
        'kk': "Kazakh",
        'km': "Khmer",
        'kn': "Kannada",
        'ko': "Korean",
        'ku': "Kurdish",
        'ky': "Kyrgyz",
        'la': "Latin",
        'lb': "Luxembourgish",
        'lis': "Lisu",
        'lo': "Lao",
        'lt': "Lithuanian",
        'lv': "Latvian",
        'mez': "Menominee",
        'mg': "Malagasy",
        'mi': "Maori",
        'mk': "Macedonian",
        'ml': "Malayalam",
        'mn': "Mongolian",
        'mni-Mtei': "Manipuri (Meitei Mayek)",
        'mr': "Marathi",
        'ms': "Malay",
        'mt': "Maltese",
        'mul': "Multiple languages",
        'my': "Burmese",
        'nb': "Norwegian",
        'ne': "Nepali",
        'nl': "Dutch",
        'nn': "Norwegian Nynorsk",
        'no': "Norwegian",
        'nv': "Navajo",
        'ny': "Nyanja",
        'oj': "Ojibwa",
        'one': "Oneida",
        'or': "Odia",
        'osa': "Osage",
        'pa': "Punjabi",
        'pl': "Polish",
        'ps': "Pashto",
        'pt-BR': "Portuguese (Brazil)",
        'pt-PT': "Portuguese (Portugal)",
        'rhg': "Rohingya",
        'ro': "Romanian",
        'rom': "Romany",
        'ru': "Russian",
        'sa': "Sanskrit",
        'sd': "Sindhi",
        'see': "Seneca",
        'si': "Sinhala",
        'sk': "Slovak",
        'sl': "Slovenian",
        'sm': "Samoan",
        'sn': "Shona",
        'so': "Somali",
        'sq': "Albanian",
        'sr': "Serbian",
        'su': "Sundanese",
        'sv': "Swedish",
        'sw': "Swahili",
        'ta': "Tamil",
        'te': "Telugu",
        'tg': "Tajik",
        'th': "Thai",
        'ti': "Tigrinya",
        'tl': "Filipino",
        'tr': "Turkish",
        'tt': "Tatar",
        'ug': "Uyghur",
        'uk': "Ukrainian",
        'ur': "Urdu",
        'uz': "Uzbek",
        'uzs': "Southern Uzbek",
        'vi': "Vietnamese",
        'xh': "Xhosa",
        'yi': "Yiddish",
        'yo': "Yoruba",
        'zh-CN': "Chinese (Simplified)",
        'zh-HK': "Chinese (Hong Kong)",
        'zh-Hans': "Chinese (Simplified, China)",
        'zh-Hant': "Chinese (Traditional, Taiwan)",
        'zh-TW': "Chinese (Traditional)",
        'zh-yue': "Cantonese",
        'zu': "Zulu",
    }

    def __init__(self, *args, **kwargs):
        self._lock = Lock()
        self._cookies = None
        super(Google, self).__init__(*args, **kwargs)

    def desc(self):
        """
        Returns a short, static description.
        """

        return "Google Translate text-to-speech web API (%d voices); " \
            "service is heavily rate-limited and not recommended for mass " \
            "generation" % len(self._VOICE_CODES)

    def options(self):
        """
        Provides access to voice only.
        """

        voice_lookup = dict([
            # aliases for Chinese, Mandarin (PRC) (most speakers)
            (self.normalize(alias), 'zh-CN')
            for alias in ['Mandarin', 'Chinese', 'zh', 'zh-CMN', 'CMN']
        ] + [
            # aliases for Spanish, European (fewer speakers)
            (self.normalize(alias), 'es-ES')
            for alias in ['es-EU']
        ] + [
            # aliases for Spanish, Americas (most speakers)
            (self.normalize(alias), 'es-419')
            for alias in ['Spanish', 'es', 'es-LA', 'es-MX', 'es-US']
        ] + [
            # aliases for English, Australian (fewer speakers)
            (self.normalize(alias), 'en-AU')
            for alias in ['en-NZ']
        ] + [
            # aliases for English, British (moderate number)
            (self.normalize(alias), 'en-GB')
            for alias in ['en-EU', 'en-UK']
        ] + [
            # aliases for English, American (most speakers)
            (self.normalize(alias), 'en-US')
            for alias in ['English', 'en']
        ] + [
            # aliases for Portuguese, European (fewer speakers)
            (self.normalize(alias), 'pt-PT')
            for alias in ['pt-EU']
        ] + [
            # aliases for Portuguese, Brazilian (most speakers)
            (self.normalize(alias), 'pt-BR')
            for alias in ['Portuguese', 'pt']
        ] + [
            # then add/override for full names (e.g. Spanish, Americas)
            (self.normalize(name), code)
            for code, name in self._VOICE_CODES.items()
        ] + [
            # then add/override for official voices (e.g. es-419)
            (self.normalize(code), code)
            for code in self._VOICE_CODES.keys()
        ])

        def transform_voice(value):
            """Normalize and attempt to convert to official code."""

            normalized = self.normalize(value)
            if normalized in voice_lookup:
                return voice_lookup[normalized]

            # if input is more than two characters, maybe the user was trying
            # a country-specific code (e.g. es-CO); chop it off and try again
            if len(normalized) > 2:
                normalized = normalized[0:2]
                if normalized in voice_lookup:
                    return voice_lookup[normalized]

            return value

        DEFAULT_SPEED = 1.0
        return [
            dict(
                key='voice',
                label="Voice",
                values=[(code, "%s (%s)" % (name, code))
                        for code, name in sorted(self._VOICE_CODES.items())],
                transform=transform_voice,
            ),
            dict(
                key='speed',
                label="Speed",
                values=[(item, f"{item}") for item in (0.1, 0.3, 0.6, DEFAULT_SPEED, 1.3, 1.6, 2.0)],
                transform=float,
                default=DEFAULT_SPEED,
            ),
        ]

    def run(self, text, options, path):
        """
        Downloads from Google directly to an MP3.

        Because the MP3 we get from Google is already so very tiny, LAME
        is not used for transcoding.
        """

        with self._lock:
            if not self._cookies:
                headers = self.net_headers('https://www.google.com')
                self._cookies = ';'.join(cookie.split(';')[0]
                                         for cookie
                                         in headers['Set-Cookie'].split(','))
                self._logger.debug("Google cookies are %s", self._cookies)

        subtexts = self.util_split(text, 100)

        try:
            self._netops += 10 * len(subtexts)
            self.net_download(
                path,
                [
                    ('https://translate.google.com/translate_tts', dict(
                        ie='UTF-8',
                        q=subtext,
                        tl=options['voice'],
                        total=len(subtexts),
                        idx=idx,
                        ttsspeed=options.get('speed', 1.0),
                        textlen=len(subtext),
                        client='tw-ob',
                    ))
                    for idx, subtext in enumerate(subtexts)
                ],
                require=dict(mime='audio/mpeg', size=1024),
                custom_headers={'Cookie': self._cookies},
            )

        except IOError as io_error:
            raise IOError(
                "Google Translate returned an HTTP 503 (Service Unavailable) "
                "error. Unless Google Translate is down, this might indicate "
                "that too many TTS requests have recently come from your IP "
                "address. If so, try again after 24 hours.\n"
                "\n"
                "Depending on your specific situation, you might be able to "
                "switch to a different service offering " +
                self._VOICE_CODES[options['voice']].split(',').pop(0) + "."
            ) if getattr(io_error, 'code', None) == 503 else io_error
