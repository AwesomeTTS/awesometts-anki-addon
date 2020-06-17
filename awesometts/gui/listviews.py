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
Data list views

This module currently exposes a SubListView for manipulating lists of
substitution rules.
"""

import re
from PyQt5 import QtCore, QtWidgets
from .common import Checkbox, HTML

__all__ = ['GroupListView', 'SubListView']

# all methods might need 'self' in the future, pylint:disable=R0201


class _ListView(QtWidgets.QListView):
    """Abstract list view for use throughout AwesomeTTS."""

    __slots__ = ['_add_btn', '_up_btn', '_down_btn', '_del_btn']

    def __init__(self, buttons, *args, **kwargs):
        super(_ListView, self).__init__(*args, **kwargs)

        self._add_btn, self._up_btn, self._down_btn, self._del_btn = buttons

        self._add_btn.clicked.connect(self._add_rule)
        self._up_btn.clicked.connect(lambda: self._reorder_rules('up'))
        self._down_btn.clicked.connect(lambda: self._reorder_rules('down'))
        self._del_btn.clicked.connect(self._del_rules)

        self.setSelectionMode(self.ExtendedSelection)

    def setModel(self, *args, **kwargs):  # pylint:disable=C0103
        """Passes on model and sets up event handling."""

        super(_ListView, self).setModel(*args, **kwargs)
        self._on_selection()
        self.selectionModel().selectionChanged.connect(self._on_selection)

    def _on_selection(self):
        """Enable/disable buttons as selection changes."""

        indexes = self.selectionModel().selectedIndexes()

        some = len(indexes) > 0
        rows = sorted(index.row() for index in indexes) if some else []
        contiguous = some and rows[-1] == rows[0] + len(rows) - 1
        allow_up = contiguous and rows[0] > 0
        allow_down = contiguous and rows[-1] < self.model().rowCount() - 1

        self._up_btn.setEnabled(allow_up)
        self._down_btn.setEnabled(allow_down)
        self._del_btn.setEnabled(some)

        if self._del_btn.hasFocus():  # avoid refocus going to delete button
            if allow_down:
                self._down_btn.setFocus()
            elif allow_up:
                self._up_btn.setFocus()

    def _add_rule(self):
        """Add a new rule and trigger an edit."""

        model = self.model()
        model.insertRow()
        index = model.index(model.rowCount(self) - 1)

        self.scrollToBottom()
        self.setCurrentIndex(index)
        self.edit(index)

    def _del_rules(self):
        """Remove the selected rule(s)."""

        model = self.model()
        indexes = self.selectionModel().selectedIndexes()
        for row in reversed(sorted(index.row() for index in indexes)):
            model.removeRows(row)

    def _reorder_rules(self, direction):
        """Move the selected rule(s) up or down."""

        indexes = self.selectionModel().selectedIndexes()
        rows = sorted(index.row() for index in indexes)
        if direction == 'up':
            self.model().moveRowsUp(rows[0], len(rows))
        else:
            self.model().moveRowsDown(rows[0], len(rows))
        self._on_selection()


class SubListView(_ListView):
    """List view specifically for substitution lists."""

    def __init__(self, sul_compiler, *args, **kwargs):
        super(SubListView, self).__init__(*args, **kwargs)
        self.setItemDelegate(_SubRuleDelegate(sul_compiler))

    def setModel(self, model, *args, **kwargs):  # pylint:disable=C0103
        """Configures model."""

        super(SubListView, self).setModel(_SubListModel(model),
                                          *args, **kwargs)


class GroupListView(_ListView):
    """List view specifically for lists of presets."""

    __slots__ = ['_presets']

    def __init__(self, presets, *args, **kwargs):
        super(GroupListView, self).__init__(*args, **kwargs)

        self.setItemDelegate(_GroupPresetDelegate(presets))
        self._presets = presets

    def setModel(self, model, *args, **kwargs):  # pylint:disable=C0103
        """Configures model."""

        super(GroupListView, self).setModel(
            _GroupListModel(self._presets, model),
            *args, **kwargs
        )


class _Delegate(QtWidgets.QItemDelegate):
    """Abstract delegate view for use throughout AwesomeTTS."""

    def sizeHint(self,            # pylint:disable=invalid-name
                 option, index):  # pylint:disable=unused-argument
        """Always return the same size."""
        return self.sizeHint.SIZE

    sizeHint.SIZE = QtCore.QSize(-1, 40)


class _SubRuleDelegate(_Delegate):
    """Item view specifically for a substitution rule."""

    __slots__ = ['_sul_compiler']

    def __init__(self, sul_compiler, *args, **kwargs):
        super(_SubRuleDelegate, self).__init__(*args, **kwargs)
        self._sul_compiler = sul_compiler

    def createEditor(self, parent,    # pylint:disable=C0103
                     option, index):  # pylint:disable=W0613
        """Return a panel to change rule values."""

        edits = QtWidgets.QHBoxLayout()
        edits.addWidget(QtWidgets.QLineEdit())
        edits.addWidget(HTML("&nbsp;<strong>&rarr;</strong>&nbsp;"))
        edits.addWidget(QtWidgets.QLineEdit())

        checkboxes = QtWidgets.QHBoxLayout()
        for label in ["regex", "case-insensitive", "unicode"]:
            checkboxes.addStretch()
            checkboxes.addWidget(Checkbox(label))
        checkboxes.addStretch()

        layout = QtWidgets.QVBoxLayout()
        layout.addStretch()
        layout.addLayout(edits)
        layout.addLayout(checkboxes)
        layout.addStretch()

        panel = QtWidgets.QWidget(parent)
        panel.setObjectName('editor')
        panel.setAutoFillBackground(True)
        panel.setFocusPolicy(QtCore.Qt.StrongFocus)
        panel.setLayout(layout)

        for layout in [edits, checkboxes, layout]:
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

        for widget in [panel] + panel.findChildren(QtWidgets.QWidget):
            widget.setContentsMargins(0, 0, 0, 0)

        return panel

    def setEditorData(self, editor, index):  # pylint:disable=C0103
        """Populate controls and focus the first edit box."""

        rule = index.data(QtCore.Qt.EditRole)

        edits = editor.findChildren(QtWidgets.QLineEdit)
        edits[0].setText(rule['input'])
        edits[1].setText(rule['replace'])

        checkboxes = editor.findChildren(Checkbox)
        checkboxes[0].setChecked(rule['regex'])
        checkboxes[1].setChecked(rule['ignore_case'])
        checkboxes[2].setChecked(rule['unicode'])

        QtCore.QTimer.singleShot(0, edits[0].setFocus)

    def setModelData(self, editor, model, index):  # pylint:disable=C0103
        """Update the underlying model after edit."""

        edits = editor.findChildren(QtWidgets.QLineEdit)
        checkboxes = editor.findChildren(Checkbox)
        obj = {'input': edits[0].text(), 'compiled': None,
               'replace': edits[1].text(), 'regex': checkboxes[0].isChecked(),
               'ignore_case': checkboxes[1].isChecked(),
               'unicode': checkboxes[2].isChecked()}

        input_len = len(obj['input'])
        if input_len > 2 and obj['input'].startswith('/'):
            input_ends = obj['input'].endswith
            if input_ends('/'):
                obj['input'] = obj['input'][1:-1]
                obj['regex'] = True
            elif input_len > 3:
                if input_ends('/i'):
                    obj['input'] = obj['input'][1:-2]
                    obj['regex'] = True
                    obj['ignore_case'] = True
                elif input_ends('/g'):
                    obj['input'] = obj['input'][1:-2]
                    obj['regex'] = True
                elif input_len > 4 and (input_ends('/ig') or
                                        input_ends('/gi')):
                    obj['input'] = obj['input'][1:-3]
                    obj['regex'] = True
                    obj['ignore_case'] = True

        try:
            obj['compiled'] = self._sul_compiler(obj)
        except Exception:  # sre_constants.error, pylint:disable=W0703
            pass

        if obj['compiled'] and obj['regex']:
            groups = obj['compiled'].groups
            for group in self.setModelData.RE_SLASH.findall(obj['replace']):
                group = int(group)
                if not group or group > groups:
                    obj['bad_replace'] = True
                    break

        model.setData(index, obj)

    setModelData.RE_SLASH = re.compile(r'\\(\d+)')


class _GroupPresetDelegate(_Delegate):
    """Item view specifically for a group preset."""

    __slots__ = ['_presets']

    def __init__(self, presets, *args, **kwargs):
        super(_GroupPresetDelegate, self).__init__(*args, **kwargs)
        self._presets = presets

    def createEditor(self, parent,    # pylint:disable=C0103
                     option, index):  # pylint:disable=W0613
        """Return a panel to change selected preset."""

        dropdown = QtWidgets.QComboBox()
        dropdown.addItem("(select preset)")
        dropdown.addItems(self._presets)

        hor = QtWidgets.QHBoxLayout()
        hor.addWidget(dropdown)

        panel = QtWidgets.QWidget(parent)
        panel.setObjectName('editor')
        panel.setAutoFillBackground(True)
        panel.setFocusPolicy(QtCore.Qt.StrongFocus)
        panel.setLayout(hor)
        return panel

    def setEditorData(self, editor, index):  # pylint:disable=C0103
        """Changes the preset in the dropdown."""

        dropdown = editor.findChild(QtWidgets.QComboBox)
        value = index.data(QtCore.Qt.EditRole)
        dropdown.setCurrentIndex(dropdown.findText(value) if value else 0)

        QtCore.QTimer.singleShot(0, dropdown.setFocus)

    def setModelData(self, editor, model, index):  # pylint:disable=C0103
        """Update the underlying model after edit."""

        dropdown = editor.findChild(QtWidgets.QComboBox)
        model.setData(
            index,
            dropdown.currentText() if dropdown.currentIndex() > 0 else ""
        )


class _ListModel(QtCore.QAbstractListModel):  # pylint:disable=R0904
    """Abstract class for list models."""

    __slots__ = ['raw_data']

    def flags(self, index):  # pylint:disable=unused-argument
        """Always return same item flags."""
        return self.flags.LIST_ITEM

    flags.LIST_ITEM = (QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable |
                       QtCore.Qt.ItemIsEnabled)

    def rowCount(self,          # pylint:disable=invalid-name
                 parent=None):  # pylint:disable=unused-argument
        """Return row count based on my raw data."""
        return len(self.raw_data)

    def __init__(self, raw_data, *args, **kwargs):
        super(_ListModel, self).__init__(*args, **kwargs)
        self.raw_data = raw_data

    def moveRowsDown(self, row, count):  # pylint:disable=C0103
        """Moves the given count of records at the given row down."""

        parent = QtCore.QModelIndex()
        self.beginMoveRows(parent, row, row + count - 1,
                           parent, row + count + 1)
        self.raw_data = (self.raw_data[0:row] +
                         self.raw_data[row + count:row + count + 1] +
                         self.raw_data[row:row + count] +
                         self.raw_data[row + count + 1:])
        self.endMoveRows()
        return True

    def moveRowsUp(self, row, count):  # pylint:disable=C0103
        """Moves the given count of records at the given row up."""

        parent = QtCore.QModelIndex()
        self.beginMoveRows(parent, row, row + count - 1, parent, row - 1)
        self.raw_data = (self.raw_data[0:row - 1] +
                         self.raw_data[row:row + count] +
                         self.raw_data[row - 1:row] +
                         self.raw_data[row + count:])
        self.endMoveRows()
        return True

    def removeRows(self, row, count=1, parent=None):  # pylint:disable=C0103
        """Removes the given count of records at the given row."""

        self.beginRemoveRows(parent or QtCore.QModelIndex(),
                             row, row + count - 1)
        self.raw_data = self.raw_data[0:row] + self.raw_data[row + count:]
        self.endRemoveRows()
        return True

    def setData(self, index, value,        # pylint:disable=C0103
                role=QtCore.Qt.EditRole):  # pylint:disable=W0613
        """Update the new value into the raw list."""

        self.raw_data[index.row()] = value
        return True


class _SubListModel(_ListModel):  # pylint:disable=R0904
    """Provides glue to/from the underlying substitution list."""

    def __init__(self, *args, **kwargs):
        super(_SubListModel, self).__init__(*args, **kwargs)
        self.raw_data = [dict(obj) for obj in self.raw_data]  # deep copy

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Return display or edit data for the indexed rule."""

        if role == QtCore.Qt.DisplayRole:
            rule = self.raw_data[index.row()]
            if not rule['input']:
                return "empty match pattern"
            elif not rule['compiled']:
                return "invalid match pattern: " + rule['input']
            elif 'bad_replace' in rule:
                return "bad replacement string: " + rule['replace']

            text = '/%s/%s' % (rule['input'],
                               'i' if rule['ignore_case'] else '') \
                   if rule['regex'] else '"%s"' % rule['input']
            action = ('replace it with "%s"' % rule['replace']
                      if rule['replace'] else "remove it")
            attr = ", ".join([
                "regex pattern" if rule['regex'] else "plain text",
                "case-insensitive" if rule['ignore_case'] else "case matters",
                "unicode enabled" if rule['unicode'] else "unicode disabled",
            ])
            return "match " + text + " and " + action + "\n(" + attr + ")"

        elif role == QtCore.Qt.EditRole:
            return self.raw_data[index.row()]

    def insertRow(self, row=None, parent=None):  # pylint:disable=C0103
        """Inserts a new row at the given position (default end)."""

        if not row:
            row = len(self.raw_data)  # defaults to end

        self.beginInsertRows(parent or QtCore.QModelIndex(), row, row)
        self.raw_data.insert(row, {'input': '', 'compiled': None,
                                   'replace': '', 'regex': False,
                                   'ignore_case': True, 'unicode': True})
        self.endInsertRows()
        return True


class _GroupListModel(_ListModel):  # pylint:disable=R0904
    """Provides glue to/from the underlying preset list."""

    __slots__ = ['_presets']

    def __init__(self, presets, *args, **kwargs):
        super(_GroupListModel, self).__init__(*args, **kwargs)
        self._presets = presets

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Return display or edit data for the indexed preset."""

        preset = self.raw_data[index.row()]
        if role == QtCore.Qt.DisplayRole:
            return ("(not selected)" if not preset
                    else preset if preset in self._presets
                    else preset + " [deleted]")
        elif role == QtCore.Qt.EditRole:
            return preset

    def insertRow(self, row=None, parent=None):  # pylint:disable=C0103
        """Inserts a new row at the given position (default end)."""

        if not row:
            row = len(self.raw_data)  # defaults to end

        self.beginInsertRows(parent or QtCore.QModelIndex(), row, row)
        self.raw_data.insert(row, "")
        self.endInsertRows()
        return True
