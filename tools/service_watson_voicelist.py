import os
import requests
import json

WATSON_SERVICES_KEY_ENVVAR_NAME = 'WATSON_SERVICES_KEY'

def get_voices(api_key):
    base_url = 'https://api.us-south.text-to-speech.watson.cloud.ibm.com/instances/7f62cf20-2944-4d83-bd53-b6f11a64de9b'
    url = base_url + '/v1/voices'
    result = requests.get(url, auth=('apikey', api_key))
    data = json.loads(result.content)
    #print(data)

    voices = data['voices']


    for entry in data['voices']:
        # print(entry)
        
        language_enum_name = entry['language'].replace('-', '_')
        if language_enum_name == 'ar_MS':
            language_enum_name = 'ar_AR'
        language_str = 'Language.' + language_enum_name
        gender_str = 'Gender.' + entry['gender'].capitalize()
        voice_name = entry['description'].split(':')[0]
        if 'Dnn' in entry['description']:
            voice_name += ' (Dnn)'
        watson_voice_formatted = f"WatsonVoice({language_str}, {gender_str}, '{entry['name']}', '{entry['description']}', '{voice_name}' ),"
        print(watson_voice_formatted)


if __name__ == '__main__':
    assert WATSON_SERVICES_KEY_ENVVAR_NAME in os.environ
    get_voices(os.environ[WATSON_SERVICES_KEY_ENVVAR_NAME])