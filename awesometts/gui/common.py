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

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt

from ..paths import ICONS

__all__ = ['ICON', 'key_event_combo', 'key_combo_desc', 'Action', 'Button',
           'Checkbox', 'Filter', 'HTML', 'Label', 'Note', 'HTMLButton']


ICON_FILE = f'{ICONS}/speaker.png'
ICON = QtGui.QIcon(ICON_FILE)


def key_event_combo(event):
    """
    Given a key event, returns an integer representing the combination
    of keys that was pressed or released.

    Certain keys are blacklisted (see BLACKLIST) and key_event_combo()
    will return None if it sees these keys in the primary key() slot for
    an event. When used by themselves or exclusively with modifiers,
    these keys cause various problems: gibberish strings returned from
    QKeySequence#toString() and in menus, inability to capture the
    keystroke because the window manager does not forward it to Qt,
    ambiguous shortcuts where order would matter (e.g. Ctrl + Alt would
    produce a different numerical value than Alt + Ctrl, because the
    key codes for Alt and Ctrl are different from the modifier flag
    codes for Alt and Ctrl), and clashes with input navigation.
    """

    key = event.key()
    if key < 32 or key in key_event_combo.BLACKLIST:
        return None

    modifiers = event.modifiers()
    return key + sum(flag
                     for flag in key_event_combo.MOD_FLAGS
                     if modifiers & flag)


key_event_combo.MOD_FLAGS = [Qt.AltModifier, Qt.ControlModifier,
                             Qt.MetaModifier, Qt.ShiftModifier]

key_event_combo.BLACKLIST = [
    Qt.Key_Alt, Qt.Key_AltGr, Qt.Key_Backspace, Qt.Key_Backtab,
    Qt.Key_CapsLock, Qt.Key_Control, Qt.Key_Dead_Abovedot,
    Qt.Key_Dead_Abovering, Qt.Key_Dead_Acute, Qt.Key_Dead_Belowdot,
    Qt.Key_Dead_Breve, Qt.Key_Dead_Caron, Qt.Key_Dead_Cedilla,
    Qt.Key_Dead_Circumflex, Qt.Key_Dead_Diaeresis, Qt.Key_Dead_Doubleacute,
    Qt.Key_Dead_Grave, Qt.Key_Dead_Hook, Qt.Key_Dead_Horn, Qt.Key_Dead_Iota,
    Qt.Key_Dead_Macron, Qt.Key_Dead_Ogonek, Qt.Key_Dead_Semivoiced_Sound,
    Qt.Key_Dead_Tilde, Qt.Key_Dead_Voiced_Sound, Qt.Key_Delete, Qt.Key_Down,
    Qt.Key_End, Qt.Key_Enter, Qt.Key_Equal, Qt.Key_Escape, Qt.Key_Home,
    Qt.Key_Insert, Qt.Key_Left, Qt.Key_Menu, Qt.Key_Meta, Qt.Key_Minus,
    Qt.Key_Mode_switch, Qt.Key_NumLock, Qt.Key_PageDown, Qt.Key_PageUp,
    Qt.Key_Plus, Qt.Key_Return, Qt.Key_Right, Qt.Key_ScrollLock, Qt.Key_Shift,
    Qt.Key_Space, Qt.Key_Tab, Qt.Key_Underscore, Qt.Key_Up,
]


def key_combo_desc(combo):
    """
    Given an key combination as returned by key_event_combo, returns a
    human-readable description.
    """

    return QtGui.QKeySequence(combo).toString(QtGui.QKeySequence.NativeText) \
        if combo else "unassigned"


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
    Connector for Qt Widgets.
    """
    def __init__(self, target, signal_name, **kwargs):
        """
        Wire up the passed signal.
        """
        super().__init__(target, **kwargs)

        signal = getattr(self, signal_name)
        signal.connect(self._show)


class _HTMLConnector(_Connector):

    @staticmethod
    def generate_link_id(owner, base_id='btn'):

        new_id = base_id

        while True:
            if new_id in owner._links:
                new_id += 'X'
            else:
                return new_id

    def __init__(self, target, owner, link_id=None, **kwargs):
        """
        Create a link for WebView-Python bridge,
        placing it on owner's list of links.
        """
        super().__init__(target, **kwargs)

        self.link_id = link_id or self.generate_link_id(owner)

        # access to private, though that is the way proposed in Anki 2.1 docs:
        # https://apps.ankiweb.net/docs/addons21.html#hooks
        owner._links[self.link_id] = self._show


class Action(QtWidgets.QAction, _QtConnector):
    """
    Provides a menu action to show a dialog when triggered.
    """

    NO_SEQUENCE = QtGui.QKeySequence()

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

        if isinstance(parent, QtWidgets.QMenu):
            parent.addAction(self)


class AbstractButton:

    @staticmethod
    def tooltip_text(tooltip, sequence=None):
        if sequence:
            return f"{tooltip} ({key_combo_desc(sequence)})"
        return tooltip


class Button(QtWidgets.QPushButton, _QtConnector, AbstractButton):
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
            self.setIconSize(QtCore.QSize(15, 15))

        else:
            self.setFixedWidth(20)
            self.setFixedHeight(20)
            self.setFocusPolicy(Qt.NoFocus)

        self.setShortcut(sequence)
        self.setToolTip(self.tooltip_text(tooltip, sequence))

        if style:
            self.setStyle(style)


class HTMLButton(AbstractButton, _HTMLConnector):

    def __init__(self, buttons, owner, target, tooltip, sequence, text=None, link_id=None):
        """
        Initializes the button and wires its 'clicked' event.

        Note that HTMLButton does not connect key-sequence as a shortcut
        to target action, as such an option is not exposed in Anki API.
        """

        _HTMLConnector.__init__(self, target, owner, link_id)
        self.buttons = buttons

        # access to private, though that is the way proposed in Anki 2.1 docs:
        # https://apps.ankiweb.net/docs/addons21.html#hooks
        self.html = owner._addButton(
            ICON_FILE,
            self.link_id,
            self.tooltip_text(tooltip, sequence),
            label=text
        )

        self.buttons.append(self.html)


class Checkbox(QtWidgets.QCheckBox):
    """Provides a checkbox with a better constructor."""

    def __init__(self, text=None, object_name=None, parent=None):
        super(Checkbox, self).__init__(text, parent)
        self.setObjectName(object_name)


class Filter(QtCore.QObject):
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
        Qt eventFilter method. Returns True if the event has been
        handled and should be filtered out.

        The result of and'ing the return values from the `when` and
        `relay` callable is forced to a boolean if it is not already (as
        Qt blows up quite spectacularly if it is not).
        """

        return bool(self._when(event) and self._relay(event))


class HTML(QtWidgets.QLabel):
    """Label with HTML enabled."""

    def __init__(self, *args, **kwargs):
        super(HTML, self).__init__(*args, **kwargs)
        self.setTextFormat(QtCore.Qt.RichText)


class Label(QtWidgets.QLabel):
    """Label with HTML disabled."""

    def __init__(self, *args, **kwargs):
        super(Label, self).__init__(*args, **kwargs)
        self.setTextFormat(QtCore.Qt.PlainText)


class Note(Label):
    """Label with wrapping enabled and HTML disabled."""

    def __init__(self, *args, **kwargs):
        super(Note, self).__init__(*args, **kwargs)
        self.setWordWrap(True)


class Slate(QtWidgets.QHBoxLayout):  # pylint:disable=too-few-public-methods
    """Horizontal panel for dealing with lists of things."""

    def __init__(self, thing, ListViewClass, list_view_args, list_name,
                 *args, **kwargs):
        super(Slate, self).__init__(*args, **kwargs)

        buttons = []
        for tooltip, icon in [("Add New " + thing, 'list-add'),
                              ("Move Selected Up", 'arrow-up'),
                              ("Move Selected Down", 'arrow-down'),
                              ("Remove Selected", 'editdelete')]:
            btn = QtWidgets.QPushButton(QtGui.QIcon(f'{ICONS}/{icon}.png'), "")
            btn.setIconSize(QtCore.QSize(16, 16))
            btn.setFlat(True)
            btn.setToolTip(tooltip)
            buttons.append(btn)

        list_view_args.append(buttons)
        list_view = ListViewClass(*list_view_args)
        list_view.setObjectName(list_name)
        list_view.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                QtWidgets.QSizePolicy.Ignored)

        vert = QtWidgets.QVBoxLayout()
        for btn in buttons:
            vert.addWidget(btn)
        vert.insertStretch(len(buttons) - 1)

        self.addWidget(list_view)
        self.addLayout(vert)
