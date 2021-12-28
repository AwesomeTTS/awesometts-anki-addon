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
import aqt.utils

from PyQt5 import QtCore, QtWidgets, QtGui

from ..paths import ICONS
from .base import Dialog
from .common import Checkbox, Label, Note, Slate
from .common import key_event_combo, key_combo_desc
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
        'lame_flags', 'launch_browser_generator', 'launch_browser_stripper',
        'launch_configurator', 'launch_editor_generator', 'launch_templater',
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

    _PROPERTY_WIDGETS = (Checkbox, QtWidgets.QComboBox, QtWidgets.QLineEdit,
                         QtWidgets.QPushButton, QtWidgets.QSpinBox, QtWidgets.QListView)

    __slots__ = ['_alerts', '_ask', '_preset_editor', '_group_editor',
                 '_sul_compiler']

    def __init__(self, alerts, ask, sul_compiler, *args, **kwargs):
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
        tabs = QtWidgets.QTabWidget()

        for content, icon, label in [
                (self._ui_tabs_text, 'editclear', "Text"),
                (self._ui_tabs_mp3gen, 'document-new', "MP3s"),
                (self._ui_tabs_windows, 'kpersonalizer', "Windows"),
                (self._ui_tabs_services, 'rating', "Services"),
                (self._ui_tabs_advanced, 'configure', "Advanced"),
        ]:
            if use_icons:
                tabs.addTab(content(), QtGui.QIcon(f'{ICONS}/{icon}.png'),
                            label)
            else:  # active tabs do not display correctly on Mac OS X w/ icons
                tabs.addTab(content(), label)

        tabs.currentChanged.connect(lambda: (tabs.adjustSize(),
                                             self.adjustSize()))
        return tabs


    def _ui_tabs_text(self):
        """Returns the "Text" tab."""

        layout = QtWidgets.QVBoxLayout()
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

        tab = QtWidgets.QWidget()
        tab.setLayout(layout)
        return tab

    def _ui_tabs_text_mode(self, infix, label, *args, **kwargs):
        """Returns group box for the given text manipulation context."""

        subtabs = QtWidgets.QTabWidget()
        subtabs.setTabPosition(QtWidgets.QTabWidget.West)

        for sublabel, sublayout in [
                ("Simple", self._ui_tabs_text_mode_simple(infix, *args,
                                                          **kwargs)),
                ("Advanced", self._ui_tabs_text_mode_adv(infix)),
        ]:
            subwidget = QtWidgets.QWidget()
            subwidget.setLayout(sublayout)
            subtabs.addTab(subwidget, sublabel)

        layout = QtWidgets.QVBoxLayout()
        # TODO
        # layout.setCanvasMargin(0)
        layout.addWidget(subtabs)

        group = QtWidgets.QGroupBox(label)
        group.setFlat(True)
        group.setLayout(layout)

        _, top, right, bottom = layout.getContentsMargins()
        layout.setContentsMargins(0, top, right, bottom)
        _, top, right, bottom = group.getContentsMargins()
        group.setContentsMargins(0, top, right, bottom)
        return group

    def _ui_tabs_text_mode_simple(self, infix, cloze_description,
                                  cloze_options, template_options=False):
        """
        Returns a layout with the "simple" configuration options
        available for manipulating text from the given context.
        """

        select = QtWidgets.QComboBox()
        for option_value, option_text in cloze_options:
            select.addItem(option_text, option_value)
        select.setObjectName(infix.join(['sub', 'cloze']))

        hor = QtWidgets.QHBoxLayout()
        hor.addWidget(Label(cloze_description))
        hor.addWidget(select)
        hor.addStretch()

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.addLayout(hor)

        if template_options:
            hor = QtWidgets.QHBoxLayout()
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



        hor = QtWidgets.QHBoxLayout()
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

        line_edit = QtWidgets.QLineEdit()
        line_edit.setObjectName(infix.join(['spec', suffix]))
        line_edit.setValidator(self._ui_tabs_text_mode_simple_spec.ucsv)
        line_edit.setFixedWidth(50)

        hor = QtWidgets.QHBoxLayout()
        hor.addWidget(Label(labels[0]))
        hor.addWidget(line_edit)
        hor.addWidget(Label(labels[1]))
        if wrap:
            hor.addWidget(Checkbox("wrap in ellipses",
                                   ''.join(['spec', infix, suffix, '_wrap'])))
        hor.addStretch()
        return hor

    class _UniqueCharacterStringValidator(QtGui.QValidator):
        """QValidator returning unique, sorted characters."""

        def fixup(self, original):
            """Returns unique characters from original, sorted."""

            return ''.join(sorted({c for c in original if not c.isspace()}))

        def validate(self, original, offset):  # pylint:disable=W0613
            """Fixes original text and resets cursor to end of line."""

            filtered = self.fixup(original)
            return QtGui.QValidator.Acceptable, filtered, len(filtered)

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

        vert = QtWidgets.QVBoxLayout()
        vert.addWidget(self._ui_tabs_mp3gen_filenames())
        vert.addWidget(self._ui_tabs_mp3gen_lame())
        vert.addWidget(self._ui_tabs_mp3gen_throttle())
        vert.addStretch()

        tab = QtWidgets.QWidget()
        tab.setLayout(vert)
        return tab

    def _ui_tabs_mp3gen_filenames(self):
        """Returns the "Filenames of MP3s" group."""

        dropdown = QtWidgets.QComboBox()
        dropdown.setObjectName('filenames')
        dropdown.addItem("hashed (safe and portable)", 'hash')
        dropdown.addItem("human-readable (may not work everywhere)", 'human')

        dropdown_line = QtWidgets.QHBoxLayout()
        dropdown_line.addWidget(Label("Filenames should be "))
        dropdown_line.addWidget(dropdown)
        dropdown_line.addStretch()

        human = QtWidgets.QLineEdit()
        human.setObjectName('filenames_human')
        human.setPlaceholderText("e.g. {{service}} {{voice}} - {{text}}")
        human.setEnabled(False)

        human_line = QtWidgets.QHBoxLayout()
        human_line.addWidget(Label("Format human-readable filenames as "))
        human_line.addWidget(human)
        human_line.addWidget(Label(".mp3"))

        dropdown.currentIndexChanged. \
            connect(lambda index: human.setEnabled(index > 0))

        vertical = QtWidgets.QVBoxLayout()
        vertical.addLayout(dropdown_line)
        vertical.addLayout(human_line)
        vertical.addWidget(Note("Changes are not retroactive to old files."))

        group = QtWidgets.QGroupBox("Filenames of MP3s Stored in Your Collection")
        group.setLayout(vertical)

        return group

    def _ui_tabs_mp3gen_lame(self):
        """Returns the "LAME Transcoder" input group."""

        flags = QtWidgets.QLineEdit()
        flags.setObjectName('lame_flags')
        flags.setPlaceholderText("e.g. '-q 5' for medium quality")

        rtr = self._addon.router
        vert = QtWidgets.QVBoxLayout()
        vert.addWidget(Note("Specify flags passed to lame when making MP3s."))
        vert.addWidget(flags)
        vert.addWidget(Note("Affects %s. Changes are not retroactive to old "
                            "files." %
                            ', '.join(rtr.by_trait(rtr.Trait.TRANSCODING))))

        group = QtWidgets.QGroupBox("LAME Transcoder")
        group.setLayout(vert)
        return group

    def _ui_tabs_mp3gen_throttle(self):
        """Returns the "Download Throttling" input group."""

        threshold = QtWidgets.QSpinBox()
        threshold.setObjectName('throttle_threshold')
        threshold.setRange(5, 1000)
        threshold.setSingleStep(5)
        threshold.setSuffix(" operations")

        sleep = QtWidgets.QSpinBox()
        sleep.setObjectName('throttle_sleep')
        sleep.setRange(15, 10800)
        sleep.setSingleStep(15)
        sleep.setSuffix(" seconds")

        hor = QtWidgets.QHBoxLayout()
        hor.addWidget(Label("After "))
        hor.addWidget(threshold)
        hor.addWidget(Label(" sleep for "))
        hor.addWidget(sleep)
        hor.addStretch()

        rtr = self._addon.router
        vert = QtWidgets.QVBoxLayout()
        vert.addWidget(Note("Tweak how often AwesomeTTS takes a break when "
                            "mass downloading files from online services."))
        vert.addLayout(hor)
        vert.addWidget(Note("Affects %s." %
                            ', '.join(rtr.by_trait(rtr.Trait.INTERNET))))

        group = QtWidgets.QGroupBox("Download Throttling during Batch Processing")
        group.setLayout(vert)
        return group

    def _ui_tabs_windows(self):
        """Returns the "Window" tab."""

        grid = QtWidgets.QGridLayout()
        for i, (desc, sub) in enumerate([
                ("open configuration in main window", 'configurator'),
                ("insert <tts> tag in template editor", 'templater'),
                ("mass generate MP3s in card browser", 'browser_generator'),
                ("mass remove audio in card browser", 'browser_stripper'),
                ("generate single MP3 in note editor*", 'editor_generator'),
        ]):
            grid.addWidget(Label("To " + desc + ", strike"), i, 0)
            grid.addWidget(self._factory_shortcut('launch_' + sub), i, 1)
        grid.setColumnStretch(1, 1)

        group = QtWidgets.QGroupBox("Window Shortcuts")
        group.setLayout(grid)

        vert = QtWidgets.QVBoxLayout()
        vert.addWidget(group)
        vert.addWidget(Note(
            "* By default, AwesomeTTS binds %(native)s for most actions. If "
            "you use math equations and LaTeX with Anki using the %(native)s "
            "E/M/T keystrokes, you may want to reassign or unbind the "
            "shortcut for generating in the note editor." %
            dict(native=key_combo_desc(QtCore.Qt.ControlModifier |
                                       QtCore.Qt.Key_T))
        ))
        vert.addWidget(Note("Editor and browser shortcuts will take effect "
                            "the next time you open those windows."))
        vert.addWidget(Note("Some keys cannot be used as shortcuts and some "
                            "keystrokes might not work in some windows, "
                            "depending on your operating system and other "
                            "add-ons you are running. You may have to "
                            "experiment to find what works best."))
        vert.addStretch()

        tab = QtWidgets.QWidget()
        tab.setLayout(vert)
        return tab

    def _ui_tabs_services(self):
        """Returns the "Services" tab."""

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._ui_tabs_services_forvo())
        layout.addWidget(self._ui_tabs_services_azure())
        layout.addStretch()

        tab = QtWidgets.QWidget()
        tab.setLayout(layout)
        return tab

    def _ui_tabs_services_forvo(self):

        ver = QtWidgets.QVBoxLayout()
        url_label = QtWidgets.QLabel("Preferred Users (Enter a comma-separated list of preferred Forvo users)")
        ver.addWidget(url_label)

        forvo_preferred_users = QtWidgets.QLineEdit()
        forvo_preferred_users.setObjectName('service_forvo_preferred_users')
        forvo_preferred_users.setPlaceholderText("Enter preferred Forvo users, comma-separated")
        ver.addWidget(forvo_preferred_users)

        group = QtWidgets.QGroupBox("Forvo")
        group.setLayout(ver)
        return group

    def _ui_tabs_services_azure(self):

        ver = QtWidgets.QVBoxLayout()
        url_label = QtWidgets.QLabel("Sleep between each request (for free API keys)")
        ver.addWidget(url_label)
        
        
        azure_sleep_time = QtWidgets.QSpinBox()
        azure_sleep_time.setObjectName('service_azure_sleep_time')
        azure_sleep_time.setRange(0, 10)
        azure_sleep_time.setSuffix(" seconds")

        ver.addWidget(azure_sleep_time)

        group = QtWidgets.QGroupBox("Azure")
        group.setLayout(ver)
        return group

    def _ui_tabs_advanced(self):
        """Returns the "Advanced" tab."""

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._ui_tabs_advanced_presets())
        layout.addWidget(self._ui_tabs_advanced_cache())
        layout.addWidget(self._ui_tabs_advanced_other())
        layout.addWidget(self._ui_tabs_advanced_plus())
        layout.addStretch()

        tab = QtWidgets.QWidget()
        tab.setLayout(layout)
        return tab

    def _ui_tabs_advanced_presets(self):
        """Returns the "Presets" input group."""

        presets_button = QtWidgets.QPushButton("Manage Presets...")
        presets_button.clicked.connect(self._on_presets)

        groups_button = QtWidgets.QPushButton("Manage Groups...")
        groups_button.clicked.connect(self._on_groups)

        hor = QtWidgets.QHBoxLayout()
        hor.addWidget(presets_button)
        hor.addWidget(groups_button)
        hor.addStretch()

        vert = QtWidgets.QVBoxLayout()
        vert.addWidget(Note("Setup services for easy access, menu playback, "
                            "randomization, or fallbacks."))
        vert.addLayout(hor)

        group = QtWidgets.QGroupBox("Service Presets and Groups")
        group.setLayout(vert)
        return group

    def _ui_tabs_advanced_cache(self):
        """Returns the "Caching" input group."""

        days = QtWidgets.QSpinBox()
        days.setObjectName('cache_days')
        days.setRange(0, 9999)
        days.setSuffix(" days")

        hor = QtWidgets.QHBoxLayout()
        hor.addWidget(Label("Delete files older than"))
        hor.addWidget(days)
        hor.addWidget(Label("at exit (zero clears everything)"))
        hor.addStretch()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(Note("AwesomeTTS caches generated audio files and "
                              "remembers failures during each session to "
                              "speed up repeated playback."))
        layout.addLayout(hor)

        abutton = QtWidgets.QPushButton("Delete Files")
        abutton.setObjectName('on_cache')
        abutton.clicked.connect(lambda: self._on_cache_clear(abutton))

        fbutton = QtWidgets.QPushButton("Forget Failures")
        fbutton.setObjectName('on_forget')
        fbutton.clicked.connect(lambda: self._on_forget_failures(fbutton))

        hor = QtWidgets.QHBoxLayout()
        hor.addWidget(abutton)
        hor.addWidget(fbutton)
        layout.addLayout(hor)

        group = QtWidgets.QGroupBox("Caching")
        group.setLayout(layout)
        return group

    def _ui_tabs_advanced_other(self):

        ver = QtWidgets.QVBoxLayout()
        ver.addWidget(Checkbox("Show AwesomeTTS widget on Deck Browser", 'homescreen_show'))

        group = QtWidgets.QGroupBox("Other")
        group.setLayout(ver)
        return group

    def _ui_tabs_advanced_plus(self):

        ver = QtWidgets.QVBoxLayout()
        urlLink="<a href=\"https://languagetools.anki.study/awesometts-plus?utm_campaign=atts_settings&utm_source=awesometts&utm_medium=addon\">1100+ High Quality TTS voices - free trial</a>" 
        url_label = QtWidgets.QLabel(urlLink)
        url_label.setOpenExternalLinks(True)
        ver.addWidget(url_label)

        plus_api_key = QtWidgets.QLineEdit()
        plus_api_key.setObjectName('plus_api_key')
        plus_api_key.setPlaceholderText("enter your API Key")

        verify_button = QtWidgets.QPushButton()
        verify_button.setObjectName('verify_plus_api_key')
        verify_button.setText('Verify')
        verify_button.clicked.connect(lambda: self._on_verify_plus_api_key(verify_button, plus_api_key))

        account_info_button = QtWidgets.QPushButton()
        account_info_button.setObjectName('plus_account_info')
        account_info_button.setText('Account Info / Plan')
        account_info_button.clicked.connect(lambda: self._on_plus_account_info(plus_api_key, self))
        
        hor = QtWidgets.QHBoxLayout()
        hor.addWidget(plus_api_key)
        hor.addWidget(verify_button)
        hor.addWidget(account_info_button)
        ver.addLayout(hor)

        ver.addWidget(Label('Please restart Anki after entering API key'))

        group = QtWidgets.QGroupBox("AwesomeTTS Plus")
        group.setLayout(ver)
        return group        

    # Factories ##############################################################

    def _factory_shortcut(self, object_name):
        """Returns a push button capable of being assigned a shortcut."""

        shortcut = QtWidgets.QPushButton()
        shortcut.atts_pending = False
        shortcut.setObjectName(object_name)
        shortcut.setCheckable(True)
        shortcut.toggled.connect(
            lambda is_down: (
                shortcut.setText("press keystroke"),
                shortcut.setFocus(),  # needed for OS X if text inputs present
            ) if is_down
            else shortcut.setText(key_combo_desc(shortcut.atts_value))
        )
        return shortcut

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
            elif isinstance(widget, QtWidgets.QLineEdit):
                widget.setText(value)
            elif isinstance(widget, QtWidgets.QPushButton):
                widget.atts_value = value
                widget.setText(key_combo_desc(widget.atts_value))
            elif isinstance(widget, QtWidgets.QComboBox):
                widget.setCurrentIndex(max(widget.findData(value), 0))
            elif isinstance(widget, QtWidgets.QSpinBox):
                widget.setValue(value)
            elif isinstance(widget, QtWidgets.QListView):
                widget.setModel(value)

        widget = self.findChild(QtWidgets.QPushButton, 'on_cache')
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

        widget = self.findChild(QtWidgets.QPushButton, 'on_forget')
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

        for list_view in self.findChildren(QtWidgets.QListView):
            for editor in list_view.findChildren(QtWidgets.QWidget, 'editor'):
                list_view.commitData(editor)  # if an editor is open, save it

        self._addon.config.update({
            widget.objectName(): (
                widget.isChecked() if isinstance(widget, Checkbox)
                else widget.atts_value if isinstance(widget, QtWidgets.QPushButton)
                else widget.value() if isinstance(widget, QtWidgets.QSpinBox)
                else widget.itemData(widget.currentIndex()) if isinstance(
                    widget, QtWidgets.QComboBox)
                else [
                    i for i in widget.model().raw_data
                    if i['compiled'] and 'bad_replace' not in i
                ] if isinstance(widget, QtWidgets.QListView)
                else widget.text()
            )
            for widget in self.findChildren(self._PROPERTY_WIDGETS)
            if widget.objectName() in self._PROPERTY_KEYS
        })

        super(Configurator, self).accept()

    def keyPressEvent(self, key_event):  # from PyQt5, pylint:disable=C0103
        """Assign new combo for shortcut buttons undergoing changes."""

        buttons = self._get_pressed_shortcut_buttons()
        if not buttons:
            return super(Configurator, self).keyPressEvent(key_event)

        key = key_event.key()

        if key == QtCore.Qt.Key_Escape:
            for button in buttons:
                button.atts_pending = False
                button.setText(key_combo_desc(button.atts_value))
            return

        if key in [QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete]:
            combo = None
        else:
            combo = key_event_combo(key_event)
            if not combo:
                return

        for button in buttons:
            button.atts_pending = combo
            button.setText(key_combo_desc(combo))

    def keyReleaseEvent(self, key_event):  # from PyQt5, pylint:disable=C0103
        """Disengage all shortcut buttons undergoing changes."""

        buttons = self._get_pressed_shortcut_buttons()
        if not buttons:
            return super(Configurator, self).keyReleaseEvent(key_event)

        elif key_event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            # need to ignore and eat key release on enter/return so that user
            # can activate the button without immediately deactivating it
            return

        for button in buttons:
            if button.atts_pending is not False:
                button.atts_value = button.atts_pending
            button.setChecked(False)

    def _get_pressed_shortcut_buttons(self):
        """Returns all shortcut buttons that are pressed."""

        return [button
                for button in self.findChildren(QtWidgets.QPushButton)
                if (button.isChecked() and
                    (button.objectName().startswith('launch_') or
                     button.objectName().startswith('tts_key_')))]

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

