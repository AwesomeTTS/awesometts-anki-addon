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
import requests

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

COUNTRIES = [
('ANY', 'Any (pick best rated pronunciation)'),
('AFG','Afghanistan'),
('ALA','Åland Islands'),
('ALB','Albania'),
('DZA','Algeria'),
('ASM','American Samoa'),
('AND','Andorra'),
('AGO','Angola'),
('AIA','Anguilla'),
('ATA','Antarctica'),
('ATG','Antigua and Barbuda'),
('ARG','Argentina'),
('ARM','Armenia'),
('ABW','Aruba'),
('AUS','Australia'),
('AUT','Austria'),
('AZE','Azerbaijan'),
('BHS','Bahamas'),
('BHR','Bahrain'),
('BGD','Bangladesh'),
('BRB','Barbados'),
('BLR','Belarus'),
('BEL','Belgium'),
('BLZ','Belize'),
('BEN','Benin'),
('BMU','Bermuda'),
('BTN','Bhutan'),
('BOL','Bolivia (Plurinational State of)'),
('BES', 'Bonaire, Sint Eustatius and Saba'),
('BIH','Bosnia and Herzegovina'),
('BWA','Botswana'),
('BVT','Bouvet Island'),
('BRA','Brazil'),
('IOT','British Indian Ocean Territory'),
('BRN','Brunei Darussalam'),
('BGR','Bulgaria'),
('BFA','Burkina Faso'),
('BDI','Burundi'),
('CPV','Cabo Verde'),
('KHM','Cambodia'),
('CMR','Cameroon'),
('CAN','Canada'),
('CYM','Cayman Islands'),
('CAF','Central African Republic'),
('TCD','Chad'),
('CHL','Chile'),
('CHN','China'),
('CXR','Christmas Island'),
('CCK','Cocos (Keeling) Islands'),
('COL','Colombia'),
('COM','Comoros'),
('COG','Congo'),
('COD','Congo, Democratic Republic of the'),
('COK','Cook Islands'),
('CRI','Costa Rica'),
('CIV','Côte d\'Ivoire'),
('HRV','Croatia'),
('CUB','Cuba'),
('CUW','Curaçao'),
('CYP','Cyprus'),
('CZE','Czechia'),
('DNK','Denmark'),
('DJI','Djibouti'),
('DMA','Dominica'),
('DOM','Dominican Republic'),
('ECU','Ecuador'),
('EGY','Egypt'),
('SLV','El Salvador'),
('GNQ','Equatorial Guinea'),
('ERI','Eritrea'),
('EST','Estonia'),
('SWZ','Eswatini'),
('ETH','Ethiopia'),
('FLK','Falkland Islands (Malvinas)'),
('FRO','Faroe Islands'),
('FJI','Fiji'),
('FIN','Finland'),
('FRA','France'),
('GUF','French Guiana'),
('PYF','French Polynesia'),
('ATF','French Southern Territories'),
('GAB','Gabon'),
('GMB','Gambia'),
('GEO','Georgia'),
('DEU','Germany'),
('GHA','Ghana'),
('GIB','Gibraltar'),
('GRC','Greece'),
('GRL','Greenland'),
('GRD','Grenada'),
('GLP','Guadeloupe'),
('GUM','Guam'),
('GTM','Guatemala'),
('GGY','Guernsey'),
('GIN','Guinea'),
('GNB','Guinea-Bissau'),
('GUY','Guyana'),
('HTI','Haiti'),
('HMD','Heard Island and McDonald Islands'),
('VAT','Holy See'),
('HND','Honduras'),
('HKG','Hong Kong'),
('HUN','Hungary'),
('ISL','Iceland'),
('IND','India'),
('IDN','Indonesia'),
('IRN','Iran (Islamic Republic of)'),
('IRQ','Iraq'),
('IRL','Ireland'),
('IMN','Isle of Man'),
('ISR','Israel'),
('ITA','Italy'),
('JAM','Jamaica'),
('JPN','Japan'),
('JEY','Jersey'),
('JOR','Jordan'),
('KAZ','Kazakhstan'),
('KEN','Kenya'),
('KIR','Kiribati'),
('PRK','Korea (Democratic People\'s Republic of)'),
('KOR','Korea, Republic of'),
('KWT','Kuwait'),
('KGZ','Kyrgyzstan'),
('LAO','Lao People\'s Democratic Republic'),
('LVA','Latvia'),
('LBN','Lebanon'),
('LSO','Lesotho'),
('LBR','Liberia'),
('LBY','Libya'),
('LIE','Liechtenstein'),
('LTU','Lithuania'),
('LUX','Luxembourg'),
('MAC','Macao'),
('MDG','Madagascar'),
('MWI','Malawi'),
('MYS','Malaysia'),
('MDV','Maldives'),
('MLI','Mali'),
('MLT','Malta'),
('MHL','Marshall Islands'),
('MTQ','Martinique'),
('MRT','Mauritania'),
('MUS','Mauritius'),
('MYT','Mayotte'),
('MEX','Mexico'),
('FSM','Micronesia (Federated States of)'),
('MDA','Moldova, Republic of'),
('MCO','Monaco'),
('MNG','Mongolia'),
('MNE','Montenegro'),
('MSR','Montserrat'),
('MAR','Morocco'),
('MOZ','Mozambique'),
('MMR','Myanmar'),
('NAM','Namibia'),
('NRU','Nauru'),
('NPL','Nepal'),
('NLD','Netherlands'),
('NCL','New Caledonia'),
('NZL','New Zealand'),
('NIC','Nicaragua'),
('NER','Niger'),
('NGA','Nigeria'),
('NIU','Niue'),
('NFK','Norfolk Island'),
('MKD','North Macedonia'),
('MNP','Northern Mariana Islands'),
('NOR','Norway'),
('OMN','Oman'),
('PAK','Pakistan'),
('PLW','Palau'),
('PSE','Palestine, State of'),
('PAN','Panama'),
('PNG','Papua New Guinea'),
('PRY','Paraguay'),
('PER','Peru'),
('PHL','Philippines'),
('PCN','Pitcairn'),
('POL','Poland'),
('PRT','Portugal'),
('PRI','Puerto Rico'),
('QAT','Qatar'),
('REU','Réunion'),
('ROU','Romania'),
('RUS','Russian Federation'),
('RWA','Rwanda'),
('BLM','Saint Barthélemy'),
('SHN','Saint Helena, Ascension and Tristan da Cunha'),
('KNA','Saint Kitts and Nevis'),
('LCA','Saint Lucia'),
('MAF','Saint Martin (French part)'),
('SPM','Saint Pierre and Miquelon'),
('VCT','Saint Vincent and the Grenadines'),
('WSM','Samoa'),
('SMR','San Marino'),
('STP','Sao Tome and Principe'),
('SAU','Saudi Arabia'),
('SEN','Senegal'),
('SRB','Serbia'),
('SYC','Seychelles'),
('SLE','Sierra Leone'),
('SGP','Singapore'),
('SXM','Sint Maarten (Dutch part)'),
('SVK','Slovakia'),
('SVN','Slovenia'),
('SLB','Solomon Islands'),
('SOM','Somalia'),
('ZAF','South Africa'),
('SGS','South Georgia and the South Sandwich Islands'),
('SSD','South Sudan'),
('ESP','Spain'),
('LKA','Sri Lanka'),
('SDN','Sudan'),
('SUR','Suriname'),
('SJM','Svalbard and Jan Mayen'),
('SWE','Sweden'),
('CHE','Switzerland'),
('SYR','Syrian Arab Republic'),
('TWN','Taiwan'),
('TJK','Tajikistan'),
('TZA','Tanzania, United Republic of'),
('THA','Thailand'),
('TLS','Timor-Leste'),
('TGO','Togo'),
('TKL','Tokelau'),
('TON','Tonga'),
('TTO','Trinidad and Tobago'),
('TUN','Tunisia'),
('TUR','Turkey'),
('TKM','Turkmenistan'),
('TCA','Turks and Caicos Islands'),
('TUV','Tuvalu'),
('UGA','Uganda'),
('UKR','Ukraine'),
('ARE','United Arab Emirates'),
('GBR','United Kingdom of Great Britain and Northern Ireland'),
('USA','United States of America'),
('UMI','United States Minor Outlying Islands'),
('URY','Uruguay'),
('UZB','Uzbekistan'),
('VUT','Vanuatu'),
('VEN','Venezuela (Bolivarian Republic of)'),
('VNM','Viet Nam'),
('VGB','Virgin Islands (British)'),
('VIR','Virgin Islands (U.S.)'),
('WLF','Wallis and Futuna'),
('ESH','Western Sahara'),
('YEM','Yemen'),
('ZMB','Zambia'),
('Zimbabwe','ZWE')
]

GENDERS = [
    ('m', 'Male'),
    ('f', 'Female'),
    ('any', 'Any')
]

PREFERRED_USER_DEFAULT_KEY = 'any'
PREFERRED_USER_DEFAULT = (PREFERRED_USER_DEFAULT_KEY, "Any")

URL_API_CORPORATE = ('apicorporate', 'https://apicorporate.forvo.com/api2/v1.1/')
URL_API_FREE = ('apifree', 'https://apifree.forvo.com/')
URL_API_COMMERCIAL = ('apicommercial', 'https://apicommercial.forvo.com/')

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
        if self.languagetools.use_plus_mode():
            # plus mode, no need for an API key
            return []

        return [
            dict(key='key', label="API Key", required=True)
        ]

    def normalize_sex(self, input):
        self._logger.debug(f'normalize_sex called with {input}')
        if isinstance(input, tuple):
            (sex_code, description) = input
            return sex_code
        else:
            return input

    def normalize_country(self, input):
        if isinstance(input, tuple):
            (country_code, description) = input
            return country_code
        else:
            return input

    def normalize_apiurl(self, input):
        if isinstance(input, tuple):
            (code, description) = input
            return code
        else:
            return input            

    def get_preferred_users(self):
        default = [
            PREFERRED_USER_DEFAULT
        ]
        preferred_users = self.config['service_forvo_preferred_users'].split(',')
        preferred_users = [x.strip() for x in preferred_users]
        users_array = [(x, x) for x in preferred_users]
        return default + users_array

    def options(self):
        """Provides access to voice only."""

        result = [
            dict(
                key='voice',
                label="Voice",
                values=VOICES,
                default='en',
                transform=self.normalize,
            ),
            dict(
                key='sex',
                label="Sex",
                values=GENDERS,
                default=('any', 'Any'),
                transform=self.normalize_sex
            ),
            dict(
                key='country',
                label="Country",
                values=COUNTRIES,
                default=('ANY', 'Any (pick best rated pronunciation)'),
                transform=self.normalize_country
            ),
            dict(
                key='preferreduser',
                label="Preferred User",
                values=self.get_preferred_users(),
                default=PREFERRED_USER_DEFAULT,
                transform=self.normalize
            )
        ]

        if not self.languagetools.use_plus_mode():
            result.append(dict(
                key='apiurl',
                label='API URL',
                values=[URL_API_FREE, URL_API_COMMERCIAL, URL_API_CORPORATE],
                default=URL_API_FREE,
                transform=self.normalize_apiurl
            ))        

        return result

    def get_language_code_from_forvo_lang(self, forvo_lang):
        forvo_language_id_map = {
            'zh': 'zh_cn',
            'ind': 'id_',
            'pt': 'pt_pt'
        }
        return forvo_language_id_map.get(forvo_lang, forvo_lang)

    def run(self, text, options, path):
        self._logger.debug(f'running Forvo on text=[{text}], options={options}')

        if self.languagetools.use_plus_mode():
            self._logger.info(f'using language tools API')

            sex = options['sex']
            country_code = options['country']
            forvo_language_code = options['voice']
            preferred_user = options['preferreduser']

            service = 'Forvo'
            voice_key = {
                'language_code': forvo_language_code,
                'country_code': country_code
            }
            if sex != 'any':
                voice_key['gender'] = sex
            if preferred_user != PREFERRED_USER_DEFAULT_KEY:
                voice_key['preferred_user'] = preferred_user

            languagetools_language_code = self.get_language_code_from_forvo_lang(forvo_language_code)
            self.languagetools.generate_audio_v2(text, service, 'batch', languagetools_language_code, 'n/a', voice_key, {}, path)
        else:

            api_key = options['key']
            if len(api_key) == 0:
                raise IOError('API Key required for Forvo')

            if len(text) > 100:
                raise IOError("Input text is too long for Forvo.")

            encoded_text = urllib.parse.quote(text)
            encoded_language = urllib.parse.quote(options['voice'])
            sex = options['sex']
            preferred_user = options['preferreduser']

            country_code = ''
            if options['country'] != 'ANY':
                # user selected a particular country
                country_code = f"/country/{options['country']}"

            username_param = ''
            if preferred_user != PREFERRED_USER_DEFAULT_KEY:
                username_param = f"/username/{preferred_user}"

            sex_param = ''
            if sex != 'any':
                sex_param = f"/sex/{sex}"

            url_base = 'apifree.forvo.com'
            if options['apiurl'] == URL_API_COMMERCIAL[0]:
                url_base = 'apicommercial.forvo.com'

            url = f'https://{url_base}/key/{api_key}/format/json/action/word-pronunciations/word/{encoded_text}/language/{encoded_language}{sex_param}{username_param}/order/rate-desc/limit/10{country_code}'

            corporate_url = False
            if options['apiurl'] == URL_API_CORPORATE[0]:
                corporate_url = True
                url = f'https://apicorporate.forvo.com/api2/v1.1/{api_key}/word-pronunciations/word/{encoded_text}/language/{encoded_language}{sex_param}/order/rate-desc/limit/1{country_code}'

            self._logger.debug(f'constructed URL: {url}')

            # run request
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'}
            response = requests.get(url, headers=headers)
            self._logger.debug(f'response.content: {response.content}')

            if response.status_code == 200:
                # success
                data = json.loads(response.content)
                self._logger.debug(f'received data: {data}')
                if corporate_url:
                    items = data['data']['items']
                else:
                    items = data['items']
                if len(items) == 0:
                    message = f"Pronunciation not found in Forvo for word [{text}], language={options['voice']}, sex={sex}, country={options['country']}"
                    raise IOError(message)
                audio_url = items[0]['pathmp3']
                for item in items:
                    if item['word'] == text:
                        audio_url = item['pathmp3']
                        break
                self.net_download(
                    path,
                    audio_url,
                    require=dict(mime='audio/mpeg', size=512),
                )            
            else:
                data = json.loads(response.content)
                error_text = str(data)
                if len(data) >= 1:
                    error_text = data[0]
                error_message = f"Status code: {response.status_code} error: {error_text} text: [{text}] voice: {options['voice']} gender: {sex}"
                self._logger.error(error_message)
                raise ValueError(error_message)
        
