# coding: utf-8
import shutil
import tempfile
from contextlib import contextmanager

import os

import sys
from warnings import warn

sys.path.insert(0, 'anki_root')

import aqt
from aqt import _run
from aqt.profiles import ProfileManager


@contextmanager
def temporary_user(dir_name, name="__Temporary Test User__", lang="en_US"):

    # prevent popping up language selection dialog
    original = ProfileManager._setDefaultLang

    def set_default_lang(profileManager):
        profileManager.setLang(lang)

    ProfileManager._setDefaultLang = set_default_lang

    pm = ProfileManager(base=dir_name)

    if name in pm.profiles():
        warn(f"Temporary user named {name} already exists")
    else:
        pm.create(name)

    pm.name = name

    yield name

    pm.remove(name)
    ProfileManager._setDefaultLang = original


@contextmanager
def temporary_dir(name):
    path = os.path.join(tempfile.gettempdir(), name)
    yield path
    shutil.rmtree(path)


@contextmanager
def anki_running():

    # we need a new user for the test
    with temporary_dir("anki_temp_base") as dir_name:
        with temporary_user(dir_name) as user_name:
            app = _run(argv=["anki", "-p", user_name, "-b", dir_name], exec=False)
            yield app

    # clean up what was spoiled
    aqt.mw.cleanupAndExit()

    # remove hooks added during app initialization
    from anki import hooks
    hooks._hooks = {}

    # test_nextIvl will fail on some systems if the locales are not restored
    import locale
    locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())

