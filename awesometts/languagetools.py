import os
import requests
import json

class LanguageTools:
    def __init__(self, api_key, logger, client_version):
        self.logger = logger
        self.base_url = 'https://cloudlanguagetools-api.vocab.ai'
        if 'ANKI_LANGUAGE_TOOLS_BASE_URL' in os.environ:
            self.base_url = os.environ['ANKI_LANGUAGE_TOOLS_BASE_URL']
        self.vocab_api_base_url = 'https://app.vocab.ai/languagetools-api/v2'
        self.api_key = api_key
        self.client_version = client_version
        self.trial_instant_signed_up = False
        self.api_key_verified = False
        self.use_vocabai_api = False

    def get_base_url(self):
        return self.base_url

    def set_api_key(self, api_key):
        self.api_key = api_key
        self.api_key_verified = False
        self.use_vocabai_api = False        

    def get_api_key(self):
        return self.api_key

    def use_plus_mode(self):
        return len(self.api_key) > 0

    def verify_api_key(self, api_key):
        # first , try to verify API key with vocab API
        response = requests.get(self.vocab_api_base_url + '/account', headers={'Authorization': f'Api-Key {api_key}'})
        if response.status_code == 200:
            # API key is valid on vocab API
            self.api_key = api_key
            self.api_key_verified = True
            self.use_vocabai_api = True
            return {
                'key_valid': True,
            }

        # now check with cloudlanguagetools API
        response = requests.get(self.base_url + '/account', headers={
            'api_key': api_key
        })
        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                return {
                    'key_valid': False,
                    'msg': data['error']
                }                    
            # key valid
            self.api_key = api_key
            self.api_key_verified = True
            self.use_vocabai_api = False
            return {
                'key_valid': True,
                'msg': f'api key: {api_key}'
            }
        
        # by default, key is invalid
        return {
            'key_valid': False,
            'msg': f'api key not valid'
        }
    
    def ensure_key_verified(self):
        if self.api_key == None:
            raise ValueError('API Key not set')
        if self.api_key_verified == False:
            self.verify_api_key(self.api_key)

    def account_info(self):
        self.ensure_key_verified()

        if self.use_vocabai_api:
            response = requests.get(self.vocab_api_base_url + '/account', headers={'Authorization': f'Api-Key {self.api_key}'})
        else:
            response = requests.get(self.base_url + '/account', headers={'api_key': self.api_key})
        data = json.loads(response.content)
        return data

    def request_trial_key(self, email):
        self.logger.info(f'requesting trial key for email {email}')
        response = requests.post(self.base_url + '/request_trial_key', json={'email': email})
        data = json.loads(response.content)
        self.logger.info(f'retrieved {data}')
        if 'api_key' in data:
            self.trial_instant_signed_up = True
        return data


    def generate_audio_v2(self, source_text, service, request_mode, language_code, deck_name, voice_key, options, path):
        self.ensure_key_verified()

        # query cloud language tools API
        data = {
            'text': source_text,
            'service': service,
            'request_mode': request_mode,
            'language_code': language_code,
            'deck_name': deck_name,
            'voice_key': voice_key,
            'options': options
        }

        if self.use_vocabai_api:
            headers={
                'Authorization': f'Api-Key {self.api_key}',
                'User-Agent': f'anki-awesometts/{self.client_version}',
            }
            full_url = self.vocab_api_base_url + '/audio'         
            response = requests.post(full_url, json=data, headers=headers)
        else:
            url_path = '/audio_v2'
            full_url = self.base_url + url_path
            self.logger.info(f'request url: {full_url}, data: {data}')
            response = requests.post(full_url, json=data, headers={'api_key': self.get_api_key(), 'client': 'awesometts', 'client_version': self.client_version})

        if response.status_code == 200:
            self.logger.info('success, receiving audio')
            with open(path, 'wb') as f:
                f.write(response.content)
        else:
            error_message = f"Status code: {response.status_code} ({response.content})"
            self.logger.error(error_message)
            raise ValueError(error_message)                    
