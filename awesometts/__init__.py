# -*- coding: utf-8 -*-

# AwesomeTTS text-to-speech add-on for Anki
# Copyright (C) 2010-Present  Anki AwesomeTTS Development Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Add-on package initialization
"""

from os.path import join
import os
import sys
from time import time

import PyQt5

from PyQt5.QtCore import PYQT_VERSION_STR, Qt
from PyQt5.QtGui import QKeySequence

import anki
import aqt

from . import conversion as to, gui, paths, service
from .bundle import Bundle
from .config import Config
from .player import Player
from .router import Router
from .text import Sanitizer
from .ttsplayer import register_tts_player
from .languagetools import LanguageTools
from .version import AWESOMETTS_VERSION

__all__ = ['browser_menus', 'cards_button', 'config_menu', 'editor_button',
           'reviewer_hooks', 
           'window_shortcuts']


def get_platform_info():
    """Exception-tolerant platform information for use with AGENT."""

    implementation = system_description = "???"
    python_version = "?.?.?"

    try:
        import platform
    except:  # catch-all, pylint:disable=bare-except
        pass
    else:
        try:
            implementation = platform.python_implementation()
        except:  # catch-all, pylint:disable=bare-except
            pass

        try:
            python_version = platform.python_version()
        except:  # catch-all, pylint:disable=bare-except
            pass

        try:
            system_description = platform.platform().replace('-', ' ')
        except:  # catch-all, pylint:disable=bare-except
            pass

    return "%s %s; %s" % (implementation, python_version, system_description)

VERSION = AWESOMETTS_VERSION

WEB = 'https://github.com/AwesomeTTS/awesometts-anki-addon'

AGENT = 'AwesomeTTS/%s (Anki %s; PyQt %s; %s)' % (VERSION, anki.version,
                                                  PYQT_VERSION_STR,
                                                  get_platform_info())


# Begin core class initialization and dependency setup, pylint:disable=C0103

if 'AWESOMETTS_DEBUG_LOGGING' in os.environ:
    import logging 
    import io
    # on windows, some special characters can't be printed, replace them with ?
    if not hasattr(sys, '_pytest_mode'):
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), sys.stdout.encoding, 'replace')
    if os.environ['AWESOMETTS_DEBUG_LOGGING'] == 'enable':
        logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', 
                            datefmt='%Y%m%d-%H:%M:%S',
                            stream=sys.stdout, 
                            level=logging.DEBUG)
    elif os.environ['AWESOMETTS_DEBUG_LOGGING'] == 'file':
        filename = os.environ['AWESOMETTS_DEBUG_FILE']
        logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', 
                            datefmt='%Y%m%d-%H:%M:%S',
                            filename=filename, 
                            level=logging.DEBUG)        
    logger = logging.getLogger('awesometts')
    logger.setLevel(logging.DEBUG)
else:
    logger = Bundle(debug=lambda *a, **k: None, error=lambda *a, **k: None,
                    info=lambda *a, **k: None, warn=lambda *a, **k: None)

sequences = {key: QKeySequence()
             for key in ['browser_generator', 'browser_stripper',
                         'configurator', 'editor_generator', 'templater']}

config = Config(
    db=Bundle(path=paths.CONFIG,
              table='general',
              normalize=to.normalized_ascii),
    cols=[
        ('cache_days', 'integer', 365, int, int),
        ('ellip_note_newlines', 'integer', False, to.lax_bool, int),
        ('ellip_template_newlines', 'integer', False, to.lax_bool, int),
        ('extras', 'text', {}, to.deserialized_dict, to.compact_json),
        ('filenames', 'text', 'hash', str, str),
        ('filenames_human', 'text',
         '{{text}} ({{service}} {{voice}})', str, str),
        ('groups', 'text', {}, to.deserialized_dict, to.compact_json),
        ('homescreen_last_preset', 'text', '', str, str),
        ('homescreen_show', 'integer', True, to.lax_bool, int),
        ('lame_flags', 'text', '--quiet -q 2', str, str),
        ('last_mass_append', 'integer', True, to.lax_bool, int),
        ('last_mass_behavior', 'integer', True, to.lax_bool, int),
        ('last_mass_dest', 'text', 'Back', str, str),
        ('last_mass_source', 'text', 'Front', str, str),
        ('last_options', 'text', {}, to.deserialized_dict, to.compact_json),
        ('last_service', 'text', ('sapi5js' if 'win32' in sys.platform
                                  else 'say' if 'darwin' in sys.platform
                                  else 'yandex'), str, str),
        ('last_strip_mode', 'text', 'ours', str, str),
        ('launch_browser_generator', 'integer', Qt.ControlModifier | Qt.Key_T,
         to.nullable_key, to.nullable_int),
        ('launch_browser_stripper', 'integer', None, to.nullable_key,
         to.nullable_int),
        ('launch_configurator', 'integer', Qt.ControlModifier | Qt.Key_T,
         to.nullable_key, to.nullable_int),
        ('launch_editor_generator', 'integer', Qt.ControlModifier | Qt.Key_T,
         to.nullable_key, to.nullable_int),
        ('launch_templater', 'integer', Qt.ControlModifier | Qt.Key_T,
         to.nullable_key, to.nullable_int),
        ('otf_only_revealed_cloze', 'integer', False, to.lax_bool, int),
        ('otf_remove_hints', 'integer', False, to.lax_bool, int),
        ('plus_api_key', 'text', '', str, str),
        ('presets', 'text', {}, to.deserialized_dict, to.compact_json),
        ('service_azure_sleep_time', 'integer', 0, int, int),
        ('service_forvo_preferred_users', 'text', '', str, str),
        ('spec_note_count', 'text', '', str, str),
        ('spec_note_count_wrap', 'integer', True, to.lax_bool, int),
        ('spec_note_ellipsize', 'text', '', str, str),
        ('spec_note_strip', 'text', '', str, str),
        ('spec_template_count', 'text', '', str, str),
        ('spec_template_count_wrap', 'integer', True, to.lax_bool, int),
        ('spec_template_ellipsize', 'text', '', str, str),
        ('spec_template_strip', 'text', '', str, str),
        ('strip_note_braces', 'integer', False, to.lax_bool, int),
        ('strip_note_brackets', 'integer', False, to.lax_bool, int),
        ('strip_note_parens', 'integer', False, to.lax_bool, int),
        ('strip_template_braces', 'integer', False, to.lax_bool, int),
        ('strip_template_brackets', 'integer', False, to.lax_bool, int),
        ('strip_template_parens', 'integer', False, to.lax_bool, int),
        ('strip_ruby_tags', 'integer', True, to.lax_bool, int),
        ('sub_note_cloze', 'text', 'anki', str, str),
        ('sub_template_cloze', 'text', 'anki', str, str),
        ('sub_note_xml_entities', 'integer', False, to.lax_bool, int),
        ('sub_template_xml_entities', 'integer', False, to.lax_bool, int),
        ('sul_note', 'text', [], to.substitution_list, to.substitution_json),
        ('sul_template', 'text', [], to.substitution_list,
         to.substitution_json),
        ('throttle_sleep', 'integer', 30, int, int),
        ('throttle_threshold', 'integer', 10, int, int),
        ('tts_voices', 'text', {}, to.deserialized_dict, to.compact_json),
    ],
    logger=logger,
    events=[
    ],
)

languagetools = LanguageTools(config['plus_api_key'], logger, VERSION)

try:
    from aqt.sound import av_player
    from anki.sound import SoundOrVideoTag

    def append_file(self, filename: str) -> None:
        self._enqueued.append(SoundOrVideoTag(filename=filename))
        self._play_next_if_idle()

    anki.sound.play = lambda filename: append_file(av_player, filename)
except ImportError:
    pass

player = Player(
    anki=Bundle(
        mw=aqt.mw,
        native=anki.sound.play,  # need direct reference, as this gets wrapped
        sound=anki.sound,  # for accessing queue member, which is not wrapped
    ),
    blank=paths.BLANK,
    config=config,
    logger=logger,
)

router = Router(
    services=Bundle(
        mappings=[
            ('amazon', service.Amazon),
            ('azure', service.Azure),
            ('baidu', service.Baidu),
            ('cambridge', service.Cambridge),
            ('cereproc', service.CereProc),
            ('collins', service.Collins),
            ('duden', service.Duden),
            ('ekho', service.Ekho),
            ('espeak', service.ESpeak),
            ('festival', service.Festival),
            ('fptai', service.FptAi),
            ('google', service.Google),
            ('googletts', service.GoogleTTS),
            ('ispeech', service.ISpeech),
            ('naver', service.Naver),
            ('naverclova', service.NaverClova),
            ('naverclovapremium', service.NaverClovaPremium),
            ('oddcast', service.Oddcast),
            ('oxford', service.Oxford),
            ('pico2wave', service.Pico2Wave),
            ('rhvoice', service.RHVoice),
            ('sapi5com', service.SAPI5COM),
            ('sapi5js', service.SAPI5JS),
            ('say', service.Say),
            ('spanishdict', service.SpanishDict),
            ('yandex', service.Yandex),
            ('youdao', service.Youdao),
            ('forvo', service.Forvo),
            ('vocalware', service.VocalWare),
            ('watson', service.Watson)
        ],
        dead=dict(
            ttsapicom="TTS-API.com has gone offline and can no longer be "
                      "used. Please switch to another service with English.",
        ),
        aliases=[('b', 'baidu'), ('g', 'google'), ('macosx', 'say'),
                 ('microsoft', 'sapi5js'), ('microsoftjs', 'sapi5js'),
                 ('microsoftjscript', 'sapi5js'), ('oed', 'oxford'),
                 ('osx', 'say'), ('sapi', 'sapi5js'), ('sapi5', 'sapi5js'),
                 ('sapi5jscript', 'sapi5js'), ('sapijs', 'sapi5js'),
                 ('sapijscript', 'sapi5js'), ('svox', 'pico2wave'),
                 ('svoxpico', 'pico2wave'), ('ttsapi', 'ttsapicom'),
                 ('windows', 'sapi5js'), ('windowsjs', 'sapi5js'),
                 ('windowsjscript', 'sapi5js'), ('y', 'yandex')],
        normalize=to.normalized_ascii,
        args=(),
        kwargs=dict(temp_dir=paths.TEMP,
                    lame_flags=lambda: config['lame_flags'],
                    normalize=to.normalized_ascii,
                    logger=logger,
                    ecosystem=Bundle(web=WEB, agent=AGENT),
                    languagetools=languagetools,
                    config=config),
    ),
    cache_dir=paths.CACHE,
    temp_dir=join(paths.TEMP, '_awesometts_scratch_' + str(int(time()))),
    logger=logger,
    config=config,
)


STRIP_TEMPLATE_POSTHTML = [
    'whitespace',
    'sounds_univ',
    'filenames',
    ('within_parens', 'strip_template_parens'),
    ('within_brackets', 'strip_template_brackets'),
    ('within_braces', 'strip_template_braces'),
    ('char_remove', 'spec_template_strip'),
    ('counter', 'spec_template_count', 'spec_template_count_wrap'),
    ('char_ellipsize', 'spec_template_ellipsize'),
    ('custom_sub', 'sul_template'),
    'ellipses',
    'whitespace',
]

def bundlefail(message, text="Not available by addon.Bundle.downloader.fail"):
    aqt.utils.showCritical(message, aqt.mw)

addon = Bundle(
    config=config,
    downloader=Bundle(
        base=aqt.addons.GetAddons,
        superbase=aqt.addons.GetAddons.__bases__[0],
        args=[aqt.mw],
        kwargs=dict(),
        attrs=dict(
            form=Bundle(
                code=Bundle(text=lambda: '301952613'),
            ),
            mw=aqt.mw,
        ),
        fail=bundlefail,
    ),
    language=service.languages.Language,
    languagetools=languagetools,
    logger=logger,
    paths=Bundle(cache=paths.CACHE,
                 is_link=paths.ADDON_IS_LINKED),
    player=player,
    router=router,
    strip=Bundle(
        # n.b. cloze substitution logic happens first in both modes because:
        # - we need the <span>...</span> markup in on-the-fly to identify it
        # - Anki won't recognize cloze w/ HTML beginning/ending within braces
        # - the following 'html' rule will cleanse the HTML out anyway

        # for content directly from a note field (e.g. BrowserGenerator runs,
        # prepopulating a modal input based on some note field, where cloze
        # placeholders are still in their unprocessed state)
        from_note=Sanitizer([
            ('ruby_tags', 'strip_ruby_tags'),
            ('clozes_braced', 'sub_note_cloze'),
            ('newline_ellipsize', 'ellip_note_newlines'),
            'html',
            'whitespace',
            'sounds_univ',
            'filenames',
            ('within_parens', 'strip_note_parens'),
            ('within_brackets', 'strip_note_brackets'),
            ('within_braces', 'strip_note_braces'),
            ('char_remove', 'spec_note_strip'),
            ('counter', 'spec_note_count', 'spec_note_count_wrap'),
            ('char_ellipsize', 'spec_note_ellipsize'),
            ('custom_sub', 'sul_note'),
            'ellipses',
            'whitespace',
            ('xml_entities', 'sub_note_xml_entities')
        ], config=config, logger=logger),

        # clean up fields coming from templates (on the fly TTS)
        from_template=Sanitizer([
            ('ruby_tags', 'strip_ruby_tags'),
            ('clozes_rendered', 'sub_template_cloze'),
            ('clozes_revealed', 'otf_only_revealed_cloze'),
            'hint_links',
            ('hint_content', 'otf_remove_hints'),
            ('newline_ellipsize', 'ellip_template_newlines'),
            'html',
            ('xml_entities', 'sub_template_xml_entities'),
        ] + STRIP_TEMPLATE_POSTHTML, config=config, logger=logger),

        # for cleaning up text from unknown sources (e.g. system clipboard);
        # n.b. clozes_revealed is not used here without the card context and
        # it would be a weird thing to apply to the clipboard content anyway
        from_unknown=Sanitizer([
            ('clozes_braced', 'sub_note_cloze'),
            ('clozes_rendered', 'sub_template_cloze'),
            'hint_links',
            ('hint_content', 'otf_remove_hints'),
            ('newline_ellipsize', 'ellip_note_newlines'),
            ('newline_ellipsize', 'ellip_template_newlines'),
            'html',
            'html',  # clipboards often have escaped HTML, so we run twice
            'whitespace',
            'sounds_univ',
            'filenames',
            ('within_parens', ['strip_note_parens', 'strip_template_parens']),
            ('within_brackets', ['strip_note_brackets',
                                 'strip_template_brackets']),
            ('within_braces', ['strip_note_braces', 'strip_template_braces']),
            ('char_remove', 'spec_note_strip'),
            ('char_remove', 'spec_template_strip'),
            ('counter', 'spec_note_count', 'spec_note_count_wrap'),
            ('counter', 'spec_template_count', 'spec_template_count_wrap'),
            ('char_ellipsize', 'spec_note_ellipsize'),
            ('char_ellipsize', 'spec_template_ellipsize'),
            ('custom_sub', 'sul_note'),
            ('custom_sub', 'sul_template'),
            'ellipses',
            'whitespace',
            ('xml_entities', 'sub_note_xml_entities')
        ], config=config, logger=logger),

        # for direct user input (e.g. previews, EditorGenerator insertion)
        from_user=Sanitizer(rules=[
            'ellipses', 
            'whitespace',
            ('xml_entities', 'sub_note_xml_entities')
        ], config=config, logger=logger),

        # target sounds specifically
        sounds=Bundle(
            # using Anki's method (used if we need to reproduce how Anki does
            # something, e.g. when Reviewer emulates {{FrontSide}})
            anki=anki.sound.stripSounds,

            # using AwesomeTTS's methods (which have access to precompiled re
            # objects, usable for everything else, e.g. when BrowserGenerator
            # or BrowserStripper need to remove old sounds)
            ours=Sanitizer(rules=['sounds_ours', 'filenames'], logger=logger),
            theirs=Sanitizer(rules=['sounds_theirs'], logger=logger),
            univ=Sanitizer(rules=['sounds_univ', 'filenames'], logger=logger),
        ),
    ),
    version=VERSION,
    web=WEB,
)

# End core class initialization and dependency setup, pylint:enable=C0103


# GUI interaction with Anki
# n.b. be careful wrapping methods that have return values (see anki.hooks);
#      in general, only the 'before' mode absolves us of responsibility

# These are all called manually from the __init__.py loader so that if there
# is some sort of breakage with a specific component, it could be possibly
# disabled easily by users who are not utilizing that functionality.


def browser_menus():
    """
    Gives user access to mass generator, MP3 stripper, and the hook that
    disables and enables it upon selection of items.
    """

    from PyQt5 import QtWidgets

    def on_setup_menus(browser):
        """Create an AwesomeTTS menu and add browser actions to it."""

        menu = QtWidgets.QMenu("Awesome&TTS", browser.form.menubar)
        browser.form.menubar.addMenu(menu)

        gui.Action(
            target=Bundle(
                constructor=gui.BrowserGenerator,
                args=(),
                kwargs=dict(browser=browser,
                            addon=addon,
                            alerts=aqt.utils.showWarning,
                            ask=aqt.utils.getText,
                            parent=browser),
            ),
            text="&Add Audio to Selected...",
            sequence=sequences['browser_generator'],
            parent=menu,
        )
        gui.Action(
            target=Bundle(
                constructor=gui.BrowserStripper,
                args=(),
                kwargs=dict(browser=browser,
                            addon=addon,
                            alerts=aqt.utils.showWarning,
                            parent=browser),
            ),
            text="&Remove Audio from Selected...",
            sequence=sequences['browser_stripper'],
            parent=menu,
        )

    def update_title_wrapper(browser):
        """Enable/disable AwesomeTTS menu items upon selection."""

        enabled = bool(browser.form.tableView.selectionModel().selectedRows())
        for action in browser.findChildren(gui.Action):
            action.setEnabled(enabled)

    anki.hooks.addHook(
        'browser.setupMenus',
        on_setup_menus,
    )

    aqt.browser.Browser.updateTitle = anki.hooks.wrap(
        aqt.browser.Browser.updateTitle,
        update_title_wrapper,
        'before',
    )


def cache_control():
    """Registers a hook to handle cache control on session exits."""

    def on_unload_profile():
        """
        Finds MP3s in the cache directory older than the user's
        configured cache limit and attempts to remove them.
        """

        from os import listdir, unlink

        cache = paths.CACHE

        try:
            filenames = listdir(cache)
        except:  # allow silent failure, pylint:disable=bare-except
            return
        if not filenames:
            return

        prospects = (join(cache, filename) for filename in filenames)

        if config['cache_days']:
            from os.path import getmtime

            limit = time() - 86400 * config['cache_days']
            targets = (prospect for prospect in prospects
                       if getmtime(prospect) < limit)
        else:
            targets = prospects

        for target in targets:
            try:
                unlink(target)
            except:  # skip broken files, pylint:disable=bare-except
                pass

    anki.hooks.addHook('unloadProfile', on_unload_profile)


def cards_button():
    """Provides access to the templater helper."""

    from aqt import clayout

    clayout.CardLayout.setupButtons = anki.hooks.wrap(
        clayout.CardLayout.setupButtons,
        lambda card_layout: card_layout.buttons.insertWidget(
            # Now, the card layout for regular notes has 7 buttons/stretchers
            # and the one for cloze notes has 6 (as it lacks a "Flip" button);
            # position 3 puts our button after "Add Field", but in the event
            # that the form suddenly has a different number of buttons, let's
            # just fallback to the far left position

            3 if card_layout.buttons.count() in [6, 7] else 0,
            gui.Button(
                text="Add &TTS",
                tooltip="Insert a tag for on-the-fly playback w/ AwesomeTTS",
                sequence=sequences['templater'],
                target=Bundle(
                    constructor=gui.Templater,
                    args=(),
                    kwargs=dict(card_layout=card_layout,
                                addon=addon,
                                alerts=aqt.utils.showWarning,
                                ask=aqt.utils.getText,
                                parent=card_layout),
                ),
            ),
        ),
        'after',  # must use 'after' so that 'buttons' attribute is set
    )


def config_menu():
    """
    Adds a menu item to the Tools menu in Anki's main window for
    launching the configuration dialog.
    """

    gui.Action(
        target=Bundle(
            constructor=gui.Configurator,
            args=(),
            kwargs=dict(addon=addon, sul_compiler=to.substitution_compiled,
                        alerts=aqt.utils.showWarning,
                        ask=aqt.utils.getText,
                        parent=aqt.mw),
        ),
        text="Awesome&TTS...",
        sequence=sequences['configurator'],
        parent=aqt.mw.form.menuTools,
    )

    # setup AwesomeTTS resources menu
    resources_menu = PyQt5.QtWidgets.QMenu('AwesomeTTS Resources', aqt.mw)
    
    def open_url_lambda(url):
        def open_url():
            PyQt5.QtGui.QDesktopServices.openUrl(PyQt5.QtCore.QUrl(url))
        return open_url

    links = [
        {'name': """What's New / Updates""", 'url_path': 'updates'},
        {'name': 'Getting Started with AwesomeTTS', 'url_path': 'tutorials/awesometts-getting-started'},
        {'name': 'Batch Audio Generation', 'url_path': 'tutorials/awesometts-batch-generation'},
        {'name': 'On the fly Audio', 'url_path': 'tutorials/awesometts-on-the-fly-tts'},
        {'name': 'All Tutorials', 'url_path': 'tutorials'},
        {'name': 'Listen to Voice Samples', 'url_path': 'languages'},
        {'name': 'Get Access to All Voices / All Services', 'url_path': 'awesometts-plus'},
    ]    
    for link in links:
        action = PyQt5.QtWidgets.QAction(link['name'], aqt.mw)
        url_path = link['url_path']
        url = f'https://languagetools.anki.study/{url_path}?utm_campaign=atts_resources&utm_source=awesometts&utm_medium=addon'
        action.triggered.connect(open_url_lambda(url))
        resources_menu.addAction(action)
    # and add it to the tools menu
    aqt.mw.form.menuTools.addMenu(resources_menu)


def editor_button():
    """
    Enable the generation of a single audio clip through the editor,
    which is present in the "Add" and browser windows.
    """

    def createAwesomeTTSEditorLambda():
        def launch(editor):
            editor_generator = gui.EditorGenerator(editor=editor,
                                                   addon=addon,
                                                   alerts=aqt.utils.showWarning,
                                                   ask=aqt.utils.getText,
                                                   parent=editor.parentWindow)
            editor_generator.show()
        return launch

    def addAwesomeTTSEditorButton(buttons, editor):
        cmd_string = 'awesometts_btn'
        editor._links[cmd_string] = createAwesomeTTSEditorLambda()
        new_button = editor._addButton(icon = gui.ICON_FILE,
            cmd = cmd_string,
            tip = "Record and insert an audio clip here w/ AwesomeTTS")
        return buttons + [new_button]

    anki.hooks.addHook('setupEditorButtons', addAwesomeTTSEditorButton)

    def createAwesomeTTSEditorShortcutLambda(editor):
        def launch():
            editor_generator = gui.EditorGenerator(editor=editor,
                                                   addon=addon,
                                                   alerts=aqt.utils.showWarning,
                                                   ask=aqt.utils.getText,
                                                   parent=editor.parentWindow)
            editor_generator.show()
        return launch

    def editor_init_shortcuts(shortcuts, editor: aqt.editor.Editor):
        shortcut_sequence = sequences['editor_generator'].toString()
        lambda_function = createAwesomeTTSEditorShortcutLambda(editor)
        shortcut_entry = (shortcut_sequence, lambda_function, True)
        shortcuts.append(shortcut_entry)

    aqt.gui_hooks.editor_did_init_shortcuts.append(editor_init_shortcuts)

    # TODO: Editor buttons are now in the WebView, not sure how (and if)
    # we should implement muzzling. Please see:
    # https://github.com/dae/anki/commit/a001553f66efe75e660eb0702cd29a9d62503fc4
    """
    aqt.editor.Editor.enableButtons = anki.hooks.wrap(
        aqt.editor.Editor.enableButtons,
        lambda editor, val=True: (
            editor.widget.findChild(gui.Button).setEnabled(val),

            # Temporarily disable any AwesomeTTS menu shortcuts in the Browser
            # window so that if a shortcut combination has been re-used
            # between the editor button and those, the "local" shortcut works.
            # Has no effect on "Add" window (the child list will be empty).
            [action.muzzle(val) for action
             in editor.parentWindow.findChildren(gui.Action)],
        ),
        'before',
    )
    """


def reviewer_hooks():
    """
    Enables support for AwesomeTTS to automatically play text-to-speech
    tags and to also do playback on-demand via shortcut keys and the
    context menu.
    """

    from PyQt5.QtCore import QEvent
    from PyQt5.QtWidgets import QMenu


    # context menu playback

    strip = Sanitizer([('newline_ellipsize', 'ellip_template_newlines')] +
                      STRIP_TEMPLATE_POSTHTML, config=config, logger=logger)

    def say_text_preset_handler(text, preset, parent):
        """Play the selected text using the preset."""

        router(
            svc_id=preset['service'],
            text=text,
            options=preset,
            callbacks=dict(
                okay=player.menu_click,
                fail=lambda exception, text: (),
            ),
        )

    def say_text_group_handler(text, group, parent):
        """Play the selected text using the group."""

        router.group(
            text=text,
            group=group,
            presets=config['presets'],
            callbacks=dict(
                okay=player.menu_click,
                fail=lambda exception, text: (),
            ),
        )    

    def on_context_menu(web_view, menu):
        """Populate context menu, given the context/configuration."""

        window = web_view.window()

        try:  # this works for web views embedded in editor windows
            atts_button = web_view.editor.widget.findChild(gui.Button)
        except AttributeError:
            atts_button = None

        say_text = config['presets'] and strip(web_view.selectedText())

        submenu = QMenu("Awesome&TTS", menu)
        submenu.setIcon(gui.ICON)

        needs_separator = False

        if atts_button:
            submenu.addAction(
                "Add MP3 to the Note",
                lambda: atts_button.click() if atts_button.isEnabled()
                else aqt.utils.showWarning(
                    "Select the note field to which you want to add an MP3.",
                    window,
                )
            )
            needs_separator = True

        if say_text:
            say_display = (say_text if len(say_text) < 25
                           else say_text[0:20].rstrip(' .') + "...")

            if config['presets']:
                if needs_separator:
                    submenu.addSeparator()
                else:
                    needs_separator = True

                def preset_glue(xxx_todo_changeme):
                    """Closure for callback handler to access `preset`."""
                    (name, preset) = xxx_todo_changeme
                    submenu.addAction(
                        'Say "%s" w/ %s' % (say_display, name),
                        lambda: say_text_preset_handler(say_text,
                                                           preset,
                                                           window),
                    )
                for item in sorted(config['presets'].items(),
                                   key=lambda item: item[0].lower()):
                    preset_glue(item)

            if config['groups']:
                if needs_separator:
                    submenu.addSeparator()
                else:
                    needs_separator = True

                def group_glue(xxx_todo_changeme1):
                    """Closure for callback handler to access `group`."""
                    (name, group) = xxx_todo_changeme1
                    submenu.addAction(
                        'Say "%s" w/ %s' % (say_display, name),
                        lambda: say_text_group_handler(say_text,
                                                                 group,
                                                                 window),
                    )
                for item in sorted(config['groups'].items(),
                                   key=lambda item: item[0].lower()):
                    group_glue(item)

        menu.addMenu(submenu)

    anki.hooks.addHook('AnkiWebView.contextMenuEvent', on_context_menu)
    anki.hooks.addHook('EditorWebView.contextMenuEvent', on_context_menu)
    anki.hooks.addHook('Reviewer.contextMenuEvent',
                       lambda reviewer, menu:
                       on_context_menu(reviewer.web, menu))


def temp_files():
    """Remove temporary files upon session exit."""

    def on_unload_profile():
        """
        Finds scratch directories in the temporary path, removes their
        files, then removes the directories themselves.
        """

        from os import listdir, unlink, rmdir
        from os.path import isdir

        temp = paths.TEMP

        try:
            subdirs = [join(temp, filename) for filename in listdir(temp)
                       if filename.startswith('_awesometts_scratch')]
        except:  # allow silent failure, pylint:disable=bare-except
            return
        if not subdirs:
            return

        for subdir in subdirs:
            if isdir(subdir):
                for filename in listdir(subdir):
                    try:
                        unlink(join(subdir, filename))
                    except:  # skip busy files, pylint:disable=bare-except
                        pass
                try:
                    rmdir(subdir)
                except:  # allow silent failure, pylint:disable=bare-except
                    pass

    anki.hooks.addHook('unloadProfile', on_unload_profile)


def window_shortcuts():
    """Enables shortcuts to launch windows."""

    def on_sequence_change(new_config):
        """Update sequences on configuration changes."""
        for key, sequence in sequences.items():
            new_sequence = QKeySequence(new_config['launch_' + key] or None)
            sequence.swap(new_sequence)

        try:
            aqt.mw.form.menuTools.findChild(gui.Action). \
                setShortcut(sequences['configurator'])
        except AttributeError:  # we do not have a config menu
            pass

    on_sequence_change(config)  # set config menu if created before we ran
    config.bind(['launch_' + key for key in sequences.keys()],
                on_sequence_change)


def register_tts_tag():
    register_tts_player(addon)

def display_homescreen():
    linkHandler = gui.homescreen.makeLinkHandler(addon)
    aqt.deckbrowser.DeckBrowser._linkHandler = anki.hooks.wrap(
        aqt.deckbrowser.DeckBrowser._linkHandler, linkHandler, "before"
    )    

    on_deckbrowser_will_render_content = gui.homescreen.makeDeckBrowserRenderContent(addon)
    aqt.gui_hooks.deck_browser_will_render_content.append(on_deckbrowser_will_render_content)