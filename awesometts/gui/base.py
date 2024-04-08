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
Base classes for GUI elements

Provides classes that can be extended for constructing GUI elements for
use with AwesomeTTS.
"""

import inspect

import aqt.qt
import aqt.utils

try:
    import PyQt6
    QComboBoxType = PyQt6.QtWidgets.QComboBox
except:
    import PyQt5
    QComboBoxType = PyQt5.QtWidgets.QComboBox

from ..paths import ICONS
from .common import Label, Note, ICON

__all__ = ['Dialog', 'ServiceDialog']

# all methods might need 'self' in the future, pylint:disable=R0201


class Dialog(aqt.qt.QDialog):
    """
    Base used for all dialog windows.
    """

    _FONT_HEADER = aqt.qt.QFont()
    _FONT_HEADER.setPointSize(12)
    _FONT_HEADER.setBold(True)

    _FONT_INFO = aqt.qt.QFont()
    _FONT_INFO.setItalic(True)

    _FONT_LABEL = aqt.qt.QFont()
    _FONT_LABEL.setBold(True)

    _FONT_TITLE = aqt.qt.QFont()
    _FONT_TITLE.setPointSize(16)
    _FONT_TITLE.setBold(True)

    _SPACING = 10

    __slots__ = [
        '_addon',  # bundle of config, logger, paths, router, version
        '_title',  # description of this window
    ]

    def __init__(self, title, addon, parent):
        """
        Set the modal status for the dialog, sets its layout to the
        return value of the _ui() method, and sets a default title.
        """

        self._addon = addon
        self._addon.logger.debug(
            "Constructing %s (%s) dialog",
            title, self.__class__.__name__,
        )
        self._title = title

        super(Dialog, self).__init__(parent)

        self.setModal(True)
        self.setLayout(self._ui())
        aqt.utils.disable_help_button(self)
        self.setWindowIcon(ICON)
        self.setWindowTitle(
            title if "AwesomeTTS" in title
            else "AwesomeTTS: " + title
        )

    # UI Construction ########################################################

    def _ui(self):
        """
        Returns a vertical layout with a banner.

        Subclasses should call this method first when overriding so that
        all dialogs have the same banner.
        """

        layout = aqt.qt.QVBoxLayout()
        layout.addLayout(self._ui_banner())
        layout.addWidget(self._ui_divider(aqt.qt.QFrame.Shape.HLine))

        return layout

    def _ui_banner(self):
        """
        Returns a horizontal layout with some title text, a strecher,
        and version text.

        For subclasses, this method will be called automatically as part
        of the base class _ui() method.
        """

        title = Label(self._title)
        title.setFont(self._FONT_TITLE)



        self.version_label = Label("AwesomeTTS\nv" + self._addon.version)
        self.version_label.setFont(self._FONT_INFO)

        layout = aqt.qt.QHBoxLayout()
        layout.addWidget(title)
        layout.addSpacing(self._SPACING)
        layout.addStretch()
        layout.addWidget(self.version_label)

        if self._addon.languagetools.use_plus_mode():
            self.show_plus_mode()

        return layout

    def _ui_divider(self, orientation_style=aqt.qt.QFrame.Shape.VLine):
        """
        Returns a divider.

        For subclasses, this method will be called automatically as part
        of the base class _ui() method.
        """

        frame = aqt.qt.QFrame()
        frame.setFrameStyle(orientation_style | aqt.qt.QFrame.Shadow.Sunken)

        return frame

    def _ui_buttons(self):
        """
        Returns a horizontal row of standard dialog buttons, with "OK"
        and "Cancel", and "Help", which links to AwesomeTTS Tutorials
        """

        buttons = aqt.qt.QDialogButtonBox()
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.helpRequested.connect(self.open_tutorials)

        buttons.setStandardButtons(
            aqt.qt.QDialogButtonBox.StandardButton.Help |
            aqt.qt.QDialogButtonBox.StandardButton.Cancel |
            aqt.qt.QDialogButtonBox.StandardButton.Ok
        )

        for btn in buttons.buttons():
            if buttons.buttonRole(btn) == aqt.qt.QDialogButtonBox.ButtonRole.AcceptRole:
                btn.setObjectName('okay')
            elif buttons.buttonRole(btn) == aqt.qt.QDialogButtonBox.ButtonRole.RejectRole:
                btn.setObjectName('cancel')


        return buttons

    # Events #################################################################

    def show(self, *args, **kwargs):
        """
        Writes a log message and pass onto superclass.
        """

        self._addon.logger.debug("Showing '%s' dialog", self.windowTitle())
        super(Dialog, self).show(*args, **kwargs)

    # Auxiliary ##############################################################

    def show_plus_mode(self):
        # when the user has signed up for the plus mode trial
        version_str = f'AwesomeTTS <span style="color:#FF0000; font-weight: bold;">Plus</span>' +\
            f'<br/>v{self._addon.version}'
        self.version_label.setText(version_str)
        self.version_label.setTextFormat(aqt.qt.Qt.TextFormat.RichText)        

    def open_tutorials(self):
        url = 'https://www.vocab.ai/tutorials?utm_campaign=atts_help&utm_source=awesometts&utm_medium=addon'
        self._addon.logger.debug("Launching %s", url)
        aqt.qt.QDesktopServices.openUrl(aqt.qt.QUrl(url))

class ServiceDialog(Dialog):
    """
    Base used for all service-related dialog windows (e.g. single file
    generator, mass file generator, template tag builder).
    """

    _OPTIONS_WIDGETS = (QComboBoxType, aqt.qt.QDoubleSpinBox, aqt.qt.QSpinBox)

    _INPUT_WIDGETS = _OPTIONS_WIDGETS + (aqt.qt.QAbstractButton,
                                         aqt.qt.QLineEdit, aqt.qt.QTextEdit)

    __slots__ = [
        '_alerts',       # API to display error messages
        '_ask',          # API to ask for text input
        '_panel_built',  # dict, svc_id to True if panel has been constructed
        '_panel_set',    # dict, svc_id to True if panel values have been set
        '_svc_id',       # active service ID
        '_svc_count',    # how many services this dialog has access to
    ]

    def __init__(self, alerts, ask, *args, **kwargs):
        """
        Initialize the mechanism for keeping track of which panels are
        loaded.
        """

        self._alerts = alerts
        self._ask = ask
        self._panel_built = {}
        self._panel_set = {}
        self._svc_id = None
        self._svc_count = 0

        super(ServiceDialog, self).__init__(*args, **kwargs)

    # UI Construction ########################################################

    def _ui(self):
        """
        Return a services panel and a control panel.
        """

        layout = super(ServiceDialog, self)._ui()

        hor = aqt.qt.QHBoxLayout()
        hor.addLayout(self._ui_services())
        hor.addSpacing(self._SPACING)
        hor.addWidget(self._ui_divider())
        hor.addSpacing(self._SPACING)
        hor.addLayout(self._ui_control())

        layout.addLayout(hor)
        return layout

    def _ui_services(self):
        """
        Return the service panel, which includes a dropdown for the
        service and a stacked widget for each service's options.
        """

        dropdown = aqt.qt.QComboBox()
        dropdown.setObjectName('service')

        stack = aqt.qt.QStackedWidget()
        stack.setObjectName('panels')

        for svc_id, text in self._addon.router.get_services():
            dropdown.addItem(text, svc_id)

            svc_layout = aqt.qt.QGridLayout()
            svc_layout.addWidget(Label("Pass the following to %s:" % text),
                                 0, 0, 1, 2)

            svc_widget = aqt.qt.QWidget()
            svc_widget.setLayout(svc_layout)

            stack.addWidget(svc_widget)
        self._svc_count = dropdown.count()

        # one extra widget for displaying a group
        group_layout = aqt.qt.QVBoxLayout()
        group_layout.addWidget(Note())
        group_layout.addStretch()
        group_widget = aqt.qt.QWidget()
        group_widget.setLayout(group_layout)
        stack.addWidget(group_widget)

        dropdown.activated.connect(self._on_service_activated)
        dropdown.currentIndexChanged.connect(self._on_preset_reset)

        self.plus_mode_stack = aqt.qt.QStackedWidget()
        night_mode = aqt.theme.theme_manager.night_mode
        signup_button_stylesheet = 'background-color: #69F0AE;'
        if night_mode:
            signup_button_stylesheet = 'background-color: #69F0AE; color: #000000;'
        font_large = aqt.qt.QFont()
        font_large.setBold(True)            

        # first layer: plus mode not activated
        horizontal_layout = aqt.qt.QHBoxLayout()
        plus_mode_url = 'https://www.vocab.ai/awesometts-plus?utm_campaign=atts_services&utm_source=awesometts&utm_medium=addon'
        plus_mode_label = 'Get All Voices'
        plus_mode_button = aqt.qt.QPushButton(plus_mode_label) 
        plus_mode_button.setStyleSheet(signup_button_stylesheet)
        plus_mode_button.setFont(font_large)
        def activate_plus_mode_lambda():
            def activate_plus():
                self.plus_mode_stack.setCurrentIndex(1)
            return activate_plus
        plus_mode_button.pressed.connect(activate_plus_mode_lambda())

        plus_mode_description=aqt.qt.QLabel()
        font_small = aqt.qt.QFont()
        font_small.setPointSize(8)
        description_text = '<i>1200+ High quality TTS voices<br/> Signup for trial in one second, just enter your email.</i>'
        plus_mode_description.setText(description_text)
        plus_mode_description.setFont(font_small)
        horizontal_layout.addWidget(plus_mode_button)
        horizontal_layout.addWidget(plus_mode_description)
        stack_widget = aqt.qt.QWidget()
        stack_widget.setLayout(horizontal_layout) 
        self.plus_mode_stack.addWidget(stack_widget)
        
        # second layer: user signining up
        horizontal_layout = aqt.qt.QHBoxLayout()
        email_text_input = aqt.qt.QLineEdit()
        email_text_input.setPlaceholderText("enter your email")
        horizontal_layout.addWidget(email_text_input)
        signup_button = aqt.qt.QPushButton('Sign Up')
        signup_button.setStyleSheet(signup_button_stylesheet)
        signup_button.setFont(font_large)
        horizontal_layout.addWidget(signup_button)
        signup_status_label = aqt.qt.QLabel("<i>Enter email to get premium voices.</i>")
        signup_status_label.setFont(font_small)
        horizontal_layout.addWidget(signup_status_label)
        stack_widget = aqt.qt.QWidget()
        stack_widget.setLayout(horizontal_layout) 
        self.plus_mode_stack.addWidget(stack_widget)

        def signup_lambda(email_input, status_label):
            def signup():
                email = email_input.text().strip()
                # status_label.setText(email)
                # try to request a trial key
                trial_signup_result = self._addon.languagetools.request_trial_key(email)
                if 'error' in trial_signup_result:
                    status_label.setText(trial_signup_result['error'])
                elif 'api_key' in trial_signup_result:
                    api_key = trial_signup_result['api_key']
                    # save in the config
                    self._addon.config['plus_api_key'] = api_key
                    # set it in memory in the languagetools object
                    self._addon.languagetools.set_api_key(api_key)
                    # this will show AwesomeTTS plus in the version label
                    self.show_plus_mode()
                    # force currently selected service UI to reload
                    # find index of currently selected service
                    self.clean_built_services()
                    dropdown = self.findChild(aqt.qt.QComboBox, 'service')
                    idx = dropdown.currentIndex()
                    self._on_service_activated(idx, force_options_reload=True)
                    # show signed up message
                    self.plus_mode_stack.setCurrentIndex(3)
            return signup
        signup_button.pressed.connect(signup_lambda(email_text_input, signup_status_label))

        # third layer: empty (plus mode activated)
        horizontal_layout = aqt.qt.QHBoxLayout()
        stack_widget = aqt.qt.QWidget()
        stack_widget.setLayout(horizontal_layout) 
        self.plus_mode_stack.addWidget(stack_widget)       

        # fourth layer: show that you are now signed up to plus mode
        horizontal_layout = aqt.qt.QHBoxLayout()
        signed_up_text = """<i>You now have access to all premium voices from Azure, Google, Amazon, Watson, Naver, Forvo.</i>"""
        signed_up_label = aqt.qt.QLabel(signed_up_text)
        signed_up_label.setWordWrap(True)
        signed_up_label.setFont(font_small)
        horizontal_layout.addWidget(signed_up_label)
        stack_widget = aqt.qt.QWidget()
        stack_widget.setLayout(horizontal_layout) 
        self.plus_mode_stack.addWidget(stack_widget)         

        if not self._addon.languagetools.use_plus_mode():
            self.plus_mode_stack.setCurrentIndex(0)
        else:
            self.plus_mode_stack.setCurrentIndex(2)


        hor = aqt.qt.QHBoxLayout()
        hor.addWidget(Label("Generate using"))
        hor.addWidget(dropdown)
        hor.addWidget(self.plus_mode_stack)
        hor.addStretch()

        header = Label("Configure Service")
        header.setFont(self._FONT_HEADER)

        layout = aqt.qt.QVBoxLayout()
        layout.addWidget(header)
        layout.addLayout(hor)
        layout.addWidget(stack)
        layout.addStretch()
        layout.addLayout(self._ui_services_presets())

        return layout

    def _ui_services_presets(self):
        """Returns the preset controls as a horizontal layout."""

        label = Label("Quickly access this service later?")
        label.setObjectName('presets_label')

        dropdown = aqt.qt.QComboBox()
        dropdown.setObjectName('presets_dropdown')
        dropdown.setSizePolicy(aqt.qt.QSizePolicy.Policy.MinimumExpanding,
                               aqt.qt.QSizePolicy.Policy.Preferred)
        dropdown.activated.connect(self._on_preset_activated)

        delete = aqt.qt.QPushButton(aqt.qt.QIcon(f'{ICONS}/editdelete.png'), "")
        delete.setObjectName('presets_delete')
        delete.setIconSize(aqt.qt.QSize(16, 16))
        delete.setFixedSize(18, 18)
        delete.setFlat(True)
        delete.setToolTip("Remove this service configuration from\n"
                          "the list of remembered services.")
        delete.clicked.connect(self._on_preset_delete)

        save = aqt.qt.QPushButton("Save")
        save.setObjectName('presets_save')
        # save.setFixedWidth(save.fontMetrics().width(save.text()) + 20)
        save.setToolTip("Remember the selected service and its input\n"
                        "settings so that you can quickly access it later.")
        save.clicked.connect(self._on_preset_save)

        layout = aqt.qt.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(dropdown)
        layout.addWidget(delete)
        layout.addSpacing(self._SPACING)
        layout.addWidget(save)

        return layout

    def _ui_control(self):
        """
        Returns the "Test Settings" header, the text input and a preview
        button.

        Subclasses should either extend this or replace it, but if they
        replace this (e.g. to display the text input differently), the
        objects created must have setObjectName() called with 'text'
        and 'preview'.
        """

        text = aqt.qt.QLineEdit()
        text.keyPressEvent = lambda key_event: (
            self._on_preview()
            if key_event.key() in [aqt.qt.Qt.Key.Key_Enter, aqt.qt.Qt.Key.Key_Return]
            else aqt.qt.QLineEdit.keyPressEvent(text, key_event)
        )
        text.setObjectName('text')
        text.setPlaceholderText("type a phrase to test...")

        button = aqt.qt.QPushButton("&Preview")
        button.setObjectName('preview')
        button.clicked.connect(self._on_preview)

        hor = aqt.qt.QHBoxLayout()
        hor.addWidget(text)
        hor.addWidget(button)

        header = Label("Preview")
        header.setFont(self._FONT_HEADER)

        layout = aqt.qt.QVBoxLayout()
        layout.addWidget(header)
        layout.addLayout(hor)
        layout.addStretch()
        layout.addSpacing(self._SPACING)

        return layout

    # Events #################################################################

    def show(self, *args, **kwargs):
        """
        Recall the last used (or default) service and call in to
        activate its panel, populate presets, and then clear the input
        text box.
        """

        self._panel_set = {}  # these must be reloaded with each window open

        dropdown = self.findChild(aqt.qt.QComboBox, 'service')

        # refresh the list of groups
        while dropdown.count() > self._svc_count:
            dropdown.removeItem(dropdown.count() - 1)
        groups = list(self._addon.config['groups'].keys())
        if groups:
            dropdown.insertSeparator(dropdown.count())
            for group in sorted(groups):
                dropdown.addItem(group, 'group:' + group)

        idx = max(dropdown.findData(self._addon.config['last_service']), 0)
        dropdown.setCurrentIndex(idx)
        self._on_service_activated(idx, initial=True)
        self._on_preset_refresh(select=True)

        text = self.findChild(aqt.qt.QWidget, 'text')
        try:
            text.setText("")
        except AttributeError:
            text.setPlainText("")

        super(ServiceDialog, self).show(*args, **kwargs)

    def clean_built_services(self):
        # clear the set of built panels
        self._panel_built = {}
        self._panel_set = {}
        # actually empty out the widgets in the panels
        stack = self.findChild(aqt.qt.QStackedWidget, 'panels')
        for stack_id in range(stack.count()):
            widget = stack.widget(stack_id)
            widget_layout = widget.layout()

            # print(f'*** clean_built_services num children: {widget_layout.count()}')
            for i in reversed(range(1, widget_layout.count())): 
                # print(f'processing child {i}')
                widget = widget_layout.itemAt(i).widget()
                if widget != None:
                    widget.setParent(None)



    def _on_service_activated(self, idx, initial=False, use_options=None, force_options_reload=False):
        """
        Construct the target widget if it has not already been built,
        recall the last-used values for the options, and then switch the
        stack to it.
        """

        combo = self.findChild(aqt.qt.QComboBox, 'service')
        svc_id = combo.itemData(idx)
        stack = self.findChild(aqt.qt.QStackedWidget, 'panels')
        save = self.findChild(aqt.qt.QPushButton, 'presets_save')

        if svc_id.startswith('group:'):  # we handle groups differently
            svc_id = svc_id[6:]
            group = self._addon.config['groups'][svc_id]
            presets = [preset for preset in group['presets'] if preset]

            stack.setCurrentIndex(stack.count() - 1)
            stack.widget(stack.count() - 1).findChild(aqt.qt.QLabel).setText(
                svc_id +
                (" has no presets yet." if len(presets) == 0
                 else " uses " + presets[0] + "." if len(presets) == 1
                 else ((" randomly selects" if group['mode'] == 'random'
                        else " tries in-order") + " from:\n -" +
                       "\n -".join(presets[0:5]) +
                       ("\n    (... and %d more)" % (len(presets) - 5)
                        if len(presets) > 5 else ""))) +
                "\n\n"
                "Go to AwesomeTTS config for group setup.\n"
                "Access preset options in dropdown below."
            )
            save.setEnabled(False)
            return

        save.setEnabled(True)
        panel_unbuilt = svc_id not in self._panel_built
        panel_unset = svc_id not in self._panel_set

        if panel_unbuilt or panel_unset or use_options:
            widget = stack.widget(idx)
            options = self._addon.router.get_options(svc_id, force_options_reload=force_options_reload)

            if panel_unbuilt:
                self._panel_built[svc_id] = True
                self._on_service_activated_build(svc_id, widget, options)

            if panel_unset or use_options:
                self._panel_set[svc_id] = True
                self._on_service_activated_set(svc_id, widget, options,
                                               use_options)

        stack.setCurrentIndex(idx)

        if panel_unbuilt and not initial:
            self.adjustSize()

        self._svc_id = svc_id
        help_svc = self.findChild(aqt.qt.QAction, 'help_svc')
        if help_svc:
            help_svc.setText("Using the %s service" % combo.currentText())

    def _on_service_activated_build(self, svc_id, widget, options):
        """
        Based on the list of options, build a grid of labels and input
        controls.
        """

        self._addon.logger.debug("Constructing panel for %s", svc_id)

        row = 1
        panel = widget.layout()

        for option in options:
            label = Label(option['label'])
            label.setFont(self._FONT_LABEL)

            if isinstance(option['values'], tuple):
                start, end = option['values'][0], option['values'][1]

                vinput = (
                    aqt.qt.QDoubleSpinBox
                    if isinstance(start, float) or isinstance(end, float)
                    else aqt.qt.QSpinBox
                )()

                vinput.setRange(start, end)
                if len(option['values']) > 2:
                    vinput.setSuffix(" " + option['values'][2])
                vinput.valueChanged.connect(self._on_preset_reset)

            else:  # list of tuples
                vinput = aqt.qt.QComboBox()
                # reduce the maximum number of items displayed, in the hopes this fixes a bug on MacOSx catalina with a large number of voices
                vinput.setMaxVisibleItems(15)
                vinput.setStyleSheet("combobox-popup: 0;")
                for value, text in option['values']:
                    vinput.addItem(text, value)

                if len(option['values']) == 1:
                    vinput.setDisabled(True)
                vinput.currentIndexChanged.connect(self._on_preset_reset)

            panel.addWidget(label, row, 0)
            panel.addWidget(vinput, row, 1, 1, 2)
            row += 1

        extras = self._addon.router.get_extras(svc_id)
        if extras:
            config = self._addon.config

            def glue_edit(edit, key):
                """Wires `textEdited` on `edit`, closing on `key`."""

                def on_text_edited(val):
                    """Updates `extras` dict when user input changes."""
                    config['extras'] = dict(
                        list(config['extras'].items()) +
                        [(
                            svc_id,
                            dict(
                                list(config['extras'].get(svc_id, {}).items()) +
                                [(key, val)]
                            ),
                        )]
                    )

                edit.textEdited.connect(on_text_edited)

            for extra in extras:
                label = Label(extra['label'])
                label.setFont(self._FONT_LABEL)

                edit = aqt.qt.QLineEdit()
                key = extra['key']
                try:
                    edit.setText(config['extras'][svc_id][key])
                except KeyError:
                    pass

                glue_edit(edit, key)

                panel.addWidget(label, row, 0)
                panel.addWidget(edit, row, 1)
                panel.addWidget(Label("(global)"), row, 2)
                row += 1

        note = Note(self._addon.router.get_desc(svc_id))
        note.setFont(self._FONT_INFO)

        panel.addWidget(note, row, 0, 1, 3, aqt.qt.Qt.AlignmentFlag.AlignTop)
        panel.setRowStretch(row, 1)

    def _on_service_activated_set(self, svc_id, widget, options,
                                  use_options=None):
        """
        Based on the list of options and the user's last known options,
        restore the values of all input controls.
        """

        self._addon.logger.debug("Restoring options for %s", svc_id)

        last_options = (use_options or
                        self._addon.config['last_options'].get(svc_id, {}))
        vinputs = widget.findChildren(self._OPTIONS_WIDGETS)

        if len(vinputs) != len(options):
            print(f'vinputs: {vinputs}')
            print(f'options: {options}')
            raise Exception(f'len(vinputs): {len(vinputs)} len(options): {len(options)}')
        assert len(vinputs) == len(options)

        for i, opt in enumerate(options):
            vinput = vinputs[i]

            if isinstance(opt['values'], tuple):
                # spinbox
                try:
                    val = last_options[opt['key']]
                    if not opt['values'][0] <= val <= opt['values'][1]:
                        raise ValueError

                except (KeyError, ValueError):
                    try:
                        val = opt['default']
                        if not opt['values'][0] <= val <= opt['values'][1]:
                            raise ValueError

                    except (KeyError, ValueError):
                        val = opt['values'][0]

                vinput.setValue(val)

            else:
                # qcombobox
                try:
                    idx = vinput.findData(last_options[opt['key']])
                    if idx < 0:
                        raise ValueError

                except (KeyError, ValueError):
                    try:
                        idx = vinput.findData(opt['default'])
                        if idx < 0:
                            raise ValueError

                    except (KeyError, ValueError):
                        idx = 0

                vinput.setCurrentIndex(idx)

    def _on_preset_refresh(self, select=None):
        """Updates the view of the preset controls."""

        label = self.findChild(Label, 'presets_label')
        dropdown = self.findChild(aqt.qt.QComboBox, 'presets_dropdown')
        delete = self.findChild(aqt.qt.QPushButton, 'presets_delete')
        presets = self._addon.config['presets']

        dropdown.clear()
        dropdown.addItem("Load Preset...    ")
        dropdown.insertSeparator(1)
        delete.setDisabled(True)

        if presets:
            label.hide()
            dropdown.show()
            dropdown.addItems(sorted(presets.keys(),
                                     key=lambda key: key.lower()))
            if select:
                if select is True:
                    # if one of the presets exactly match the svc_id and
                    # options that were just deserialized, then we want to
                    # select that one in the dropdown (this makes getting the
                    # same "preset" in the template helper dialog easier)
                    svc_id, options = self._get_service_values()
                    select = next(
                        (
                            name for name, preset in list(presets.items())
                            if svc_id == preset.get('service')
                            and not next(
                                (True for key, value in list(options.items())
                                 if preset.get(key) != options.get(key)),
                                False,
                            )
                        ),
                        None,
                    ) if options else None

                if select:
                    idx = dropdown.findText(select)
                    if idx > 0:
                        dropdown.setCurrentIndex(idx)
                        delete.setDisabled(False)
            delete.show()
        else:
            label.show()
            dropdown.hide()
            delete.hide()

    def _on_preset_reset(self):
        """Sets preset dropdown back and disables delete button."""

        if next((True
                 for frame in inspect.stack()
                 if frame[3] == '_on_preset_activated'),
                False):
            return  # ignore value change events triggered by preset loads

        self.findChild(aqt.qt.QPushButton, 'presets_delete').setDisabled(True)
        self.findChild(aqt.qt.QComboBox, 'presets_dropdown').setCurrentIndex(0)

    def _on_preset_save(self):
        """Saves the current service state back as a preset."""

        svc_id, options = self._get_service_values()
        assert "bad get_service_values() value", \
               not svc_id.startswith('group:') and options
        svc_name = self.findChild(aqt.qt.QComboBox, 'service').currentText()

        name, okay = self._ask(
            title="Save a Preset Service Configuration",
            prompt=(
                "Please enter a name for <strong>%s</strong> with "
                "<strong>%s</strong> set to <kbd>%s</kbd>." %
                ((svc_name,) + list(options.items())[0])

                if len(options) == 1 else

                "Please enter a name for <strong>%s</strong> with the "
                "following:<br>%s" % (
                    svc_name,
                    "<br>".join(
                        "- <strong>%s:</strong> <kbd>%s</kbd>" % item
                        for item in sorted(options.items())
                    )
                )

                if len(options) > 1 else

                f"Please enter a name for <strong>{svc_name}</strong>."
            ),
            default=(svc_name if not options.get('voice')
                     else "%s (%s)" % (svc_name, options['voice'])),
            parent=self,
        )

        name = okay and name.strip()
        if name:
            self._addon.config['presets'] = dict(
                list(self._addon.config['presets'].items()) +
                [(name, dict([('service', svc_id)] + list(options.items())))]
            )
            self._on_preset_refresh(select=name)

    def _on_preset_activated(self, idx):
        """Loads preset at given index and toggles delete button."""

        delete = self.findChild(aqt.qt.QPushButton, 'presets_delete')

        if idx > 0:
            delete.setEnabled(True)
            name = self.findChild(aqt.qt.QComboBox,
                                  'presets_dropdown').currentText()
            try:
                preset = self._addon.config['presets'][name]
                svc_id = preset['service']
            except KeyError:
                self._alerts("%s preset is invalid." % name, self)
                return

            dropdown = self.findChild(aqt.qt.QComboBox, 'service')
            idx = dropdown.findData(svc_id)
            if idx < 0:
                self._alerts(self._addon.router.get_unavailable_msg(svc_id),
                             self)
                return

            dropdown.setCurrentIndex(idx)
            self._on_service_activated(idx, use_options=preset)
        else:
            delete.setEnabled(False)

    def _on_preset_delete(self):
        """Removes the currently selected preset from configuration."""

        presets = dict(self._addon.config['presets'])
        try:
            del presets[self.findChild(aqt.qt.QComboBox,
                                       'presets_dropdown').currentText()]
        except KeyError:
            pass
        else:
            self._addon.config['presets'] = presets

        self._on_preset_refresh()

    def _on_preview(self):
        """
        Handle parsing the inputs and passing onto the router.
        """

        svc_id, values = self._get_service_values()
        text_input, text_value = self._get_service_text()
        self._disable_inputs()

        text_value = self._addon.strip.from_user(text_value)
        callbacks = dict(
            done=lambda: self._disable_inputs(False),
            okay=self._addon.player.preview,
            fail=lambda exception, text_value: self._alerts(
                "Cannot preview the input phrase with these settings.\n\n%s" %
                str(exception),
                self,
            ),
            then=text_input.setFocus,
        )

        if svc_id.startswith('group:'):
            config = self._addon.config
            self._addon.router.group(text=text_value,
                                     group=config['groups'][svc_id[6:]],
                                     presets=config['presets'],
                                     callbacks=callbacks)
        else:
            self._addon.router(svc_id=svc_id, text=text_value,
                               options=values, callbacks=callbacks)

    # Auxiliary ##############################################################

    def _disable_inputs(self, flag=True):
        """
        Mass disable (or enable if flag is False) all inputs, except the
        cancel button.
        """

        for widget in (
                widget
                for widget in self.findChildren(self._INPUT_WIDGETS)
                if widget.objectName() != 'cancel'
                and (not isinstance(widget, aqt.qt.QComboBox) or
                     len(widget) > 1)
        ):
            widget.setDisabled(flag)

        if not flag:
            self.findChild(aqt.qt.QPushButton, 'presets_delete').setEnabled(
                self.findChild(aqt.qt.QComboBox,
                               'presets_dropdown').currentIndex() > 0
            )
            self.findChild(aqt.qt.QPushButton, 'presets_save').setEnabled(
                self.findChild(aqt.qt.QComboBox,
                               'service').currentIndex() < self._svc_count
            )

    def _get_service_values(self):
        """
        Return the service ID and a dict of all the options.
        """

        dropdown = self.findChild(aqt.qt.QComboBox, 'service')
        idx = dropdown.currentIndex()
        svc_id = dropdown.itemData(idx)
        if svc_id.startswith('group:'):
            return svc_id, None

        vinputs = self.findChild(aqt.qt.QStackedWidget, 'panels') \
            .widget(idx).findChildren(self._OPTIONS_WIDGETS)
        options = self._addon.router.get_options(svc_id)

        assert len(options) == len(vinputs)

        return svc_id, {
            options[i]['key']:
                vinputs[i].value()
                if isinstance(vinputs[i], aqt.qt.QDoubleSpinBox) or isinstance(vinputs[i], aqt.qt.QSpinBox)  # aqt.qt.QDoubleSpinBox, aqt.qt.QSpinBox
                else vinputs[i].itemData(vinputs[i].currentIndex())
            for i in range(len(options))
        }

    def _get_service_text(self):
        """
        Return the text box and its phrase.
        """

        text_input = self.findChild(aqt.qt.QWidget, 'text')
        try:
            text_value = text_input.text()
        except AttributeError:
            text_value = text_input.toPlainText()

        return text_input, text_value

    def _get_all(self):
        """
        Returns a dict of the options that need to be updated to
        remember and process the state of the form.
        """

        svc_id, values = self._get_service_values()
        return {
            'last_service': svc_id,
            'last_options': {
                **self._addon.config['last_options'],
                **{svc_id: values}
            },
        } if values else dict(last_service=svc_id)
