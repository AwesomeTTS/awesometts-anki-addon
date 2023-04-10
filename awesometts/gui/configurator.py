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

"""Configuration dialog"""

from locale import format as locale
import os
import os.path
from sys import platform
import pprint
import aqt.utils

import aqt.qt

from ..paths import ICONS
from .base import Dialog
from .common import Checkbox, Label, Note, Slate
from .listviews import SubListView
from .presets import Presets
from .groups import Groups

__all__ = ['Configurator']

# all methods might need 'self' in the future, pylint:disable=R0201


class Configurator(Dialog):
    """Provides a dialog for configuring the add-on."""

    _PROPERTY_KEYS = [
        'cache_days', 'ellip_note_newlines',
        'ellip_template_newlines', 'filenames', 'filenames_human', 'homescreen_show',
        'lame_flags', 'shortcut_launch_browser_generator', 'shortcut_launch_browser_stripper',
        'shortcut_launch_configurator', 'shortcut_launch_editor_generator', 'shorcut_launch_templater',
        'otf_only_revealed_cloze', 'otf_remove_hints', 'spec_note_strip',
        'spec_note_ellipsize', 'spec_template_ellipsize', 'spec_note_count',
        'spec_note_count_wrap', 'spec_template_count',
        'spec_template_count_wrap', 'spec_template_strip', 'strip_note_braces',
        'strip_note_brackets', 'strip_note_parens', 'strip_template_braces',
        'strip_template_brackets', 'strip_template_parens', 'sub_note_cloze',
        'sub_template_cloze', 'sul_note', 'sul_template', 'throttle_sleep',
        'throttle_threshold', 'plus_api_key', 'service_forvo_preferred_users',
        'service_azure_sleep_time',
        'strip_ruby_tags',
        'sub_note_xml_entities', 'sub_template_xml_entities'
    ]

    _PROPERTY_WIDGETS = (Checkbox, aqt.qt.QComboBox, aqt.qt.QLineEdit,
                         aqt.qt.QPushButton, aqt.qt.QSpinBox, aqt.qt.QListView,
                         aqt.qt.QKeySequenceEdit)

    __slots__ = ['_alerts', '_ask', '_preset_editor', '_group_editor',
                 '_sul_compiler']

    def __init__(self, logger, alerts, ask, sul_compiler, *args, **kwargs):
        self._logger = logger
        self._alerts = alerts
        self._ask = ask
        self._preset_editor = None
        self._group_editor = None
        self._sul_compiler = sul_compiler

        super(Configurator, self).__init__(title="Configuration",
                                           *args, **kwargs)

    # UI Construction ########################################################

    def _ui(self):
        """Returns vertical layout w/ banner, our tabs, cancel/OK."""

        layout = super(Configurator, self)._ui()
        layout.addWidget(self._ui_tabs())
        layout.addWidget(self._ui_buttons())
        return layout

    def _ui_tabs(self):
        """Returns tab widget w/ Playback, Text, MP3s, Advanced."""

        use_icons = not platform.startswith('darwin')
        tabs = aqt.qt.QTabWidget()

        for content, icon, label in [
                (self._ui_tabs_text, 'editclear', "Text"),
                (self._ui_tabs_mp3gen, 'document-new', "MP3s"),
                (self._ui_tabs_windows, 'kpersonalizer', "Windows"),
                (self._ui_tabs_services, 'rating', "Services"),
                (self._ui_tabs_advanced, 'configure', "Advanced"),
        ]:
            if use_icons:
                tabs.addTab(content(), aqt.qt.QIcon(f'{ICONS}/{icon}.png'),
                            label)
            else:  # active tabs do not display correctly on Mac OS X w/ icons
                tabs.addTab(content(), label)

        tabs.currentChanged.connect(lambda: (tabs.adjustSize(),
                                             self.adjustSize()))
        return tabs


    def _ui_tabs_text(self):
        """Returns the "Text" tab."""

        layout = aqt.qt.QVBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.addWidget(self._ui_tabs_text_mode(
            '_template_',
            "Handling Template Text (e.g. On-the-Fly, Context Menus)",
            "For a front-side rendered cloze,",
            [('anki', "read however Anki displayed it"),
             ('wrap', "read w/ hint wrapped in ellipses"),
             ('ellipsize', "read as an ellipsis, ignoring hint"),
             ('remove', "remove entirely")],
            template_options=True,
        ), 50)
        layout.addWidget(self._ui_tabs_text_mode(
            '_note_',
            "Handling Text from a Note Field (e.g. Browser Generator)",
            "For a braced cloze marker,",
            [('anki', "read as Anki would display on a card front"),
             ('wrap', "replace w/ hint wrapped in ellipses"),
             ('deleted', "replace w/ deleted text"),
             ('ellipsize', "replace w/ ellipsis, ignoring both"),
             ('remove', "remove entirely")],
        ), 50)

        tab = aqt.qt.QWidget()
        tab.setLayout(layout)
        return tab

    def _ui_tabs_text_mode(self, infix, label, *args, **kwargs):
        """Returns group box for the given text manipulation context."""

        subtabs = aqt.qt.QTabWidget()
        subtabs.setTabPosition(aqt.qt.QTabWidget.TabPosition.West)

        for sublabel, sublayout in [
                ("Simple", self._ui_tabs_text_mode_simple(infix, *args,
                                                          **kwargs)),
                ("Advanced", self._ui_tabs_text_mode_adv(infix)),
        ]:
            subwidget = aqt.qt.QWidget()
            subwidget.setLayout(sublayout)
            subtabs.addTab(subwidget, sublabel)

        layout = aqt.qt.QVBoxLayout()
        # TODO
        # layout.setCanvasMargin(0)
        layout.addWidget(subtabs)

        group = aqt.qt.QGroupBox(label)
        group.setFlat(True)
        group.setLayout(layout)

        layout_margins = layout.contentsMargins()
        layout_margins.setLeft(0)
        layout.setContentsMargins(layout_margins)
        groupbox_margins = group.contentsMargins()
        groupbox_margins.setLeft(0)
        group.setContentsMargins(groupbox_margins)

        return group

    def _ui_tabs_text_mode_simple(self, infix, cloze_description,
                                  cloze_options, template_options=False):
        """
        Returns a layout with the "simple" configuration options
        available for manipulating text from the given context.
        """

        select = aqt.qt.QComboBox()
        for option_value, option_text in cloze_options:
            select.addItem(option_text, option_value)
        select.setObjectName(infix.join(['sub', 'cloze']))

        hor = aqt.qt.QHBoxLayout()
        hor.addWidget(Label(cloze_description))
        hor.addWidget(select)
        hor.addStretch()

        layout = aqt.qt.QVBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.addLayout(hor)

        if template_options:
            hor = aqt.qt.QHBoxLayout()
            hor.addWidget(Checkbox("For cloze answers, read revealed text "
                                   "only", 'otf_only_revealed_cloze'))
            hor.addWidget(Checkbox("Ignore {{hint}} fields",
                                   'otf_remove_hints'))
            layout.addLayout(hor)

        layout.addWidget(Checkbox(
            "Convert any newline(s) in input into an ellipsis",
            infix.join(['ellip', 'newlines'])
        ))

        if not template_options:
            layout.addWidget(Checkbox(
                "Process Ruby/Furigana tags", 'strip_ruby_tags'
            ))
            layout.addWidget(Checkbox(
                """Escape HTML special characters like <,>,&&. 
    This may be necessary for technical content, 
    such as medical flashcards.""", 
                'sub_note_xml_entities'
            ))            
        else:
            layout.addWidget(Checkbox(
                """Escape HTML special characters like <,>,&&. 
    This may be necessary for technical content, 
    such as medical flashcards.""", 
                'sub_template_xml_entities'
            ))                        



        hor = aqt.qt.QHBoxLayout()
        hor.addWidget(Label("Strip off text within:"))
        for option_subkey, option_label in [('parens', "parentheses"),
                                            ('brackets', "brackets"),
                                            ('braces', "braces")]:
            hor.addWidget(Checkbox(option_label,
                                   infix.join(['strip', option_subkey])))
        hor.addStretch()

        layout.addLayout(hor)
        layout.addLayout(self._ui_tabs_text_mode_simple_spec(
            infix, 'strip', ("Remove all", "characters from the input")))
        layout.addLayout(self._ui_tabs_text_mode_simple_spec(
            infix, 'count', ("Count adjacent", "characters"), True))
        layout.addLayout(self._ui_tabs_text_mode_simple_spec(
            infix, 'ellipsize', ("Replace", "characters with an ellipsis")))
        layout.addStretch()
        return layout

    def _ui_tabs_text_mode_simple_spec(self, infix, suffix, labels,
                                       wrap=False):
        """Returns a layout for specific character handling."""

        line_edit = aqt.qt.QLineEdit()
        line_edit.setObjectName(infix.join(['spec', suffix]))
        line_edit.setValidator(self._ui_tabs_text_mode_simple_spec.ucsv)
        line_edit.setFixedWidth(50)

        hor = aqt.qt.QHBoxLayout()
        hor.addWidget(Label(labels[0]))
        hor.addWidget(line_edit)
        hor.addWidget(Label(labels[1]))
        if wrap:
            hor.addWidget(Checkbox("wrap in ellipses",
                                   ''.join(['spec', infix, suffix, '_wrap'])))
        hor.addStretch()
        return hor

    class _UniqueCharacterStringValidator(aqt.qt.QValidator):
        """QValidator returning unique, sorted characters."""

        def fixup(self, original):
            """Returns unique characters from original, sorted."""

            return ''.join(sorted({c for c in original if not c.isspace()}))

        def validate(self, original, offset):  # pylint:disable=W0613
            """Fixes original text and resets cursor to end of line."""

            filtered = self.fixup(original)
            return aqt.qt.QValidator.Acceptable, filtered, len(filtered)

    _ui_tabs_text_mode_simple_spec.ucsv = _UniqueCharacterStringValidator()

    def _ui_tabs_text_mode_adv(self, infix):
        """
        Returns a layout with the "advanced" pattern replacement
        panel for manipulating text from the given context.
        """

        return Slate("Rule", SubListView, [self._sul_compiler],
                     'sul' + infix.rstrip('_'))

    def _ui_tabs_mp3gen(self):
        """Returns the "MP3s" tab."""

        vert = aqt.qt.QVBoxLayout()
        vert.addWidget(self._ui_tabs_mp3gen_filenames())
        vert.addWidget(self._ui_tabs_mp3gen_lame())
        vert.addWidget(self._ui_tabs_mp3gen_throttle())
        vert.addStretch()

        tab = aqt.qt.QWidget()
        tab.setLayout(vert)
        return tab

    def _ui_tabs_mp3gen_filenames(self):
        """Returns the "Filenames of MP3s" group."""

        dropdown = aqt.qt.QComboBox()
        dropdown.setObjectName('filenames')
        dropdown.addItem("hashed (safe and portable)", 'hash')
        dropdown.addItem("human-readable (may not work everywhere)", 'human')

        dropdown_line = aqt.qt.QHBoxLayout()
        dropdown_line.addWidget(Label("Filenames should be "))
        dropdown_line.addWidget(dropdown)
        dropdown_line.addStretch()

        human = aqt.qt.QLineEdit()
        human.setObjectName('filenames_human')
        human.setPlaceholderText("e.g. {{service}} {{voice}} - {{text}}")
        human.setEnabled(False)

        human_line = aqt.qt.QHBoxLayout()
        human_line.addWidget(Label("Format human-readable filenames as "))
        human_line.addWidget(human)
        human_line.addWidget(Label(".mp3"))

        dropdown.currentIndexChanged. \
            connect(lambda index: human.setEnabled(index > 0))

        vertical = aqt.qt.QVBoxLayout()
        vertical.addLayout(dropdown_line)
        vertical.addLayout(human_line)
        vertical.addWidget(Note("Changes are not retroactive to old files."))

        group = aqt.qt.QGroupBox("Filenames of MP3s Stored in Your Collection")
        group.setLayout(vertical)

        return group

    def _ui_tabs_mp3gen_lame(self):
        """Returns the "LAME Transcoder" input group."""

        flags = aqt.qt.QLineEdit()
        flags.setObjectName('lame_flags')
        flags.setPlaceholderText("e.g. '-q 5' for medium quality")

        rtr = self._addon.router
        vert = aqt.qt.QVBoxLayout()
        vert.addWidget(Note("Specify flags passed to lame when making MP3s."))
        vert.addWidget(flags)
        vert.addWidget(Note("Affects %s. Changes are not retroactive to old "
                            "files." %
                            ', '.join(rtr.by_trait(rtr.Trait.TRANSCODING))))

        group = aqt.qt.QGroupBox("LAME Transcoder")
        group.setLayout(vert)
        return group

    def _ui_tabs_mp3gen_throttle(self):
        """Returns the "Download Throttling" input group."""

        threshold = aqt.qt.QSpinBox()
        threshold.setObjectName('throttle_threshold')
        threshold.setRange(5, 1000)
        threshold.setSingleStep(5)
        threshold.setSuffix(" operations")

        sleep = aqt.qt.QSpinBox()
        sleep.setObjectName('throttle_sleep')
        sleep.setRange(15, 10800)
        sleep.setSingleStep(15)
        sleep.setSuffix(" seconds")

        hor = aqt.qt.QHBoxLayout()
        hor.addWidget(Label("After "))
        hor.addWidget(threshold)
        hor.addWidget(Label(" sleep for "))
        hor.addWidget(sleep)
        hor.addStretch()

        rtr = self._addon.router
        vert = aqt.qt.QVBoxLayout()
        vert.addWidget(Note("Tweak how often AwesomeTTS takes a break when "
                            "mass downloading files from online services."))
        vert.addLayout(hor)
        vert.addWidget(Note("Affects %s." %
                            ', '.join(rtr.by_trait(rtr.Trait.INTERNET))))

        group = aqt.qt.QGroupBox("Download Throttling during Batch Processing")
        group.setLayout(vert)
        return group

    def _ui_tabs_windows(self):
        """Returns the "Window" tab."""

        grid = aqt.qt.QGridLayout()
        for i, (desc, sub) in enumerate([
                ("open configuration in main window", 'configurator'),
                ("insert <tts> tag in template editor", 'templater'),
                ("mass generate MP3s in card browser", 'browser_generator'),
                ("mass remove audio in card browser", 'browser_stripper'),
                ("generate single MP3 in note editor*", 'editor_generator'),
        ]):
            object_name = 'shortcut_launch_' + sub
            grid.addWidget(Label("To " + desc + ", use keyboard shortcut: "), i, 0)
            grid.addWidget(self._get_keyboard_shortcut_textedit(object_name), i, 1)
            grid.addWidget(self._get_keyboard_shortcut_clear_button(object_name), i, 2)
        grid.setColumnStretch(1, 1)

        group = aqt.qt.QGroupBox("Window Shortcuts")
        group.setLayout(grid)

        vert = aqt.qt.QVBoxLayout()
        vert.addWidget(group)
        vert.addWidget(Note(
            "* By default, AwesomeTTS binds %(native)s for most actions. If "
            "you use math equations and LaTeX with Anki using the %(native)s "
            "E/M/T keystrokes, you may want to reassign or unbind the "
            "shortcut for generating in the note editor." %
            dict(native='Ctrl + T')
        ))
        vert.addWidget(Note("Please restart Anki after changing keyboard shortcuts."))
        vert.addWidget(Note("Some keys cannot be used as shortcuts and some "
                            "keystrokes might not work in some windows, "
                            "depending on your operating system and other "
                            "add-ons you are running. You may have to "
                            "experiment to find what works best."))
        vert.addStretch()

        tab = aqt.qt.QWidget()
        tab.setLayout(vert)
        return tab

    def _ui_tabs_services(self):
        """Returns the "Services" tab."""

        layout = aqt.qt.QVBoxLayout()
        layout.addWidget(self._ui_tabs_services_forvo())
        layout.addWidget(self._ui_tabs_services_azure())
        layout.addStretch()

        tab = aqt.qt.QWidget()
        tab.setLayout(layout)
        return tab

    def _ui_tabs_services_forvo(self):

        ver = aqt.qt.QVBoxLayout()
        url_label = aqt.qt.QLabel("Preferred Users (Enter a comma-separated list of preferred Forvo users)")
        ver.addWidget(url_label)

        forvo_preferred_users = aqt.qt.QLineEdit()
        forvo_preferred_users.setObjectName('service_forvo_preferred_users')
        forvo_preferred_users.setPlaceholderText("Enter preferred Forvo users, comma-separated")
        ver.addWidget(forvo_preferred_users)

        group = aqt.qt.QGroupBox("Forvo")
        group.setLayout(ver)
        return group

    def _ui_tabs_services_azure(self):

        ver = aqt.qt.QVBoxLayout()
        url_label = aqt.qt.QLabel("Sleep between each request (for free API keys)")
        ver.addWidget(url_label)
        
        
        azure_sleep_time = aqt.qt.QSpinBox()
        azure_sleep_time.setObjectName('service_azure_sleep_time')
        azure_sleep_time.setRange(0, 10)
        azure_sleep_time.setSuffix(" seconds")

        ver.addWidget(azure_sleep_time)

        group = aqt.qt.QGroupBox("Azure")
        group.setLayout(ver)
        return group

    def _ui_tabs_advanced(self):
        """Returns the "Advanced" tab."""

        layout = aqt.qt.QVBoxLayout()
        layout.addWidget(self._ui_tabs_advanced_presets())
        layout.addWidget(self._ui_tabs_advanced_cache())
        layout.addWidget(self._ui_tabs_advanced_other())
        layout.addWidget(self._ui_tabs_advanced_plus())
        layout.addStretch()

        tab = aqt.qt.QWidget()
        tab.setLayout(layout)
        return tab

    def _ui_tabs_advanced_presets(self):
        """Returns the "Presets" input group."""

        presets_button = aqt.qt.QPushButton("Manage Presets...")
        presets_button.clicked.connect(self._on_presets)

        groups_button = aqt.qt.QPushButton("Manage Groups...")
        groups_button.clicked.connect(self._on_groups)

        hor = aqt.qt.QHBoxLayout()
        hor.addWidget(presets_button)
        hor.addWidget(groups_button)
        hor.addStretch()

        vert = aqt.qt.QVBoxLayout()
        vert.addWidget(Note("Setup services for easy access, menu playback, "
                            "randomization, or fallbacks."))
        vert.addLayout(hor)

        group = aqt.qt.QGroupBox("Service Presets and Groups")
        group.setLayout(vert)
        return group

    def _ui_tabs_advanced_cache(self):
        """Returns the "Caching" input group."""

        days = aqt.qt.QSpinBox()
        days.setObjectName('cache_days')
        days.setRange(0, 9999)
        days.setSuffix(" days")

        hor = aqt.qt.QHBoxLayout()
        hor.addWidget(Label("Delete files older than"))
        hor.addWidget(days)
        hor.addWidget(Label("at exit (zero clears everything)"))
        hor.addStretch()

        layout = aqt.qt.QVBoxLayout()
        layout.addWidget(Note("AwesomeTTS caches generated audio files and "
                              "remembers failures during each session to "
                              "speed up repeated playback."))
        layout.addLayout(hor)

        abutton = aqt.qt.QPushButton("Delete Files")
        abutton.setObjectName('on_cache')
        abutton.clicked.connect(lambda: self._on_cache_clear(abutton))

        fbutton = aqt.qt.QPushButton("Forget Failures")
        fbutton.setObjectName('on_forget')
        fbutton.clicked.connect(lambda: self._on_forget_failures(fbutton))

        hor = aqt.qt.QHBoxLayout()
        hor.addWidget(abutton)
        hor.addWidget(fbutton)
        layout.addLayout(hor)

        group = aqt.qt.QGroupBox("Caching")
        group.setLayout(layout)
        return group

    def _ui_tabs_advanced_other(self):

        ver = aqt.qt.QVBoxLayout()
        ver.addWidget(Checkbox("Show AwesomeTTS widget on Deck Browser", 'homescreen_show'))

        group = aqt.qt.QGroupBox("Other")
        group.setLayout(ver)
        return group

    def _ui_tabs_advanced_plus(self):

        ver = aqt.qt.QVBoxLayout()
        urlLink="<a href=\"https://languagetools.anki.study/awesometts-plus?utm_campaign=atts_settings&utm_source=awesometts&utm_medium=addon\">1100+ High Quality TTS voices - free trial</a>" 
        url_label = aqt.qt.QLabel(urlLink)
        url_label.setOpenExternalLinks(True)
        ver.addWidget(url_label)

        plus_api_key = aqt.qt.QLineEdit()
        plus_api_key.setObjectName('plus_api_key')
        plus_api_key.setPlaceholderText("enter your API Key")

        verify_button = aqt.qt.QPushButton()
        verify_button.setObjectName('verify_plus_api_key')
        verify_button.setText('Verify')
        verify_button.clicked.connect(lambda: self._on_verify_plus_api_key(verify_button, plus_api_key))

        account_info_button = aqt.qt.QPushButton()
        account_info_button.setObjectName('plus_account_info')
        account_info_button.setText('Account Info / Plan')
        account_info_button.clicked.connect(lambda: self._on_plus_account_info(plus_api_key, self))
        
        hor = aqt.qt.QHBoxLayout()
        hor.addWidget(plus_api_key)
        hor.addWidget(verify_button)
        hor.addWidget(account_info_button)
        ver.addLayout(hor)

        help_label = Label("Please restart Anki after entering API key. If you'd like to use free services, or "+
        "use your own service API keys, remove the above API key and restart Anki.")
        help_label.setWordWrap(True)
        ver.addWidget(help_label)

        group = aqt.qt.QGroupBox("AwesomeTTS Plus")
        group.setLayout(ver)
        return group        

    # Factories ##############################################################

    def _get_keyboard_shortcut_textedit(self, object_name):
        shortcut = aqt.qt.QKeySequenceEdit()
        shortcut.setObjectName(object_name)
        return shortcut

    def _get_keyboard_shortcut_clear_button(self, sequence_edit_object_name):
        def clear_fn():
            sequence_edit = self.findChild(aqt.qt.QKeySequenceEdit, sequence_edit_object_name)
            sequence_edit.clear()
        button = aqt.qt.QPushButton('Clear')
        button.pressed.connect(clear_fn)
        return button
                

    # Events #################################################################

    def show(self, *args, **kwargs):
        """Restores state on inputs; rough opposite of the accept()."""

        for widget, value in [
                (widget, self._addon.config[widget.objectName()])
                for widget in self.findChildren(self._PROPERTY_WIDGETS)
                if widget.objectName() in self._PROPERTY_KEYS
        ]:
            if isinstance(widget, Checkbox):
                widget.setChecked(value)
                widget.stateChanged.emit(value)
            elif isinstance(widget, aqt.qt.QKeySequenceEdit):
                self._logger.debug(f'found keyboard shortcut: {value}')
                widget.setKeySequence(aqt.qt.QKeySequence(value))
            elif isinstance(widget, aqt.qt.QLineEdit):
                widget.setText(value)
            elif isinstance(widget, aqt.qt.QComboBox):
                widget.setCurrentIndex(max(widget.findData(value), 0))
            elif isinstance(widget, aqt.qt.QSpinBox):
                widget.setValue(value)
            elif isinstance(widget, aqt.qt.QListView):
                widget.setModel(value)
            else:
                raise Exception(f'*** unsupported object type: {type(widget)}')

        widget = self.findChild(aqt.qt.QPushButton, 'on_cache')
        widget.atts_list = (
            [filename for filename in os.listdir(self._addon.paths.cache)]
            if os.path.isdir(self._addon.paths.cache) else []
        )
        if widget.atts_list:
            widget.setEnabled(True)
            widget.setText("Delete Files (%s)" %
                           locale("%d", len(widget.atts_list), grouping=True))
        else:
            widget.setEnabled(False)
            widget.setText("Delete Files")

        widget = self.findChild(aqt.qt.QPushButton, 'on_forget')
        fail_count = self._addon.router.get_failure_count()
        if fail_count:
            widget.setEnabled(True)
            widget.setText("Forget Failures (%s)" %
                           locale("%d", fail_count, grouping=True))
        else:
            widget.setEnabled(False)
            widget.setText("Forget Failures")

        super(Configurator, self).show(*args, **kwargs)

    def accept(self):
        """Saves state on inputs; rough opposite of show()."""

        for list_view in self.findChildren(aqt.qt.QListView):
            for editor in list_view.findChildren(aqt.qt.QWidget, 'editor'):
                list_view.commitData(editor)  # if an editor is open, save it

        config_update_dict = {
            widget.objectName(): (
                widget.isChecked() if isinstance(widget, Checkbox)
                else widget.atts_value if isinstance(widget, aqt.qt.QPushButton)
                else widget.value() if isinstance(widget, aqt.qt.QSpinBox)
                # for keyboard shortcuts, get the keysequence, and convert to string
                else widget.keySequence().toString() if isinstance(widget, aqt.qt.QKeySequenceEdit)
                else widget.itemData(widget.currentIndex()) if isinstance(
                    widget, aqt.qt.QComboBox)
                else [
                    i for i in widget.model().raw_data
                    if i['compiled'] and 'bad_replace' not in i
                ] if isinstance(widget, aqt.qt.QListView)
                else widget.text()
            )
            for widget in self.findChildren(self._PROPERTY_WIDGETS)
            if widget.objectName() in self._PROPERTY_KEYS
        }

        # don't overwrite api_key
        if config_update_dict['plus_api_key'] == '' and self._addon.languagetools.trial_instant_signed_up:
            # we just signed up for the instant trial, don't set the api key to empty string now
            del config_update_dict['plus_api_key']

        self._logger.debug(f'updating config with: {pprint.pformat(config_update_dict, indent=4)}')

        self._addon.config.update(config_update_dict)

        super(Configurator, self).accept()

    def _on_presets(self):
        """Opens the presets editor."""

        if not self._preset_editor:
            self._preset_editor = Presets(addon=self._addon,
                                          alerts=self._alerts,
                                          ask=self._ask,
                                          parent=self)
        self._preset_editor.show()

    def _on_groups(self):
        """
        Check to make sure the user as at least two presets, and if so,
        launch the Groups management window.
        """

        if len(self._addon.config['presets']) < 2:
            self._alerts("You must have at least two presets before you can "
                         "create a group.", parent=self)
            return

        if not self._group_editor:
            self._group_editor = Groups(ask=self._ask, addon=self._addon,
                                        parent=self)

        self._group_editor.show()

    def _on_cache_clear(self, button):
        """Attempts clear known files from cache."""

        button.setEnabled(False)
        count_error = count_success = 0

        for filename in button.atts_list:
            try:
                os.unlink(os.path.join(self._addon.paths.cache, filename))
                count_success += 1
            except:  # capture all exceptions, pylint:disable=W0702
                count_error += 1

        if count_error:
            if count_success:
                button.setText("partially emptied (%s left)" %
                               locale("%d", count_error, grouping=True))
            else:
                button.setText("unable to empty")
        else:
            button.setText("emptied cache")

    def _on_forget_failures(self, button):
        """Tells the router to forget all cached failures."""

        button.setEnabled(False)
        self._addon.router.forget_failures()
        button.setText("forgot failures")

    def _on_verify_plus_api_key(self, button, lineedit):
        """Verify API key"""

        button.setEnabled(False)
        button.setText('Verifying..')
        api_key = lineedit.text()
        result = self._addon.languagetools.verify_api_key(api_key)
        if result['key_valid'] == True:
            button.setText('Key Valid')
            # store api key in configuration
            self._addon.config['plus_api_key'] = api_key
            self._addon.languagetools.set_api_key(api_key)
        else:
            button.setEnabled(True)
            button.setText('Verify')
            aqt.utils.showCritical(result['msg'])

    def _on_plus_account_info(self, lineedit, parent_dialog):
        """Load account info"""

        api_key = lineedit.text()
        if len(api_key) == 0:
            aqt.utils.showCritical('Please enter AwesomeTTS Plus API Key', parent=parent_dialog, title='AwesomeTTS Plus Account Info')
            return
        data = self._addon.languagetools.account_info(api_key)
        lines = []
        for key, value in data.items():
            html = f'<b>{key}</b>: {value}'
            if key == 'update_url':
                html = f"""<br/><a href='{value}'>Upgrade / Downgrade / Payment Info</a>"""
            if key == 'cancel_url':
                html = f"""<br/><a href='{value}'>Cancel Plan</a>"""
            lines.append(html)
        account_info_str = '<br/>'.join(lines)
        aqt.utils.showInfo(account_info_str, parent=parent_dialog, title='AwesomeTTS Plus Account Info', textFormat='rich')

