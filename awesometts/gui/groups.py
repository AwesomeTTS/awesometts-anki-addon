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

"""Groups management dialog"""

from PyQt5 import QtCore, QtWidgets, QtGui

from ..paths import ICONS
from .base import Dialog
from .common import Label, Note, Slate
from .listviews import GroupListView

__all__ = ['Groups']


class Groups(Dialog):
    """Provides a dialog for editing groups of presets."""

    __slots__ = [
        '_ask',            # dialog interface for asking for user input
        '_current_group',  # current group name
        '_groups',         # deep copy from config['groups']
    ]

    def __init__(self, ask, *args, **kwargs):
        super(Groups, self).__init__(title="Manage Preset Groups",
                                     *args, **kwargs)
        self._ask = ask
        self._current_group = None
        self._groups = None  # set in show()

    # UI Construction ########################################################

    def _ui(self):
        """
        Returns a vertical layout with a banner and controls to update
        the groups.
        """

        layout = super(Groups, self)._ui()

        groups = QtWidgets.QComboBox()
        groups.setObjectName('groups')
        groups.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                             QtWidgets.QSizePolicy.Preferred)
        groups.activated.connect(self._on_group_activated)

        # TODO: icons do not work with 2.1
        delete = QtWidgets.QPushButton(QtGui.QIcon(f'{ICONS}/editdelete.png'), "")
        delete.setObjectName('delete')
        delete.setIconSize(QtCore.QSize(16, 16))
        delete.setFixedSize(18, 18)
        delete.setFlat(True)
        delete.clicked.connect(self._on_group_delete)

        add = QtWidgets.QPushButton(QtGui.QIcon(f'{ICONS}/list-add.png'), "")
        add.setObjectName('add')
        add.setIconSize(QtCore.QSize(16, 16))
        add.setFixedSize(18, 18)
        add.setFlat(True)
        add.clicked.connect(self._on_group_add)

        hor = QtWidgets.QHBoxLayout()
        hor.addWidget(groups)
        hor.addWidget(delete)
        hor.addWidget(add)
        hor.addStretch()

        vert = QtWidgets.QVBoxLayout()
        vert.setObjectName('child')

        layout.addLayout(hor)
        layout.addSpacing(self._SPACING)
        layout.addLayout(vert)
        layout.addWidget(self._ui_buttons())
        return layout

    # Events #################################################################

    def show(self, *args, **kwargs):
        """Restores state on opening the dialog."""

        self._groups = {
            name: {'mode': group['mode'], 'presets': group['presets'][:]}
            for name, group in self._addon.config['groups'].items()
        }
        self._on_refresh()

        super(Groups, self).show(*args, **kwargs)

    def help_request(self):
        """Launch browser to the documentation for groups."""

        self._launch_link('usage/groups')

    def _on_group_activated(self, idx):
        """Show the correct panel for the selected group."""

        self._pull_presets()
        delete = self.findChild(QtWidgets.QPushButton, 'delete')
        vert = self.findChild(QtWidgets.QLayout, 'child')

        while vert.count():
            vert.itemAt(0).widget().setParent(None)

        if idx > 0:
            delete.setEnabled(True)

            name = self.findChild(QtWidgets.QComboBox, 'groups').currentText()
            self._current_group = name
            group = self._groups[name]

            randomize = QtWidgets.QRadioButton("randomized")
            randomize.setChecked(group['mode'] == 'random')
            randomize.clicked.connect(lambda: group.update({'mode': 'random'}))

            in_order = QtWidgets.QRadioButton("in-order")
            in_order.setChecked(group['mode'] == 'ordered')
            in_order.clicked.connect(lambda: group.update({'mode': 'ordered'}))

            hor = QtWidgets.QHBoxLayout()
            hor.addWidget(Label("Mode:"))
            hor.addWidget(randomize)
            hor.addWidget(in_order)
            hor.addStretch()

            inner = QtWidgets.QVBoxLayout()
            inner.addLayout(hor)
            inner.addLayout(Slate(
                "Preset",
                GroupListView,
                [sorted(
                    self._addon.config['presets'].keys(),
                    key=lambda preset: preset.lower(),
                )],
                'presets',
            ))

            slate = QtWidgets.QWidget()
            slate.setLayout(inner)

            vert.addWidget(slate)

            self.findChild(QtWidgets.QListView,
                           'presets').setModel(group['presets'])

        else:
            delete.setEnabled(False)

            self._current_group = None

            header = Label("About Preset Groups")
            header.setFont(self._FONT_HEADER)

            vert.addWidget(header)
            vert.addWidget(Note("Preset groups can operate in two modes: "
                                "randomized or in-order."))
            vert.addWidget(Note("The randomized mode can be helpful if you "
                                "want to hear playback in a variety of preset "
                                "voices while you study."))
            vert.addWidget(Note("The in-order mode can be used if you prefer "
                                "playback from a particular preset, but want "
                                "to fallback to another preset if your first "
                                "choice does not have audio for your input "
                                "phrase."))
            vert.addWidget(Label(""), 1)

    def _on_group_delete(self):
        """Delete the selected group."""

        del self._groups[self.findChild(QtWidgets.QComboBox,
                                        'groups').currentText()]
        self._on_refresh()

    def _on_group_add(self):
        """Prompt the user for a name and add a new group."""

        default = "New Group"
        i = 1

        while default in self._groups:
            i += 1
            default = "New Group #%d" % i

        name, okay = self._ask(
            title="Create a New Group",
            prompt="Please enter a name for your new group.",
            default=default,
            parent=self,
        )

        name = okay and name.strip()
        if name:
            self._groups[name] = {'mode': 'random', 'presets': []}
            self._on_refresh(select=name)

    def _on_refresh(self, select=None):
        """Repopulate the group dropdown and initialize panel."""

        groups = self.findChild(QtWidgets.QComboBox, 'groups')
        groups.clear()
        groups.addItem("View/Edit Group...")

        if self._groups:
            groups.setEnabled(True)
            groups.insertSeparator(1)
            groups.addItems(sorted(self._groups.keys(),
                                   key=lambda name: name.upper()))
            if select:
                idx = groups.findText(select)
                groups.setCurrentIndex(idx)
                self._on_group_activated(idx)
            else:
                self._on_group_activated(0)

        else:
            groups.setEnabled(False)
            self._on_group_activated(0)

    def accept(self):
        """Saves groups back to user configuration."""

        self._pull_presets()
        self._addon.config['groups'] = {
            name: {'mode': group['mode'], 'presets': group['presets'][:]}
            for name, group in self._groups.items()
        }
        self._current_group = None
        super(Groups, self).accept()

    def reject(self):
        """Unset the current group."""

        self._current_group = None
        super(Groups, self).reject()

    def _pull_presets(self):
        """Update current group's presets."""

        name = self._current_group
        if not name or name not in self._groups:
            return

        list_view = self.findChild(QtWidgets.QListView, 'presets')
        for editor in list_view.findChildren(QtWidgets.QWidget, 'editor'):
            list_view.commitData(editor)  # if an editor is open, save it

        self._groups[name]['presets'] = list_view.model().raw_data
