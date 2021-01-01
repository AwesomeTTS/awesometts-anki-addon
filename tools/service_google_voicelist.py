import google.cloud.texttospeech

# pip install google-cloud-texttospeech
# export GOOGLE_APPLICATION_CREDENTIALS=/mnt/d/storage/dev/account_keys/cloudlanguagetools.json

def language_code_to_enum(language_code):
    override_map = {
        'ar-XA': 'ar_AR',
        'cmn-TW': 'zh_TW',
        'cmn-CN': 'zh_CN',
        'yue-HK': 'zh_HK'
    }
    if language_code in override_map:
        return override_map[language_code]
    language_enum_name = language_code.replace('-', '_')
    return language_enum_name

def main():
    client = google.cloud.texttospeech.TextToSpeechClient()
    voices = client.list_voices()

    result = []

    for voice in voices.voices:
        #result.append(GoogleVoice(voice))    
        google_language_code = voice.language_codes[0]
        language_enum_name = language_code_to_enum(google_language_code)
        gender_str = voice.ssml_gender.name.lower().capitalize()
        # print(voice)
        print(f"GoogleVoice(Language.{language_enum_name}, Gender.{gender_str}, '{voice.name}', '{google_language_code}'),")


if __name__ == '__main__':
    main()