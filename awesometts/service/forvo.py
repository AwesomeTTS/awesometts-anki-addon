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
Service implementation for Forvo Pronunciation API
"""

import json
from .base import Service
from .common import Trait
import urllib

__all__ = ['Forvo']


VOICES = [
    ('abq','Abaza'),
    ('ab','Abkhazian'),
    ('ady','Adygean'),
    ('aa','Afar'),
    ('af','Afrikaans'),
    ('ak','Akan'),
    ('sq','Albanian'),
    ('ale','Aleut'),
    ('alq','Algonquin'),
    ('am','Amharic'),
    ('grc','Ancient Greek'),
    ('ar','Arabic'),
    ('an','Aragonese'),
    ('arp','Arapaho'),
    ('aae','Arbëresh'),
    ('hy','Armenian'),
    ('rup','Aromanian'),
    ('as','Assamese'),
    ('aii','Assyrian Neo-Aramaic'),
    ('ast','Asturian'),
    ('av','Avaric'),
    ('ay','Aymara'),
    ('az','Azerbaijani'),
    ('bqi','Bakhtiari'),
    ('bal','Balochi'),
    ('bm','Bambara'),
    ('bcj','Bardi'),
    ('ba','Bashkir'),
    ('eu','Basque'),
    ('bar','Bavarian'),
    ('be','Belarusian'),
    ('bn','Bengali'),
    ('bh','Bihari'),
    ('bi','Bislama'),
    ('bs','Bosnian'),
    ('bph','Botlikh'),
    ('pcc','Bouyei'),
    ('br','Breton'),
    ('bzd','Bribri'),
    ('bg','Bulgarian'),
    ('bxr','Buriat'),
    ('my','Burmese'),
    ('bsk','Burushaski'),
    ('sro','Campidanese'),
    ('yue','Cantonese'),
    ('kea','Cape Verdean Creole'),
    ('ca','Catalan'),
    ('ceb','Cebuano'),
    ('tzm','Central Atlas Tamazight'),
    ('bcl','Central Bikol'),
    ('ch','Chamorro'),
    ('ce','Chechen'),
    ('chr','Cherokee'),
    ('ny','Chichewa'),
    ('cv','Chuvash'),
    ('rar','Cook Islands Maori'),
    ('kw','Cornish'),
    ('co','Corsican'),
    ('cr','Cree'),
    ('mus','Creek'),
    ('crh','Crimean Tatar'),
    ('hr','Croatian'),
    ('cs','Czech'),
    ('dag','Dagbani'),
    ('da','Danish'),
    ('prs','Dari'),
    ('din','Dinka'),
    ('dv','Divehi'),
    ('nl','Dutch'),
    ('dz','Dzongkha'),
    ('arz','Egyptian Arabic'),
    ('egl','Emilian'),
    ('en','English'),
    ('myv','Erzya'),
    ('eo','Esperanto'),
    ('et','Estonian'),
    ('eto','Eton'),
    ('evn','Evenki'),
    ('ee','Ewe'),
    ('ewo','Ewondo'),
    ('fo','Faroese'),
    ('hif','Fiji Hindi'),
    ('fj','Fijian'),
    ('fi','Finnish'),
    ('vls','Flemish'),
    ('frp','Franco-Provençal'),
    ('fr','French'),
    ('fur','Friulan'),
    ('ff','Fulah'),
    ('fzho','Fuzhou'),
    ('gl','Galician'),
    ('gan','Gan Chinese'),
    ('ka','Georgian'),
    ('de','German'),
    ('glk','Gilaki'),
    ('el','Greek'),
    ('gn','Guarani'),
    ('gu','Gujarati'),
    ('afb','Gulf Arabic'),
    ('guz','Gusii'),
    ('ht','Haitian Creole'),
    ('hak','Hakka'),
    ('mey','Hassaniyya'),
    ('ha','Hausa'),
    ('haw','Hawaiian'),
    ('he','Hebrew'),
    ('hz','Herero'),
    ('hil','Hiligaynon'),
    ('hi','Hindi'),
    ('ho','Hiri motu'),
    ('hmn','Hmong'),
    ('hu','Hungarian'),
    ('is','Icelandic'),
    ('ig','Igbo'),
    ('ilo','Iloko'),
    ('ind','Indonesian'),
    ('inh','Ingush'),
    ('ia','Interlingua'),
    ('iu','Inuktitut'),
    ('ik','Inupiaq'),
    ('ga','Irish'),
    ('it','Italian'),
    ('ibd','Iwaidja'),
    ('jam','Jamaican Patois'),
    ('ja','Japanese'),
    ('jv','Javanese'),
    ('cjy','Jin Chinese'),
    ('lad','Judeo-Spanish'),
    ('kbd','Kabardian'),
    ('kab','Kabyle'),
    ('kl','Kalaallisut'),
    ('xal','Kalmyk'),
    ('kn','Kannada'),
    ('kr','Kanuri'),
    ('krc','Karachay-Balkar'),
    ('kaa','Karakalpak'),
    ('ks','Kashmiri'),
    ('csb','Kashubian'),
    ('kk','Kazakh'),
    ('kca','Khanty'),
    ('kha','Khasi'),
    ('km','Khmer'),
    ('ki','Kikuyu'),
    ('kmb','Kimbundu'),
    ('rw','Kinyarwanda'),
    ('rn','Kirundi'),
    ('tlh','Klingon'),
    ('kv','Komi'),
    ('kg','Kongo'),
    ('gom','Konkani'),
    ('ko','Korean'),
    ('avk','Kotava'),
    ('kri','Krio'),
    ('kj','Kuanyama'),
    ('ku','Kurdish'),
    ('kmr','Kurmanji'),
    ('kfr','Kutchi'),
    ('ky','Kyrgyz'),
    ('lbe','Lak'),
    ('lkt','Lakota'),
    ('lo','Lao'),
    ('ltg','Latgalian'),
    ('la','Latin'),
    ('lv','Latvian'),
    ('lzz','Laz'),
    ('lez','Lezgian'),
    ('lij','Ligurian'),
    ('li','Limburgish'),
    ('ln','Lingala'),
    ('lt','Lithuanian'),
    ('lmo','Lombard'),
    ('lou','Louisiana Creole'),
    ('nds','Low German'),
    ('loz','Lozi'),
    ('lu','Luba-katanga'),
    ('lg','Luganda'),
    ('luo','Luo'),
    ('lut','Lushootseed'),
    ('lb','Luxembourgish'),
    ('mk','Macedonian'),
    ('vmf','Mainfränkisch'),
    ('mg','Malagasy'),
    ('ms','Malay'),
    ('ml','Malayalam'),
    ('mt','Maltese'),
    ('mnc','Manchu'),
    ('zh','Mandarin Chinese'),
    ('gv','Manx'),
    ('swb','Maore'),
    ('mi','Māori'),
    ('arn','Mapudungun'),
    ('mr','Marathi'),
    ('chm','Mari'),
    ('mh','Marshallese'),
    ('msb','Masbateño'),
    ('mfe','Mauritian Creole'),
    ('mzn','Mazandarani'),
    ('mfo','Mbe'),
    ('mni','Meitei'),
    ('pdt','Mennonite Low German'),
    ('apm','Mescalero-Chiricahua'),
    ('mic','Micmac'),
    ('cdo','Min Dong'),
    ('nan','Min Nan'),
    ('min','Minangkabau'),
    ('lrc','Minjaee Luri'),
    ('moh','Mohawk'),
    ('mdf','Moksha'),
    ('mo','Moldovan'),
    ('mn','Mongolian'),
    ('mos','Mossi'),
    ('wlc','Mwali'),
    ('nah','Nahuatl'),
    ('nsk','Naskapi'),
    ('na','Nauru'),
    ('nv','Navajo'),
    ('nxq','Naxi'),
    ('ng','Ndonga'),
    ('wni','Ndzwani'),
    ('nap','Neapolitan'),
    ('new','Nepal Bhasa'),
    ('ne','Nepali'),
    ('zdj','Ngazidja'),
    ('nog','Nogai'),
    ('apc','North Levantine Arabic'),
    ('nd','North Ndebele'),
    ('sme','Northern Sami'),
    ('no','Norwegian Bokmål'),
    ('nn','Norwegian Nynorsk'),
    ('ii','Nuosu'),
    ('ngh','Nǀuu'),
    ('oc','Occitan'),
    ('oj','Ojibwa'),
    ('ryu','Okinawan'),
    ('or','Oriya'),
    ('om','Oromo'),
    ('osa','Osage'),
    ('os','Ossetian'),
    ('ota','Ottoman Turkish'),
    ('pau','Palauan'),
    ('pln','Palenquero'),
    ('pi','Pali'),
    ('pag','Pangasinan'),
    ('pap','Papiamento'),
    ('ps','Pashto'),
    ('pdc','Pennsylvania Dutch'),
    ('fa','Persian'),
    ('pcd','Picard'),
    ('pms','Piedmontese'),
    ('pjt','Pitjantjatjara'),
    ('pl','Polish'),
    ('pt','Portuguese'),
    ('fuc','Pulaar'),
    ('pa','Punjabi'),
    ('qu','Quechua'),
    ('zpf','Quiatoni Zapotec'),
    ('rap','Rapa Nui'),
    ('rhg','Rohingya'),
    ('rgn','Romagnol'),
    ('rom','Romani'),
    ('ro','Romanian'),
    ('rm','Romansh'),
    ('cgg','Rukiga'),
    ('ru','Russian'),
    ('rue','Rusyn'),
    ('sm','Samoan'),
    ('sg','Sango'),
    ('sa','Sanskrit'),
    ('skr','Saraiki'),
    ('sc','Sardinian'),
    ('sco','Scots'),
    ('gd','Scottish Gaelic'),
    ('trv','Seediq'),
    ('sr','Serbian'),
    ('srr','Serer'),
    ('sn','Shona'),
    ('shh','Shoshone'),
    ('scn','Sicilian'),
    ('szl','Silesian'),
    ('sd','Sindhi'),
    ('si','Sinhalese'),
    ('sk','Slovak'),
    ('sl','Slovenian'),
    ('so','Somali'),
    ('st','Sotho'),
    ('nr','South Ndebele'),
    ('luz','Southern Luri'),
    ('es','Spanish'),
    ('srn','Sranan Tongo'),
    ('su','Sundanese'),
    ('swg','Swabian German'),
    ('sw','Swahili'),
    ('ss','Swati'),
    ('sv','Swedish'),
    ('gsw','Swiss German'),
    ('syl','Sylheti'),
    ('tl','Tagalog'),
    ('ty','Tahitian'),
    ('tg','Tajik'),
    ('tzl','Talossan'),
    ('tly','Talysh'),
    ('ta','Tamil'),
    ('tt','Tatar'),
    ('te','Telugu'),
    ('tet','Tetum'),
    ('th','Thai'),
    ('bo','Tibetan'),
    ('ti','Tigrinya'),
    ('tli','Tlingit'),
    ('tpi','Tok Pisin'),
    ('x-tp','Toki Pona'),
    ('tdn','Tondano'),
    ('to','Tongan'),
    ('ts','Tsonga'),
    ('tn','Tswana'),
    ('tmh','Tuareg'),
    ('yrk','Tundra Nenets'),
    ('tr','Turkish'),
    ('tk','Turkmen'),
    ('tus','Tuscarora'),
    ('tyv','Tuvan'),
    ('tw','Twi'),
    ('udm','Udmurt'),
    ('uk','Ukrainian'),
    ('hsb','Upper Sorbian'),
    ('ur','Urdu'),
    ('ug','Uyghur'),
    ('uz','Uzbek'),
    ('ve','Venda'),
    ('vec','Venetian'),
    ('vi','Vietnamese'),
    ('vo','Volapük'),
    ('vro','Võro'),
    ('wa','Walloon'),
    ('cy','Welsh'),
    ('fy','Western Frisian'),
    ('wo','Wolof'),
    ('wuu','Wu Chinese'),
    ('xh','Xhosa'),
    ('hsn','Xiang Chinese'),
    ('sah','Yakut'),
    ('yey','Yeyi'),
    ('yi','Yiddish'),
    ('yo','Yoruba'),
    ('yua','Yucatec Maya'),
    ('esu','Yupik'),
    ('zza','Zazaki'),
    ('za','Zhuang'),
    ('zu','Zulu')
]


GENDERS = [
    ('m', 'Male'),
    ('f', 'Female')
]

sex_mapping = {
    'Male': 'm',
    'Female': 'f'
}

class Forvo(Service):
    """
    Provides a Service-compliant implementation for Forvo.
    """

    __slots__ = []

    NAME = "Forvo"

    TRAITS = [Trait.INTERNET, Trait.DICTIONARY]

    def desc(self):
        """Returns a short, static description."""

        return "Forvo Pronunciation (%d voices)" % len(VOICES)

    def extras(self):
        """The Forvo API requires an API key."""

        return [dict(key='key', label="API Key", required=True)]

    def normalize_sex(self, input):
        self._logger.debug(f'normalize_sex called with {input}')
        (sex_code, description) = input
        return sex_code

    def options(self):
        """Provides access to voice only."""

        return [
            dict(
                key='voice',
                label="Voice",
                values=VOICES,
                default=('en', 'English'),
                transform=self.normalize,
            ),
            dict(
                key='sex',
                label="Sex",
                values=GENDERS,
                default=('m', 'Male'),
                transform=self.normalize_sex,
            )
        ]

    def run(self, text, options, path):
        self._logger.debug(f'running Forvo on text=[{text}], options={options}')

        api_key = options['key']
        if len(api_key) == 0:
            raise IOError('API Key required for Forvo')

        if len(text) > 100:
            raise IOError("Input text is too long for Forvo.")

        encoded_text = urllib.parse.quote(text)
        encoded_language = urllib.parse.quote(options['voice'])
        sex = options['sex']

        #url = f"https://apicorporate.forvo.com/api2/v1.1/d6a0d68b18fbcf26bcbb66ec20739492/word-pronunciations/word/{encoded_text}/language/{encoded_language}/order/rate-desc"
        url = f'https://apifree.forvo.com/key/{api_key}/format/json/action/word-pronunciations/word/{encoded_text}/language/{encoded_language}/sex/{sex}/order/rate-desc/limit/1'
        self._logger.debug(f'constructed URL: {url}')
        
        payload = self.net_stream(url)
        
        try:
            data = json.loads(payload)
        except ValueError:
            raise ValueError("Unable to interpret the response from Forvo API.")
            
        try:
            self._logger.debug(f'received data: {data}')
            audio_url = data['items'][0]['pathmp3']
        except KeyError:
            raise KeyError("Cannot find the audio URL in the response from the Forvo API.")
        except IndexError:
            raise IOError("Forvo doesn't have any audio for this input.")
    
        self.net_download(
            path,
            audio_url,
            require=dict(mime='audio/mpeg', size=512),
        )
