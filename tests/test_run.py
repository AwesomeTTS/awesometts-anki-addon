from urllib.error import HTTPError
from warnings import warn

import tools.anki_testing
import tools.speech_recognition
from pytest import raises
import magic # to verify file types
import os
import sys

import logging as logger
logger.basicConfig(stream=sys.stdout, level=logger.DEBUG)


class Success(Exception):
    pass


def get_default_options(addon, svc_id):
    available_options = addon.router.get_options(svc_id)

    options = {}

    for option in available_options:
        key = option['key']
        if 'test_default' in option:
            value = option['test_default']
        elif 'default' in option:
            value = option['default']
        else:
            value = option['values'][0]
            if isinstance(value, tuple):
                value = value[0]
        options[key] = value

    return options

class TestClass():
    def setup_class(self):
        self.anki_app = tools.anki_testing.get_anki_app()
        from awesometts import addon
        self.addon = addon

    def teardown_class(self):
        tools.anki_testing.destroy_anki_app()


    def test_addon_initialization(self):
        import awesometts
        awesometts.browser_menus()     # mass generator and MP3 stripper
        awesometts.cache_control()     # automatically clear the media cache regularly
        awesometts.cards_button()      # on-the-fly templater helper in card view
        awesometts.config_menu()       # provides access to configuration dialog
        awesometts.editor_button()     # single audio clip generator button
        awesometts.reviewer_hooks()    # on-the-fly playback/shortcuts, context menus
        awesometts.sound_tag_delays()  # delayed playing of stored [sound]s in review
        awesometts.temp_files()        # remove temporary files upon session exit
        awesometts.update_checker()    # if enabled, runs the add-on update checker
        awesometts.window_shortcuts()  # enable/update shortcuts for add-on windows
        # if we didn't hit any exceptions at this point, declare success
        assert True


    def test_gui(self):
        pass


    def test_services(self):
        """Tests all services (except services which require an API key) using a single word.

        Retrieving, processing, and playing of word "successful" will be tested,
        using default (or first available) options. To expose a specific
        value of an option for testing purposes only, use test_default.
        """
        require_key = ['iSpeech', 'Google Cloud Text-to-Speech', 'Microsoft Azure']
        # in an attempt to get continuous integration running again, a number of services had to be disabled. 
        # we'll have to revisit this when we get a baseline of working tests
        it_fails = ['Baidu Translate', 'Duden', 'abair.ie', 'Fluency.nl', 'ImTranslator', 'NeoSpeech', 'VoiceText', 'Wiktionary', 'Yandex.Translate']

        for svc_id, name, in self.addon.router.get_services():

            if name in require_key:
                warn(f'Skipping {name} (no API key)')
                continue

            if name in it_fails:
                warn(f'Skipping {name} - known to fail; if you can fix it, please open a PR')
                continue

            print(f'Testing {name}')

            # some services only support a single word. so use a single word as input as a common denominator
            input_word = 'pronunciation'

            options = get_default_options(self.addon, svc_id)

            with raises(Success):
                self.addon.router(
                    svc_id=svc_id,
                    text=input_word,
                    options=options,
                    callbacks={
                        'okay': self.get_verify_audio_callback(input_word, 'en-US'),
                        'fail': self.get_failure_callback()
                    },
                    async_variable=False
                )

    def get_verify_audio_callback(self, expected_text, language):
        """
        Build and return a callback which compares the received audio against the expected text, in the specified language
        """

        def verify_audio_text(path):
            # make sure file exists
            assert os.path.exists(path)
            # get filetype by looking at file header
            filetype = magic.from_file(path)
            # should be an MP3 file
            assert 'MPEG ADTS, layer III' in filetype

            print(f'got file: {path}')

            # run this file through azure speech recognition
            if tools.speech_recognition.recognition_available():
                print('performing speech recognition')
                result_text = tools.speech_recognition.recognize_speech(path, language)
                print(f'detected text: {result_text}')
                # make sure it's what we expect
                # remove final ., 。 (for chinese) and lowercase
                processed_result = result_text.lower().replace('.', '').replace('。', '').replace('?', '')
                assert processed_result == expected_text
                # at this point, declare success
                raise Success()
            else:
                # we know we have an mp3 audio file, desclare success
                raise Success()
        return verify_audio_text

    def get_failure_callback(self):
        def failure(exception, text):
            print(f'got exception: {exception} text: {text}')
            assert False
        return failure

    def run_service_testcases(self, svc_id, test_cases):
        """
        a generic way to run a number of test cases for a given service
        """
        # get default options
        options = get_default_options(self.addon, svc_id)
        print(options)

        for test_case in test_cases:
            options['voice'] = test_case['voice']
            text_input = test_case['text_input']
            with raises(Success):
                self.addon.router(
                    svc_id=svc_id,
                    text=text_input,
                    options=options,
                    callbacks={
                        'okay': self.get_verify_audio_callback(text_input, test_case['recognition_language']),
                        'fail': self.get_failure_callback()
                    },
                    async_variable=False
                )        

    def test_google_cloud_tts(self):
        # test google cloud text-to-speech service
        # to run this test only:
        # python -m pytest tests -s -k 'test_google_cloud_tts'
        # requires an API key , which should be set on the travis CI build

        GOOGLE_CLOUD_TTS_KEY_ENVVAR = 'GOOGLE_SERVICES_KEY'
        if GOOGLE_CLOUD_TTS_KEY_ENVVAR not in os.environ:
            return

        service_key = os.environ[GOOGLE_CLOUD_TTS_KEY_ENVVAR]
        assert len(service_key) > 0

        svc_id = 'GoogleTTS'

        # get default options
        options = get_default_options(self.addon, svc_id)
        print(options)

        # add the google services API key in the config
        config_snippet = {
            'extras': {'googletts': {'key': service_key}}
        }
        self.addon.config.update(config_snippet)

        # generate audio files for all these test cases, then run them through the speech recognition API to make sure the output is correct
        test_cases = [
            {'voice': 'en-US-Wavenet-D', 'text_input': 'this is the first sentence', 'recognition_language':'en-US'},
            {'voice': 'en-GB-Standard-B', 'text_input': 'i want to save my stomach for veggie dumplings', 'recognition_language':'en-GB'},
            {'voice': 'fr-FR-Wavenet-B', 'text_input': 'ravi de vous rencontrer', 'recognition_language':'fr-FR'},
            {'voice': 'cmn-CN-Wavenet-B', 'text_input': '我试着每天都不去吃快餐', 'recognition_language':'zh-CN'},
        ]

        self.run_service_testcases(svc_id, test_cases)

    def test_azure(self):
        # test azure cognitive services API
        # to run this test only:
        # python -m pytest tests -s -k 'test_azure'
        # requires an API key , which should be set on the travis CI build

        AZURE_SERVICES_KEY_ENVVAR_NAME = 'AZURE_SERVICES_KEY'
        if AZURE_SERVICES_KEY_ENVVAR_NAME not in os.environ:
            return

        service_key = os.environ[AZURE_SERVICES_KEY_ENVVAR_NAME]
        assert len(service_key) > 0

        svc_id = 'Azure'

        # get default options
        options = get_default_options(self.addon, svc_id)
        print(options)

        # add the google services API key in the config
        config_snippet = {
            'extras': {'azure': {'key': service_key}}
        }
        self.addon.config.update(config_snippet)

        # generate audio files for all these test cases, then run them through the speech recognition API to make sure the output is correct
        test_cases = [
            {'voice': 'Microsoft Server Speech Text to Speech Voice (en-US, BenjaminRUS)', 'text_input': 'this is the first sentence', 'recognition_language':'en-US'},
            {'voice': 'Microsoft Server Speech Text to Speech Voice (fr-CH, Guillaume)', 'text_input': 'ravi de vous rencontrer', 'recognition_language':'fr-FR'},
            {'voice': 'Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoxiaoNeural)', 'text_input': '我试着每天都不去吃快餐', 'recognition_language':'zh-CN'},
        ]

        self.run_service_testcases(svc_id, test_cases)        


    def test_naver(self):
        # test Naver Translate service
        # to run this test only:
        # python -m pytest tests -s -k 'test_naver'

        svc_id = 'Naver'

        # generate audio files for all these test cases, then run them through the speech recognition API to make sure the output is correct
        test_cases = [
            {'voice': 'en', 'text_input': 'this is the first sentence', 'recognition_language':'en-US'},
            {'voice': 'ko', 'text_input': '여보세요', 'recognition_language':'ko-KR'},
            #{'voice': 'zh', 'text_input': '你好', 'recognition_language':'zh-CN'}, #chinese voice doesn't seem to work
            {'voice': 'ja', 'text_input': 'おはようございます', 'recognition_language':'ja-JP'},
        ]

        self.run_service_testcases(svc_id, test_cases)

    def test_youdao(self):
        # python -m pytest tests -s -k 'test_youdao'

        svc_id = 'Youdao'

        # generate audio files for all these test cases, then run them through the speech recognition API to make sure the output is correct
        test_cases = [
            {'voice': 'en', 'text_input': 'this is the first sentence', 'recognition_language':'en-US'},
            {'voice': 'jp', 'text_input': 'おはようございます', 'recognition_language':'ja-JP'},
        ]

        self.run_service_testcases(svc_id, test_cases)

    def test_oxford(self):
        # python -m pytest tests -s -k 'test_oxford'

        svc_id = 'Oxford'
        test_cases = [
            {'voice': 'en', 'text_input': 'successful', 'recognition_language':'en-US'},
        ]
        self.run_service_testcases(svc_id, test_cases)        

    def test_cambridge(self):
        # python -m pytest tests -s -k 'test_cambridge'
        svc_id = 'Cambridge'
        test_cases = [
            {'voice': 'en-GB', 'text_input': 'successful', 'recognition_language':'en-GB'},
            {'voice': 'en-US', 'text_input': 'congratulations', 'recognition_language':'en-US'},
        ]
        self.run_service_testcases(svc_id, test_cases)

    def test_collins(self):
        # python -m pytest tests -s -k 'test_collins'
        svc_id = 'Collins'
        test_cases = [
            {'voice': 'en', 'text_input': 'successful', 'recognition_language':'en-GB'},
            {'voice': 'fr', 'text_input': 'bonjour', 'recognition_language':'fr-FR'},
            #{'voice': 'de', 'text_input': 'entschuldigung', 'recognition_language':'de-DE'}, doesn't seem to work
            #{'voice': 'zh', 'text_input': '你好', 'recognition_language':'zh-CN'}, # doesn't seem to work
        ]
        self.run_service_testcases(svc_id, test_cases)


    def test_oddcast(self):
        # python -m pytest tests -s -k 'test_oddcast'
        svc_id = 'Oddcast'

        options = get_default_options(self.addon, svc_id)
        print(options)

        test_cases = [
            {'voice': 'en/steven', 'text_input': 'successful', 'recognition_language':'en-US'},
            {'voice': 'th/narisa', 'text_input': 'กรุงเทพฯ', 'recognition_language':'th-TH'},
        ]
        self.run_service_testcases(svc_id, test_cases)                        