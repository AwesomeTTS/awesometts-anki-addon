import os
import requests
import json

class LanguageTools:
    def __init__(self, api_key):
        self.base_url = 'https://cloud-language-tools-prod.anki.study'
        if 'ANKI_LANGUAGE_TOOLS_BASE_URL' in os.environ:
            self.base_url = os.environ['ANKI_LANGUAGE_TOOLS_BASE_URL']
        self.api_key = api_key

    def set_api_key(self, api_key):
        self.api_key = api_key

    def use_plus_mode(self):
        return len(self.api_key) > 0

    def verify_api_key(self, api_key):
        response = requests.post(self.base_url + '/verify_api_key', json={
            'api_key': api_key
        })
        data = json.loads(response.content)
        return data
