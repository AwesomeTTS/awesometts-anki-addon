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
import sys
from time import time

from PyQt4.QtCore import PYQT_VERSION_STR, Qt
from PyQt4.QtGui import QKeySequence

import anki
import aqt

from . import conversion as to, gui, paths, service
from .bundle import Bundle
from .config import Config
from .player import Player
from .router import Router
from .text import Sanitizer
from .updates import Updates

__all__ = ['browser_menus', 'cards_button', 'config_menu', 'editor_button',
           'reviewer_hooks', 'sound_tag_delays', 'update_checker',
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

VERSION = '1.12.0'

WEB = 'https://ankiatts.appspot.com'

AGENT = 'AwesomeTTS/%s (Anki %s; PyQt %s; %s)' % (VERSION, anki.version,
                                                  PYQT_VERSION_STR,
                                                  get_platform_info())


# Begin core class initialization and dependency setup, pylint:disable=C0103

logger = Bundle(debug=lambda *a, **k: None, error=lambda *a, **k: None,
                info=lambda *a, **k: None, warn=lambda *a, **k: None)
# for logging output, replace `logger` with a real one, e.g.:
# import logging as logger
# logger.basicConfig(stream=sys.stdout, level=logger.DEBUG)

sequences = {key: QKeySequence()
             for key in ['browser_generator', 'browser_stripper',
                         'configurator', 'editor_generator', 'templater']}

config = Config(
    db=Bundle(path=paths.CONFIG,
              table='general',
              normalize=to.normalized_ascii),
    cols=[
        ('automaticAnswers', 'integer', True, to.lax_bool, int),
        ('automatic_answers_errors', 'integer', True, to.lax_bool, int),
        ('automaticQuestions', 'integer', True, to.lax_bool, int),
        ('automatic_questions_errors', 'integer', True, to.lax_bool, int),
        ('cache_days', 'integer', 365, int, int),
        ('delay_answers_onthefly', 'integer', 0, int, int),
        ('delay_answers_stored_ours', 'integer', 0, int, int),
        ('delay_answers_stored_theirs', 'integer', 0, int, int),
        ('delay_questions_onthefly', 'integer', 0, int, int),
        ('delay_questions_stored_ours', 'integer', 0, int, int),
        ('delay_questions_stored_theirs', 'integer', 0, int, int),
        ('ellip_note_newlines', 'integer', False, to.lax_bool, int),
        ('ellip_template_newlines', 'integer', False, to.lax_bool, int),
        ('extras', 'text', {}, to.deserialized_dict, to.compact_json),
        ('filenames', 'text', 'hash', str, str),
        ('filenames_human', 'text',
         u'{{text}} ({{service}} {{voice}})', unicode, unicode),
        ('groups', 'text', {}, to.deserialized_dict, to.compact_json),
        ('lame_flags', 'text', '--quiet -q 2', str, str),
        ('last_mass_append', 'integer', True, to.lax_bool, int),
        ('last_mass_behavior', 'integer', True, to.lax_bool, int),
        ('last_mass_dest', 'text', 'Back', unicode, unicode),
        ('last_mass_source', 'text', 'Front', unicode, unicode),
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
        ('presets', 'text', {}, to.deserialized_dict, to.compact_json),
        ('spec_note_count', 'text', '', unicode, unicode),
        ('spec_note_count_wrap', 'integer', True, to.lax_bool, int),
        ('spec_note_ellipsize', 'text', '', unicode, unicode),
        ('spec_note_strip', 'text', '', unicode, unicode),
        ('spec_template_count', 'text', '', unicode, unicode),
        ('spec_template_count_wrap', 'integer', True, to.lax_bool, int),
        ('spec_template_ellipsize', 'text', '', unicode, unicode),
        ('spec_template_strip', 'text', '', unicode, unicode),
        ('strip_note_braces', 'integer', False, to.lax_bool, int),
        ('strip_note_brackets', 'integer', False, to.lax_bool, int),
        ('strip_note_parens', 'integer', False, to.lax_bool, int),
        ('strip_template_braces', 'integer', False, to.lax_bool, int),
        ('strip_template_brackets', 'integer', False, to.lax_bool, int),
        ('strip_template_parens', 'integer', False, to.lax_bool, int),
        ('sub_note_cloze', 'text', 'anki', str, str),
        ('sub_template_cloze', 'text', 'anki', str, str),
        ('sul_note', 'text', [], to.substitution_list, to.substitution_json),
        ('sul_template', 'text', [], to.substitution_list,
         to.substitution_json),
        ('templater_cloze', 'integer', True, to.lax_bool, int),
        ('templater_field', 'text', 'Front', unicode, unicode),
        ('templater_hide', 'text', 'normal', str, str),
        ('templater_target', 'text', 'front', str, str),
        ('throttle_sleep', 'integer', 30, int, int),
        ('throttle_threshold', 'integer', 10, int, int),
        ('TTS_KEY_A', 'integer', Qt.Key_F4, to.nullable_key, to.nullable_int),
        ('TTS_KEY_Q', 'integer', Qt.Key_F3, to.nullable_key, to.nullable_int),
        ('updates_enabled', 'integer', True, to.lax_bool, int),
        ('updates_ignore', 'text', '', str, str),
        ('updates_postpone', 'integer', 0, int, lambda i: int(round(i))),
    ],
    logger=logger,
    events=[
    ],
)

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
            ('abair', service.Abair),
            ('baidu', service.Baidu),
            ('collins', service.Collins),
            ('duden', service.Duden),
            ('ekho', service.Ekho),
            ('espeak', service.ESpeak),
            ('festival', service.Festival),
            ('fluencynl', service.FluencyNl),
            ('google', service.Google),
            ('howjsay', service.Howjsay),
            ('imtranslator', service.ImTranslator),
            ('ispeech', service.ISpeech),
            ('naver', service.Naver),
            ('neospeech', service.NeoSpeech),
            ('oddcast', service.Oddcast),
            ('oxford', service.Oxford),
            ('pico2wave', service.Pico2Wave),
            ('rhvoice', service.RHVoice),
            ('sapi5com', service.SAPI5COM),
            ('sapi5js', service.SAPI5JS),
            ('say', service.Say),
            ('spanishdict', service.SpanishDict),
            ('voicetext', service.VoiceText),
            ('wiktionary', service.Wiktionary),
            ('yandex', service.Yandex),
            ('youdao', service.Youdao),
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
                    ecosystem=Bundle(web=WEB, agent=AGENT)),
    ),
    cache_dir=paths.CACHE,
    temp_dir=join(paths.TEMP, '_awesometts_scratch_' + str(int(time()))),
    logger=logger,
    config=config,
)

updates = Updates(
    agent=AGENT,
    endpoint='%s/api/update/%s-%s-%s' % (WEB, anki.version, sys.platform,
                                         VERSION),
    logger=logger,
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
        fail=lambda message: aqt.utils.showCritical(message, aqt.mw),
    ),
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
        ], config=config, logger=logger),

        # for cleaning up already-processed HTML templates (e.g. on-the-fly,
        # where cloze is marked with <span class=cloze></span> tags)
        from_template_front=Sanitizer([
            ('clozes_rendered', 'sub_template_cloze'),
            'hint_links',
            ('hint_content', 'otf_remove_hints'),
            ('newline_ellipsize', 'ellip_template_newlines'),
            'html',
        ] + STRIP_TEMPLATE_POSTHTML, config=config, logger=logger),

        # like the previous, but for the back sides of cards
        from_template_back=Sanitizer([
            ('clozes_revealed', 'otf_only_revealed_cloze'),
            'hint_links',
            ('hint_content', 'otf_remove_hints'),
            ('newline_ellipsize', 'ellip_template_newlines'),
            'html',
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
        ], config=config, logger=logger),

        # for direct user input (e.g. previews, EditorGenerator insertion)
        from_user=Sanitizer(rules=['ellipses', 'whitespace'], logger=logger),

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
    updates=updates,
    version=VERSION,
    web=WEB,
)

# End core class initialization and dependency setup, pylint:enable=C0103


# GUI interaction with Anki
# n.b. be careful wrapping methods that have return values (see anki.hooks);
#      in general, only the 'before' mode absolves us of responsibility

# These are all called manually from the AwesomeTTS.py loader so that if there
# is some sort of breakage with a specific component, it could be possibly
# disabled easily by users who are not utilizing that functionality.


def browser_menus():
    """
    Gives user access to mass generator, MP3 stripper, and the hook that
    disables and enables it upon selection of items.
    """

    from PyQt4 import QtGui

    def on_setup_menus(browser):
        """Create an AwesomeTTS menu and add browser actions to it."""

        menu = QtGui.QMenu("Awesome&TTS", browser.form.menubar)
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


def editor_button():
    """
    Enable the generation of a single audio clip through the editor,
    which is present in the "Add" and browser windows.
    """

    anki.hooks.addHook(
        'setupEditorButtons',
        lambda editor: editor.iconsBox.addWidget(
            gui.Button(
                tooltip="Record and insert an audio clip here w/ AwesomeTTS",
                sequence=sequences['editor_generator'],
                target=Bundle(
                    constructor=gui.EditorGenerator,
                    args=(),
                    kwargs=dict(editor=editor,
                                addon=addon,
                                alerts=aqt.utils.showWarning,
                                ask=aqt.utils.getText,
                                parent=editor.parentWindow),
                ),
                style=editor.plastiqueStyle,
            ),
        ),
    )

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


def reviewer_hooks():
    """
    Enables support for AwesomeTTS to automatically play text-to-speech
    tags and to also do playback on-demand via shortcut keys and the
    context menu.
    """

    from PyQt4.QtCore import QEvent
    from PyQt4.QtGui import QMenu

    reviewer = gui.Reviewer(addon=addon,
                            alerts=aqt.utils.showWarning,
                            mw=aqt.mw)

    # automatic playback

    anki.hooks.addHook(
        'showQuestion',
        lambda: reviewer.card_handler('question', aqt.mw.reviewer.card),
    )

    anki.hooks.addHook(
        'showAnswer',
        lambda: reviewer.card_handler('answer', aqt.mw.reviewer.card),
    )

    # shortcut-triggered playback

    reviewer_filter = gui.Filter(
        relay=lambda event: reviewer.key_handler(
            key_event=event,
            state=aqt.mw.reviewer.state,
            card=aqt.mw.reviewer.card,
            replay_audio=aqt.mw.reviewer.replayAudio,
        ),

        when=lambda event: (aqt.mw.state == 'review' and
                            event.type() == QEvent.KeyPress and
                            not event.isAutoRepeat() and
                            not event.spontaneous()),

        parent=aqt.mw,  # prevents filter from being garbage collected
    )

    aqt.mw.installEventFilter(reviewer_filter)

    # context menu playback

    strip = Sanitizer([('newline_ellipsize', 'ellip_template_newlines')] +
                      STRIP_TEMPLATE_POSTHTML, config=config, logger=logger)

    def on_context_menu(web_view, menu):
        """Populate context menu, given the context/configuration."""

        window = web_view.window()

        try:  # this works for web views embedded in editor windows
            atts_button = web_view.editor.widget.findChild(gui.Button)
        except AttributeError:
            atts_button = None

        say_text = config['presets'] and strip(web_view.selectedText())

        tts_card = tts_side = None
        tts_shortcuts = False
        try:  # this works for web views in the reviewer and template dialog
            if window is aqt.mw and aqt.mw.state == 'review':
                tts_card = aqt.mw.reviewer.card
                tts_side = aqt.mw.reviewer.state
                tts_shortcuts = True
            elif web_view.objectName() == 'mainText':  # card template dialog
                parent_name = web_view.parentWidget().objectName()
                tts_card = window.card
                tts_side = ('question' if parent_name == 'groupBox'
                            else 'answer' if parent_name == 'groupBox_2'
                            else None)
        except Exception:  # just in case, pylint:disable=broad-except
            pass

        tts_question = tts_card and tts_side and \
            reviewer.has_tts('question', tts_card)
        tts_answer = tts_card and tts_side == 'answer' and \
            reviewer.has_tts('answer', tts_card)

        if not (atts_button or say_text or tts_question or tts_answer):
            return

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

                def preset_glue((name, preset)):
                    """Closure for callback handler to access `preset`."""
                    submenu.addAction(
                        'Say "%s" w/ %s' % (say_display, name),
                        lambda: reviewer.selection_handler(say_text,
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

                def group_glue((name, group)):
                    """Closure for callback handler to access `group`."""
                    submenu.addAction(
                        'Say "%s" w/ %s' % (say_display, name),
                        lambda: reviewer.selection_handler_group(say_text,
                                                                 group,
                                                                 window),
                    )
                for item in sorted(config['groups'].items(),
                                   key=lambda item: item[0].lower()):
                    group_glue(item)

        if tts_question or tts_answer:
            if needs_separator:
                submenu.addSeparator()

            if tts_question:
                submenu.addAction(
                    "Play On-the-Fly TTS from Question Side",
                    lambda: reviewer.nonselection_handler('question', tts_card,
                                                          window),
                    tts_shortcuts and config['tts_key_q'] or 0,
                )

            if tts_answer:
                submenu.addAction(
                    "Play On-the-Fly TTS from Answer Side",
                    lambda: reviewer.nonselection_handler('answer', tts_card,
                                                          window),
                    tts_shortcuts and config['tts_key_a'] or 0,
                )

        menu.addMenu(submenu)

    anki.hooks.addHook('AnkiWebView.contextMenuEvent', on_context_menu)
    anki.hooks.addHook('EditorWebView.contextMenuEvent', on_context_menu)
    anki.hooks.addHook('Reviewer.contextMenuEvent',
                       lambda reviewer, menu:
                       on_context_menu(reviewer.web, menu))


def sound_tag_delays():
    """
    Enables support for the following sound delay configuration options:

    - delay_questions_stored_ours (AwesomeTTS MP3s on questions)
    - delay_questions_stored_theirs (non-AwesomeTTS MP3s on questions)
    - delay_answers_stored_ours (AwesomeTTS MP3s on answers)
    - delay_answers_stored_theirs (non-AwesomeTTS MP3s on answers)
    """

    anki.sound.play = player.native_wrapper


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


def update_checker():
    """
    Automatic check for new version, if neither postponed nor ignored.

    With the profilesLoaded hook, we do not run the check until the user
    is actually in a profile, which guarantees the main window has been
    loaded. Without it, update components (e.g. aqt.downloader.download,
    aqt.addons.GetAddons) that expect it might fail unexpectedly.
    """

    if not config['updates_enabled'] or \
       config['updates_postpone'] and config['updates_postpone'] > time():
        return

    def on_need(version, info):
        """If not an ignored version, pop open the updater dialog."""

        if config['updates_ignore'] == version:
            return

        gui.Updater(
            version=version,
            info=info,
            addon=addon,
            parent=aqt.mw,
        ).show()

    anki.hooks.addHook(
        'profileLoaded',
        lambda: updates.used() or updates.check(callbacks=dict(need=on_need)),
    )


def window_shortcuts():
    """Enables shortcuts to launch windows."""

    def on_sequence_change(new_config):
        """Update sequences on configuration changes."""

        for key, sequence in sequences.items():
            try:
                sequence.swap(new_config['launch_' + key] or 0)
            except AttributeError:  # support for PyQt 4.7 and below
                sequences[key] = QKeySequence(new_config['launch_' + key] or 0)

        try:
            aqt.mw.form.menuTools.findChild(gui.Action). \
                setShortcut(sequences['configurator'])
        except AttributeError:  # we do not have a config menu
            pass

    on_sequence_change(config)  # set config menu if created before we ran
    config.bind(['launch_' + key for key in sequences.keys()],
                on_sequence_change)
