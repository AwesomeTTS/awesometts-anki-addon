import os
import requests
import json

class LanguageTools:
    def __init__(self, api_key, logger, client_version):
        self.logger = logger
        self.base_url = 'https://cloud-language-tools-tts-prod.anki.study'
        if 'ANKI_LANGUAGE_TOOLS_BASE_URL' in os.environ:
            self.base_url = os.environ['ANKI_LANGUAGE_TOOLS_BASE_URL']
        self.api_key = api_key
        self.client_version = client_version

    def get_base_url(self):
        return self.base_url

    def set_api_key(self, api_key):
        self.api_key = api_key

    def get_api_key(self):
        return self.api_key

    def use_plus_mode(self):
        return len(self.api_key) > 0

    def verify_api_key(self, api_key):
        response = requests.post(self.base_url + '/verify_api_key', json={
            'api_key': api_key
        })
        data = json.loads(response.content)
        return data
    
    def account_info(self, api_key):
        response = requests.get(self.base_url + '/account', headers={'api_key': api_key})
        data = json.loads(response.content)
        return data

    def generate_audio(self, source_text, service, voice_key, options, path):
        # query cloud language tools API
        url_path = '/audio'
        full_url = self.base_url + url_path
        data = {
            'text': source_text,
            'service': service,
            'voice_key': voice_key,
            'options': options
        }
        self.logger.info(f'request url: {full_url}, data: {data}')
        response = requests.post(full_url, json=data, headers={'api_key': self.get_api_key()})

        if response.status_code == 200:
            self.logger.info('success, receiving audio')
            with open(path, 'wb') as f:
                f.write(response.content)
        else:
            error_message = f"Status code: {response.status_code} ({response.content})"
            self.logger.error(error_message)
            raise ValueError(error_message)        

    def generate_audio_v2(self, source_text, service, request_mode, language_code, deck_name, voice_key, options, path):
        # query cloud language tools API
        url_path = '/audio_v2'
        full_url = self.base_url + url_path
        data = {
            'text': source_text,
            'service': service,
            'request_mode': request_mode,
            'language_code': language_code,
            'deck_name': deck_name,
            'voice_key': voice_key,
            'options': options
        }
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
