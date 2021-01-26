import os
import requests
import json

class LanguageTools:
    def __init__(self):
        self.base_url = 'https://cloud-language-tools-prod.anki.study'
        if 'ANKI_LANGUAGE_TOOLS_BASE_URL' in os.environ:
            self.base_url = os.environ['ANKI_LANGUAGE_TOOLS_BASE_URL']
        self.api_key_valid = False

    def verify_api_key(self, api_key):
        response = requests.post(self.base_url + '/verify_api_key', json={
            'api_key': api_key
        })
        data = json.loads(response.content)
        return data
