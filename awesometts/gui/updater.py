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
Updater dialog
"""

from time import time
from PyQt4 import QtCore, QtGui

from .base import Dialog
from .common import Note

__all__ = ['Updater']

_NO_SCROLLBAR = QtCore.Qt.ScrollBarAlwaysOff


class Updater(Dialog):
    """
    Produces a dialog suitable for displaying to the user when an update
    is available, whether the user did a manual update check or if it
    was triggered at start-up.
    """

    __slots__ = [
        '_version',    # latest version string for the add-on
        '_info',       # dict with additional information about the update
        '_is_manual',  # True if the update was triggered manually
        '_inhibited',  # contains reason as a string if updates cannot occur
    ]

    def __init__(self, version, info, is_manual=False, *args, **kwargs):
        """
        Builds the dialog with the given version and info. If the check
        is flagged as a manual one, the various deferment options are
        hidden.
        """

        self._version = version
        self._info = info
        self._is_manual = is_manual
        self._inhibited = None
        self._set_inhibited(kwargs.get('addon'))

        super(Updater, self).__init__(
            title="AwesomeTTS v%s Available" % version,
            *args, **kwargs
        )

    def _set_inhibited(self, addon):
        """
        Sets a human-readable reason why automatic updates are not
        possible based on things present in the environment, if needed.
        """

        if not self._info['auto']:
            self._inhibited = "This update cannot be applied automatically."

        elif addon.paths.is_link:
            self._inhibited = "Because you are using AwesomeTTS via a " \
                "symlink, you should not update the add-on directly from " \
                "the Anki user interface. However, if you are using the " \
                "symlink to point to a clone of the code repository, you " \
                "can use the git tool to pull in upstream updates."

    # UI Construction ########################################################

    def _ui(self):
        """
        Returns the superclass's banner follow by our update information
        and action buttons.
        """

        layout = super(Updater, self)._ui()

        if self._info['intro']:
            layout.addWidget(Note(self._info['intro']))

        if self._info['notes']:
            list_icon = QtGui.QIcon(':/icons/rating.png')

            list_widget = QtGui.QListWidget()
            for note in self._info['notes']:
                list_widget.addItem(QtGui.QListWidgetItem(list_icon, note))
            list_widget.setHorizontalScrollBarPolicy(_NO_SCROLLBAR)
            list_widget.setWordWrap(True)
            layout.addWidget(list_widget)

        if self._info['synopsis']:
            layout.addWidget(Note(self._info['synopsis']))

        if self._inhibited:
            inhibited = Note(self._inhibited)
            inhibited.setFont(self._FONT_INFO)

            layout.addSpacing(self._SPACING)
            layout.addWidget(inhibited)

        layout.addSpacing(self._SPACING)
        layout.addWidget(self._ui_buttons())

        return layout

    def _ui_buttons(self):
        """
        Returns a horizontal row of action buttons. Overrides the one
        from the superclass.
        """

        buttons = QtGui.QDialogButtonBox()

        now_button = QtGui.QPushButton(
            QtGui.QIcon(':/icons/emblem-favorite.png'),
            "Update Now",
        )
        now_button.setAutoDefault(False)
        now_button.setDefault(False)
        now_button.clicked.connect(self._update)

        if self._inhibited:
            now_button.setEnabled(False)

        if self._is_manual:
            later_button = QtGui.QPushButton(
                QtGui.QIcon(':/icons/fileclose.png'),
                "Don't Update",
            )
            later_button.clicked.connect(self.reject)

        else:
            menu = QtGui.QMenu()
            menu.addAction("Remind Me Next Session", self._remind_session)
            menu.addAction("Remind Me Tomorrow", self._remind_tomorrow)
            menu.addAction("Remind Me in a Week", self._remind_week)
            menu.addAction("Skip v%s" % self._version, self._skip_version)
            menu.addAction("Stop Checking for Updates", self._disable)

            later_button = QtGui.QPushButton(
                QtGui.QIcon(':/icons/clock16.png'),
                "Not Now",
            )
            later_button.setMenu(menu)

        later_button.setAutoDefault(False)
        later_button.setDefault(False)

        buttons.addButton(now_button, QtGui.QDialogButtonBox.YesRole)
        buttons.addButton(later_button, QtGui.QDialogButtonBox.NoRole)

        return buttons

    # Events #################################################################

    def _update(self):
        """
        Updates the add-on via the Anki interface.
        """

        self.accept()

        if isinstance(self.parentWidget(), QtGui.QDialog):
            self.parentWidget().reject()

        dlb = self._addon.downloader

        try:
            class OurGetAddons(dlb.base):  # see base, pylint:disable=R0903
                """
                Creates a sort of jerry-rigged version of Anki's add-on
                downloader dialog (usually GetAddons, but configurable)
                such that an accept() call on it will download
                AwesomeTTS specifically.
                """

                def __init__(self):
                    dlb.superbase.__init__(  # skip, pylint:disable=W0233
                        self,
                        *dlb.args,
                        **dlb.kwargs
                    )

                    for name, value in dlb.attrs.items():
                        setattr(self, name, value)

            addon_dialog = OurGetAddons()
            addon_dialog.accept()  # see base, pylint:disable=E1101

        except Exception as exception:  # catch all, pylint:disable=W0703
            dlb.fail(
                "Unable to automatically update AwesomeTTS (%s); you may "
                "want to restart Anki and then update the add-on manually "
                "from the Tools menu." %
                (exception.message or format(exception))
            )

    def _remind_session(self):
        """
        Closes the dialog; add-on will automatically check next session.
        """

        self.reject()

    def _remind_tomorrow(self):
        """
        Bumps the postpone time by 24 hours before closing dialog.
        """

        self._addon.config['updates_postpone'] = time() + 86400
        self.reject()

    def _remind_week(self):
        """
        Bumps the postpone time by 7 days before closing dialog.
        """

        self._addon.config['updates_postpone'] = time() + 604800
        self.reject()

    def _skip_version(self):
        """
        Marks current version as ignored before closing dialog.
        """

        self._addon.config['updates_ignore'] = self._version
        self.reject()

    def _disable(self):
        """
        Disables the automatic updates flag before closing dialog.
        """

        self._addon.config['updates_enabled'] = False
        self.reject()
