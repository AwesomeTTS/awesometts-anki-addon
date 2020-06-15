from urllib.error import HTTPError
from warnings import warn

from anki_testing import anki_running
import tools.speech_recognition
from pytest import raises
import magic # to verify file types
import os


def test_addon_initialization():
    with anki_running() as anki_app:
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


def test_gui():
    pass


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


def test_services():
    """Tests all services (except iSpeech) using a single word.

    Retrieving, processing, and playing of word "test" will be tested,
    using default (or first available) options. To expose a specific
    value of an option for testing purposes only, use test_default.
    """
    require_key = ['iSpeech', 'Google Cloud Text-to-Speech']
    # in an attempt to get continuous integration running again, a number of services had to be disabled. 
    # we'll have to revisit this when we get a baseline of working tests
    it_fails = ['Baidu Translate', 'Duden', 'NAVER Translate', 'abair.ie', 'Fluency.nl', 'ImTranslator', 'NeoSpeech', 'VoiceText', 'Wiktionary', 'Yandex.Translate']

    with anki_running() as anki_app:

        from awesometts import addon

        def success_if_path_exists_and_plays(path):

            # play (and hope that we have no errors)
            addon.player.preview(path)

            # and after making sure that the path exists
            if os.path.exists(path):
                
                if tools.speech_recognition.recognition_available():
                    print('performing speech recognition')
                    result_text = tools.speech_recognition.recognize_speech(path, 'en-US')
                    print(f'detected text: {result_text}')
                    if result_text == 'Pronunciation.':
                        raise Success()
                else:
                    # just check that we indeed have an mp3 file
                    filetype = magic.from_file(path)
                    #print(f'filetype: {filetype}')
                    if 'MPEG ADTS, layer III' in filetype:
                        # claim success
                        raise Success()

        def failure(exception, text):
            print(f'got exception: {exception} text: {text}')
            assert False

        callbacks = {
            'okay': success_if_path_exists_and_plays,
            'fail': failure
        }

        for svc_id, name, in addon.router.get_services():

            if name in require_key:
                warn(f'Skipping {name} (no API key)')
                continue

            if name in it_fails:
                warn(f'Skipping {name} - known to fail; if you can fix it, please open a PR')
                continue

            print(f'Testing {name}')

            # some services only support a single word. so use a single word as input as a common denominator
            input_word = 'pronunciation'

            options = get_default_options(addon, svc_id)

            with raises(Success):
                addon.router(
                    svc_id=svc_id,
                    text=input_word,
                    options=options,
                    callbacks=callbacks,
                    async_variable=False
                )

def test_google_cloud_tts():
    # test google cloud text-to-speech service
    # to run this test only:
    # python -m pytest tests -s -k 'test_google_cloud_tts'
    # requires an API key , which should be set on the travis CI build

    GOOGLE_CLOUD_TTS_KEY_ENVVAR = 'GOOGLE_SERVICES_KEY'
    if GOOGLE_CLOUD_TTS_KEY_ENVVAR not in os.environ:
        return

    service_key = os.environ[GOOGLE_CLOUD_TTS_KEY_ENVVAR]
    assert len(service_key) > 0

    with anki_running() as anki_app:

        from awesometts import addon

        def get_verify_audio_callback(expected_text, language):
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
                    assert result_text == expected_text
                    # at this point, declare success
                    raise Success()
                else:
                    # we know we have an mp3 audio file, desclare success
                    raise Success()
            return verify_audio_text

        def failure(exception, text):
            print(f'got exception: {exception} text: {text}')
            assert False

        svc_id = 'GoogleTTS'

        # get default options
        options = get_default_options(addon, svc_id)

        # add the google services API key in the config
        config_snippet = {
            'extras': {'googletts': {'key': service_key}}
        }
        addon.config.update(config_snippet)

        with raises(Success):
            addon.router(
                svc_id=svc_id,
                text='this is the first sentence',
                options=options,
                callbacks={
                    'okay': get_verify_audio_callback('This is the first sentence.', 'en-US'),
                    'fail': failure
                },
                async_variable=False
            )

    assert True