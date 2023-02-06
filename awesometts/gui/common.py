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
Common reusable GUI elements

Provides menu action and button classes.

As everything done from the add-on code has to do with AwesomeTTS, these
all carry a speaker icon (if supported by the desktop environment).
"""

import aqt.qt

from ..paths import ICONS

__all__ = ['ICON', 'Action', 'Button',
           'Checkbox', 'Filter', 'HTML', 'Label', 'Note']


ICON_FILE = f'{ICONS}/speaker.png'
ICON = aqt.qt.QIcon(ICON_FILE)


class _Connector:  # used like a mixin, pylint:disable=R0903
    """
    Handles deferring construction of the target class until it's
    needed and then keeping a reference to it as long as its triggering
    GUI element still exists.
    """

    def __init__(self, target, **kwargs):
        """
        Store the target for future use.
        """
        super().__init__(**kwargs)

        self._target = target
        self._instance = None

    def _show(self, *args, **kwargs):
        """
        If the target has not yet been constructed, do so now, and then
        show it.
        """

        if not self._instance:
            self._instance = self._target.constructor(
                *self._target.args,
                **self._target.kwargs
            )

        self._instance.show()


class _QtConnector(_Connector):
    """
    Connector for aqt.qt.Qt.Widgets.
    """
    def __init__(self, target, signal_name, **kwargs):
        """
        Wire up the passed signal.
        """
        super().__init__(target, **kwargs)

        signal = getattr(self, signal_name)
        signal.connect(self._show)


class Action(aqt.qt.QAction, _QtConnector):
    """
    Provides a menu action to show a dialog when triggered.
    """

    NO_SEQUENCE = aqt.qt.QKeySequence()

    __slots__ = [
        '_sequence',  # the key sequence that activates this action
    ]

    def muzzle(self, disable):
        """
        If disable is True, then this shortcut will be temporarily
        disabled (i.e. muzzled), but the action will remain available
        if it would normally be.
        """

        self.setShortcut(self.NO_SEQUENCE if disable else self._sequence)

    def __init__(self, target, text, sequence, parent):
        """
        Initializes the menu action and wires its 'triggered' event.

        If the specified parent is a QMenu, this new action will
        automatically be added to it.
        """
        # PyQt5 uses an odd behaviour for multi-inheritance super() calls,
        # please see: http://pyqt.sourceforge.net/Docs/PyQt5/multiinheritance.html
        # Importantly there is no way to pass self.triggered to _Connector
        # before initialization of the QAction (and I do not know if it is
        # possible # to change order of initialization without changing the
        # order in mro). So one trick is to pass the signal it in a closure
        # so it will be kind of lazy evaluated later and the other option is to
        # pass only signal name and use getattr in _Connector. For now the latter
        # is used (more elegant, but less flexible).
        # Maybe composition would be more predictable here?
        super().__init__(ICON, text, parent, signal_name='triggered', target=target)

        self.setShortcut(sequence)
        self._sequence = sequence

        if isinstance(parent, aqt.qt.QMenu):
            parent.addAction(self)


class AbstractButton:

    @staticmethod
    def tooltip_text(tooltip, sequence=None):
        if sequence:
            return f"{tooltip} ({sequence.toString()})"
        return tooltip


class Button(aqt.qt.QPushButton, _QtConnector, AbstractButton):
    """
    Provides a button to show a dialog when clicked.
    """

    def __init__(self, target, tooltip, sequence, text=None, style=None):
        """
        Initializes the button and wires its 'clicked' event.

        Note that buttons that have text get one set of styling
        different from ones without text.
        """
        super().__init__(ICON, text, signal_name='clicked', target=target)

        if text:
            self.setIconSize(aqt.qt.QSize(15, 15))

        else:
            self.setFixedWidth(20)
            self.setFixedHeight(20)
            self.setFocusPolicy(aqt.qt.Qt.NoFocus)

        self.setShortcut(sequence)
        self.setToolTip(self.tooltip_text(tooltip, sequence))
        self.setDefault(False)
        self.setAutoDefault(False)

        if style:
            self.setStyle(style)


class Checkbox(aqt.qt.QCheckBox):
    """Provides a checkbox with a better constructor."""

    def __init__(self, text=None, object_name=None, parent=None):
        super(Checkbox, self).__init__(text, parent)
        self.setObjectName(object_name)


class Filter(aqt.qt.QObject):
    """
    Once instantiated, serves as an installEventFilter-compatible object
    instance that supports filtering events with a condition.
    """

    def __init__(self, relay, when, *args, **kwargs):
        """
        Make a filter that will "relay" onto a callable "when" a certain
        condition is met (both callables accepting an event argument).
        """

        super(Filter, self).__init__(*args, **kwargs)
        self._relay = relay
        self._when = when

    def eventFilter(self, _, event):  # pylint: disable=invalid-name
        """
       aqt.qt.Qt.eventFilter method. Returns True if the event has been
        handled and should be filtered out.

        The result of and'ing the return values from the `when` and
        `relay` callable is forced to a boolean if it is not already (as
       aqt.qt.Qt.blows up quite spectacularly if it is not).
        """

        return bool(self._when(event) and self._relay(event))


class HTML(aqt.qt.QLabel):
    """Label with HTML enabled."""

    def __init__(self, *args, **kwargs):
        super(HTML, self).__init__(*args, **kwargs)
        self.setTextFormat(aqt.qt.Qt.TextFormat.RichText)


class Label(aqt.qt.QLabel):
    """Label with HTML disabled."""

    def __init__(self, *args, **kwargs):
        super(Label, self).__init__(*args, **kwargs)
        self.setTextFormat(aqt.qt.Qt.TextFormat.PlainText)


class Note(Label):
    """Label with wrapping enabled and HTML disabled."""

    def __init__(self, *args, **kwargs):
        super(Note, self).__init__(*args, **kwargs)
        self.setWordWrap(True)


class Slate(aqt.qt.QHBoxLayout):  # pylint:disable=too-few-public-methods
    """Horizontal panel for dealing with lists of things."""

    def __init__(self, thing, ListViewClass, list_view_args, list_name,
                 *args, **kwargs):
        super(Slate, self).__init__(*args, **kwargs)

        buttons = []
        for tooltip, icon in [("Add New " + thing, 'list-add'),
                              ("Move Selected Up", 'arrow-up'),
                              ("Move Selected Down", 'arrow-down'),
                              ("Remove Selected", 'editdelete')]:
            btn = aqt.qt.QPushButton(aqt.qt.QIcon(f'{ICONS}/{icon}.png'), "")
            btn.setIconSize(aqt.qt.QSize(16, 16))
            btn.setFlat(True)
            btn.setToolTip(tooltip)
            buttons.append(btn)

        list_view_args.append(buttons)
        list_view = ListViewClass(*list_view_args)
        list_view.setObjectName(list_name)
        list_view.setSizePolicy(aqt.qt.QSizePolicy.Policy.MinimumExpanding,
                                aqt.qt.QSizePolicy.Policy.Ignored)

        vert = aqt.qt.QVBoxLayout()
        for btn in buttons:
            vert.addWidget(btn)
        vert.insertStretch(len(buttons) - 1)

        self.addWidget(list_view)
        self.addLayout(vert)
