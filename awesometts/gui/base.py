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

from PyQt5 import QtCore, QtWidgets, QtGui

from ..paths import ICONS
from .common import Label, Note, ICON

__all__ = ['Dialog', 'ServiceDialog']

# all methods might need 'self' in the future, pylint:disable=R0201


class Dialog(QtWidgets.QDialog):
    """
    Base used for all dialog windows.
    """

    _FONT_HEADER = QtGui.QFont()
    _FONT_HEADER.setPointSize(12)
    _FONT_HEADER.setBold(True)

    _FONT_INFO = QtGui.QFont()
    _FONT_INFO.setItalic(True)

    _FONT_LABEL = QtGui.QFont()
    _FONT_LABEL.setBold(True)

    _FONT_TITLE = QtGui.QFont()
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
        self.setWindowFlags(
            self.windowFlags() &
            ~QtCore.Qt.WindowContextHelpButtonHint
        )
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

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(self._ui_banner())
        layout.addWidget(self._ui_divider(QtWidgets.QFrame.HLine))

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

        version = Label("AwesomeTTS\nv" + self._addon.version)
        version.setFont(self._FONT_INFO)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(title)
        layout.addSpacing(self._SPACING)
        layout.addStretch()
        layout.addWidget(version)

        return layout

    def _ui_divider(self, orientation_style=QtWidgets.QFrame.VLine):
        """
        Returns a divider.

        For subclasses, this method will be called automatically as part
        of the base class _ui() method.
        """

        frame = QtWidgets.QFrame()
        frame.setFrameStyle(orientation_style | QtWidgets.QFrame.Sunken)

        return frame

    def _ui_buttons(self):
        """
        Returns a horizontal row of standard dialog buttons, with "OK"
        and "Cancel". If the subclass implements help_request() or
        help_menu(), a "Help" button will also be shown.

        Subclasses must call this method explicitly, at a location of
        their choice. Once called, accept(), reject(), and optionally
        help_request() become wired to the appropriate signals.
        """

        buttons = QtWidgets.QDialogButtonBox()
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        has_help_menu = callable(getattr(self, 'help_menu', None))
        has_help_request = callable(getattr(self, 'help_request', None))

        if has_help_menu or has_help_request:
            if has_help_request:
                buttons.helpRequested.connect(self.help_request)

            buttons.setStandardButtons(
                QtWidgets.QDialogButtonBox.Help |
                QtWidgets.QDialogButtonBox.Cancel |
                QtWidgets.QDialogButtonBox.Ok
            )

        else:
            buttons.setStandardButtons(
                QtWidgets.QDialogButtonBox.Cancel |
                QtWidgets.QDialogButtonBox.Ok
            )

        for btn in buttons.buttons():
            if buttons.buttonRole(btn) == QtWidgets.QDialogButtonBox.AcceptRole:
                btn.setObjectName('okay')
            elif buttons.buttonRole(btn) == QtWidgets.QDialogButtonBox.RejectRole:
                btn.setObjectName('cancel')
            elif (buttons.buttonRole(btn) == QtWidgets.QDialogButtonBox.HelpRole
                  and has_help_menu):
                btn.setMenu(self.help_menu(btn))

        return buttons

    # Events #################################################################

    def show(self, *args, **kwargs):
        """
        Writes a log message and pass onto superclass.
        """

        self._addon.logger.debug("Showing '%s' dialog", self.windowTitle())
        super(Dialog, self).show(*args, **kwargs)

    # Auxiliary ##############################################################

    def _launch_link(self, path):
        """
        Opens a URL on the AwesomeTTS website with the given path.
        """

        url = '/'.join([self._addon.web, path])
        self._addon.logger.debug("Launching %s", url)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))


class ServiceDialog(Dialog):
    """
    Base used for all service-related dialog windows (e.g. single file
    generator, mass file generator, template tag builder).
    """

    _OPTIONS_WIDGETS = (QtWidgets.QComboBox, QtWidgets.QAbstractSpinBox)

    _INPUT_WIDGETS = _OPTIONS_WIDGETS + (QtWidgets.QAbstractButton,
                                         QtWidgets.QLineEdit, QtWidgets.QTextEdit)

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

        hor = QtWidgets.QHBoxLayout()
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

        dropdown = QtWidgets.QComboBox()
        dropdown.setObjectName('service')

        stack = QtWidgets.QStackedWidget()
        stack.setObjectName('panels')

        for svc_id, text in self._addon.router.get_services():
            dropdown.addItem(text, svc_id)

            svc_layout = QtWidgets.QGridLayout()
            svc_layout.addWidget(Label("Pass the following to %s:" % text),
                                 0, 0, 1, 2)

            svc_widget = QtWidgets.QWidget()
            svc_widget.setLayout(svc_layout)

            stack.addWidget(svc_widget)
        self._svc_count = dropdown.count()

        # one extra widget for displaying a group
        group_layout = QtWidgets.QVBoxLayout()
        group_layout.addWidget(Note())
        group_layout.addStretch()
        group_widget = QtWidgets.QWidget()
        group_widget.setLayout(group_layout)
        stack.addWidget(group_widget)

        dropdown.activated.connect(self._on_service_activated)
        dropdown.currentIndexChanged.connect(self._on_preset_reset)

        hor = QtWidgets.QHBoxLayout()
        hor.addWidget(Label("Generate using"))
        hor.addWidget(dropdown)
        hor.addStretch()

        header = Label("Configure Service")
        header.setFont(self._FONT_HEADER)

        layout = QtWidgets.QVBoxLayout()
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

        dropdown = QtWidgets.QComboBox()
        dropdown.setObjectName('presets_dropdown')
        dropdown.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                               QtWidgets.QSizePolicy.Preferred)
        dropdown.activated.connect(self._on_preset_activated)

        delete = QtWidgets.QPushButton(QtGui.QIcon(f'{ICONS}/editdelete.png'), "")
        delete.setObjectName('presets_delete')
        delete.setIconSize(QtCore.QSize(16, 16))
        delete.setFixedSize(18, 18)
        delete.setFlat(True)
        delete.setToolTip("Remove this service configuration from\n"
                          "the list of remembered services.")
        delete.clicked.connect(self._on_preset_delete)

        save = QtWidgets.QPushButton("Save")
        save.setObjectName('presets_save')
        save.setFixedWidth(save.fontMetrics().width(save.text()) + 20)
        save.setToolTip("Remember the selected service and its input\n"
                        "settings so that you can quickly access it later.")
        save.clicked.connect(self._on_preset_save)

        layout = QtWidgets.QHBoxLayout()
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

        text = QtWidgets.QLineEdit()
        text.keyPressEvent = lambda key_event: (
            self._on_preview()
            if key_event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]
            else QtWidgets.QLineEdit.keyPressEvent(text, key_event)
        )
        text.setObjectName('text')
        text.setPlaceholderText("type a phrase to test...")

        button = QtWidgets.QPushButton("&Preview")
        button.setObjectName('preview')
        button.clicked.connect(self._on_preview)

        hor = QtWidgets.QHBoxLayout()
        hor.addWidget(text)
        hor.addWidget(button)

        header = Label("Preview")
        header.setFont(self._FONT_HEADER)

        layout = QtWidgets.QVBoxLayout()
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

        dropdown = self.findChild(QtWidgets.QComboBox, 'service')

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

        text = self.findChild(QtWidgets.QWidget, 'text')
        try:
            text.setText("")
        except AttributeError:
            text.setPlainText("")

        super(ServiceDialog, self).show(*args, **kwargs)

    def help_menu(self, owner):
        """
        Returns a menu that can be attached to the Help button.
        """

        menu = QtWidgets.QMenu(owner)

        help_svc = QtWidgets.QAction(menu)
        help_svc.triggered \
            .connect(lambda: self._launch_link('services/' + self._svc_id))
        help_svc.setObjectName('help_svc')

        try:
            menu.addAction(
                self.HELP_USAGE_DESC,
                lambda: self._launch_link('usage/' + self.HELP_USAGE_SLUG),
            )
        except AttributeError:
            pass

        menu.addAction(help_svc)
        menu.addAction(
            "Managing service presets",
            lambda: self._launch_link('usage/presets'),
        )
        menu.addAction(
            "Enabling other TTS services",
            lambda: self._launch_link('services'),
        )
        return menu

    def _on_service_activated(self, idx, initial=False, use_options=None):
        """
        Construct the target widget if it has not already been built,
        recall the last-used values for the options, and then switch the
        stack to it.
        """

        combo = self.findChild(QtWidgets.QComboBox, 'service')
        svc_id = combo.itemData(idx)
        stack = self.findChild(QtWidgets.QStackedWidget, 'panels')
        save = self.findChild(QtWidgets.QPushButton, 'presets_save')

        if svc_id.startswith('group:'):  # we handle groups differently
            svc_id = svc_id[6:]
            group = self._addon.config['groups'][svc_id]
            presets = [preset for preset in group['presets'] if preset]

            stack.setCurrentIndex(stack.count() - 1)
            stack.widget(stack.count() - 1).findChild(QtWidgets.QLabel).setText(
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
            options = self._addon.router.get_options(svc_id)

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
        help_svc = self.findChild(QtWidgets.QAction, 'help_svc')
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
                    QtWidgets.QDoubleSpinBox
                    if isinstance(start, float) or isinstance(end, float)
                    else QtWidgets.QSpinBox
                )()

                vinput.setRange(start, end)
                if len(option['values']) > 2:
                    vinput.setSuffix(" " + option['values'][2])
                vinput.valueChanged.connect(self._on_preset_reset)

            else:  # list of tuples
                vinput = QtWidgets.QComboBox()
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

                edit = QtWidgets.QLineEdit()
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

        panel.addWidget(note, row, 0, 1, 3, QtCore.Qt.AlignTop)
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

        assert len(vinputs) == len(options)

        for i, opt in enumerate(options):
            vinput = vinputs[i]

            if isinstance(opt['values'], tuple):
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
        dropdown = self.findChild(QtWidgets.QComboBox, 'presets_dropdown')
        delete = self.findChild(QtWidgets.QPushButton, 'presets_delete')
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

        self.findChild(QtWidgets.QPushButton, 'presets_delete').setDisabled(True)
        self.findChild(QtWidgets.QComboBox, 'presets_dropdown').setCurrentIndex(0)

    def _on_preset_save(self):
        """Saves the current service state back as a preset."""

        svc_id, options = self._get_service_values()
        assert "bad get_service_values() value", \
               not svc_id.startswith('group:') and options
        svc_name = self.findChild(QtWidgets.QComboBox, 'service').currentText()

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

        delete = self.findChild(QtWidgets.QPushButton, 'presets_delete')

        if idx > 0:
            delete.setEnabled(True)
            name = self.findChild(QtWidgets.QComboBox,
                                  'presets_dropdown').currentText()
            try:
                preset = self._addon.config['presets'][name]
                svc_id = preset['service']
            except KeyError:
                self._alerts("%s preset is invalid." % name, self)
                return

            dropdown = self.findChild(QtWidgets.QComboBox, 'service')
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
            del presets[self.findChild(QtWidgets.QComboBox,
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
            fail=lambda exception: self._alerts(
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
                and (not isinstance(widget, QtWidgets.QComboBox) or
                     len(widget) > 1)
        ):
            widget.setDisabled(flag)

        if not flag:
            self.findChild(QtWidgets.QPushButton, 'presets_delete').setEnabled(
                self.findChild(QtWidgets.QComboBox,
                               'presets_dropdown').currentIndex() > 0
            )
            self.findChild(QtWidgets.QPushButton, 'presets_save').setEnabled(
                self.findChild(QtWidgets.QComboBox,
                               'service').currentIndex() < self._svc_count
            )

    def _get_service_values(self):
        """
        Return the service ID and a dict of all the options.
        """

        dropdown = self.findChild(QtWidgets.QComboBox, 'service')
        idx = dropdown.currentIndex()
        svc_id = dropdown.itemData(idx)
        if svc_id.startswith('group:'):
            return svc_id, None

        vinputs = self.findChild(QtWidgets.QStackedWidget, 'panels') \
            .widget(idx).findChildren(self._OPTIONS_WIDGETS)
        options = self._addon.router.get_options(svc_id)

        assert len(options) == len(vinputs)

        return svc_id, {
            options[i]['key']:
                vinputs[i].value()
                if isinstance(vinputs[i], QtWidgets.QAbstractSpinBox)
                else vinputs[i].itemData(vinputs[i].currentIndex())
            for i in range(len(options))
        }

    def _get_service_text(self):
        """
        Return the text box and its phrase.
        """

        text_input = self.findChild(QtWidgets.QWidget, 'text')
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
