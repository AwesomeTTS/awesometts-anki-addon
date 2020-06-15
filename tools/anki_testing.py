# coding: utf-8
import shutil
import tempfile
from contextlib import contextmanager

import os

import sys
from warnings import warn

import aqt
from aqt import _run
from aqt import AnkiApp
from aqt.main import AnkiQt
from aqt.profiles import ProfileManager


"""
return AnkiQt handle, to be caled at beginning of test
"""
def get_anki_app():
    # mock some functions to avoid issues
    # ===================================

    # don't use the second instance mechanism, start a new instance every time
    def mock_secondInstance(ankiApp):
        return False

    AnkiApp.secondInstance = mock_secondInstance

    # prevent auto-updater code from running (it makes http requests)
    def mock_setupAutoUpdate(AnkiQt):
        pass

    AnkiQt.setupAutoUpdate = mock_setupAutoUpdate 

    # setup user profile in temp directory
    # ====================================

    lang="en_US"
    name="anonymous"

    # get temporary dir for profile
    tempdir = tempfile.TemporaryDirectory(suffix='anki')
    dir_name = tempdir.name

    # prevent popping up language selection dialog
    original = ProfileManager.setDefaultLang

    def set_default_lang(profileManager):
        profileManager.setLang(lang)

    ProfileManager.setDefaultLang = set_default_lang
    pm = ProfileManager(base=dir_name)
    pm.setupMeta()

    # create profile no matter what (since we are starting in a unique temp directory)
    pm.create(name)

    # this needs to be called explicitly
    pm.setDefaultLang()

    pm.name = name

    # run the app
    # ===========

    argv=["anki", "-p", name, "-b", dir_name]
    print(f'running anki with argv={argv}')
    app = _run(argv=argv, exec=False)

    return app


def destroy_anki_app():
    # clean up what was spoiled
    aqt.mw.cleanupAndExit()

    # remove hooks added during app initialization
    from anki import hooks
    hooks._hooks = {}

    # test_nextIvl will fail on some systems if the locales are not restored
    import locale
    locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())    
