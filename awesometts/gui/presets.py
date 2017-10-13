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

"""Presets management dialog"""

from PyQt5 import QtWidgets

from .base import ServiceDialog
from .common import Label, Note

__all__ = ['Presets']


class Presets(ServiceDialog):
    """Provides a dialog for editing presets."""

    __slots__ = []

    def __init__(self, *args, **kwargs):
        super(Presets, self).__init__(title="Manage Service Presets",
                                      *args, **kwargs)

    # UI Construction ########################################################

    def _ui_control(self):
        """Add explanation of the preset functionality."""

        header = Label("About Service Presets")
        header.setFont(self._FONT_HEADER)

        layout = super(Presets, self)._ui_control()
        layout.addWidget(header)
        layout.addWidget(Note(
            'Once saved, your service option presets can be easily recalled '
            'in most AwesomeTTS dialog windows and/or used for on-the-fly '
            'playback with <tts preset="..."> ... </tts> template tags.'
        ))
        layout.addWidget(Note(
            "Selecting text and then side-clicking in some Anki panels (e.g. "
            "review mode, card layout editor, note editor fields) will also "
            "allow playback of the selected text using any of your presets."
        ))
        layout.addSpacing(self._SPACING)
        layout.addStretch()
        layout.addWidget(self._ui_buttons())

        return layout

    def _ui_buttons(self):
        """Removes the "Cancel" button."""

        buttons = super(Presets, self)._ui_buttons()
        for btn in buttons.buttons():
            if buttons.buttonRole(btn) == QtWidgets.QDialogButtonBox.RejectRole:
                buttons.removeButton(btn)
        return buttons

    # Events #################################################################

    def accept(self):
        """Remember the user's options if they hit "Okay"."""

        self._addon.config.update(self._get_all())
        super(Presets, self).accept()
