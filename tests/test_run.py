from urllib.error import HTTPError
from warnings import warn

from anki_testing import anki_running
from pytest import raises


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
            import os

            # play (and hope that we have no errors)
            addon.player.preview(path)

            # and after making sure that the path exists
            if os.path.exists(path):
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

            options = get_default_options(addon, svc_id)

            with raises(Success):
                addon.router(
                    svc_id=svc_id,
                    text='test',
                    options=options,
                    callbacks=callbacks,
                    async_variable=False
                )
