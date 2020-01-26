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
Template generation dialog
"""

from PyQt5 import QtWidgets

from .base import ServiceDialog
from .common import Checkbox, Label, Note

__all__ = ['Templater']

# all methods might need 'self' in the future, pylint:disable=R0201


class Templater(ServiceDialog):
    """
    Provides a dialog for building an on-the-fly TTS tag in Anki's card
    layout editor.
    """

    HELP_USAGE_DESC = "Inserting on-the-fly playback tags into templates"

    HELP_USAGE_SLUG = 'on-the-fly'

    __slots__ = [
        '_card_layout',  # reference to the card layout window
        '_is_cloze',     # True if the model attached
    ]

    def __init__(self, card_layout, *args, **kwargs):
        """
        Sets our title.
        """

        from anki.consts import MODEL_CLOZE
        self._card_layout = card_layout
        self._is_cloze = card_layout.model['type'] == MODEL_CLOZE

        super(Templater, self).__init__(
            title="Add On-the-Fly TTS Tag to Template",
            *args, **kwargs
        )

    # UI Construction ########################################################

    def _ui_control(self):
        """
        Returns the superclass's text and preview buttons, adding our
        field input selector, then the base class's cancel/OK buttons.
        """

        header = Label("Tag Options")
        header.setFont(self._FONT_HEADER)

        layout = super(Templater, self)._ui_control()
        layout.addWidget(header)
        layout.addWidget(Note("AwesomeTTS will speak <tts> tags as you "
                              "review."))
        layout.addStretch()
        layout.addLayout(self._ui_control_fields())
        layout.addStretch()
        layout.addWidget(Note("This feature requires desktop Anki w/ "
                              "AwesomeTTS installed; it will not work on "
                              "mobile apps or AnkiWeb."))
        layout.addStretch()
        layout.addWidget(self._ui_buttons())

        return layout

    def _ui_control_fields(self):
        """
        Returns a dropdown box to let the user select a source field.
        """

        widgets = {}
        layout = QtWidgets.QGridLayout()

        for row, label, name, options in [
                (0, "Field:", 'field', [
                    ('', "customize the tag's content"),
                ] + [
                    (field, field)
                    for field in sorted({field['name']
                                         for field
                                         in self._card_layout.model['flds']})
                ]),

                (1, "Visibility:", 'hide', [
                    ('normal', "insert the tag as-is"),
                    ('inline', "hide just this tag w/ inline CSS"),
                    ('global', "add rule to hide any TTS tag for note type"),
                ]),

                (2, "Add to:", 'target', [
                    ('front', "Front Template"),
                    ('back', "Back Template"),
                ]),

                # row 3 is used below if self._is_cloze is True
        ]:
            label = Label(label)
            label.setFont(self._FONT_LABEL)

            widgets[name] = self._ui_control_fields_dropdown(name, options)
            layout.addWidget(label, row, 0)
            layout.addWidget(widgets[name], row, 1)

        if self._is_cloze:
            cloze = Checkbox(object_name='cloze')
            cloze.setMinimumHeight(25)

            warning = Label("Remember 'cloze:' for any cloze fields.")
            warning.setMinimumHeight(25)

            layout.addWidget(cloze, 3, 1)
            layout.addWidget(warning, 3, 1)

            widgets['field'].setCurrentIndex(-1)
            widgets['field'].currentIndexChanged.connect(lambda index: (
                cloze.setVisible(index),
                cloze.setText(
                    "%s uses cloze" %
                    (widgets['field'].itemData(index) if index else "this")
                ),
                warning.setVisible(not index),
            ))

        return layout

    def _ui_control_fields_dropdown(self, name, options):
        """
        Returns a dropdown with the given list of options.
        """

        dropdown = QtWidgets.QComboBox()
        dropdown.setObjectName(name)
        for value, label in options:
            dropdown.addItem(label, value)

        return dropdown

    def _ui_buttons(self):
        """
        Adjust title of the OK button.
        """

        buttons = super(Templater, self)._ui_buttons()
        buttons.findChild(QtWidgets.QAbstractButton, 'okay').setText("&Insert")

        return buttons

    # Events #################################################################

    def show(self, *args, **kwargs):
        """
        Restore the three dropdown's last known state and then focus the
        field dropdown.
        """

        super(Templater, self).show(*args, **kwargs)

        for name in ['hide', 'target', 'field']:
            dropdown = self.findChild(QtWidgets.QComboBox, name)
            dropdown.setCurrentIndex(max(
                dropdown.findData(self._addon.config['templater_' + name]), 0
            ))

        if self._is_cloze:
            self.findChild(Checkbox, 'cloze') \
                .setChecked(self._addon.config['templater_cloze'])

        dropdown.setFocus()  # abuses fact that 'field' is last in the loop

    def accept(self):
        """
        Given the user's selected service and options, assembles a TTS
        tag and then remembers the options.
        """

        try:
            from html import escape
        except ImportError:
            from cgi import escape

        now = self._get_all()
        tform = self._card_layout.tform
        target = getattr(tform, now['templater_target'])
        presets = self.findChild(QtWidgets.QComboBox, 'presets_dropdown')

        last_service = now['last_service']
        attrs = ([('group', last_service[6:])]
                 if last_service.startswith('group:') else
                 [('preset', presets.currentText())]
                 if presets.currentIndex() > 0 else
                 [('service', last_service)] +
                 sorted(now['last_options'][last_service].items()))
        if now['templater_hide'] == 'inline':
            attrs.append(('style', 'display: none'))
        attrs = ' '.join('%s="%s"' % (key, escape(str(value), quote=True))
                         for key, value in attrs)

        cloze = now.get('templater_cloze')
        field = now['templater_field']
        html = ('' if not field
                else '{{cloze:%s}}' % field if cloze
                else '{{%s}}' % field)

        target.setPlainText('\n'.join([target.toPlainText(),
                                       '<tts %s>%s</tts>' % (attrs, html)]))

        if now['templater_hide'] == 'global':
            existing_css = tform.css.toPlainText()
            extra_css = 'tts { display: none }'
            if existing_css.find(extra_css) < 0:
                tform.css.setPlainText('\n'.join([
                    existing_css,
                    extra_css,
                ]))

        self._addon.config.update(now)
        super(Templater, self).accept()

    def _get_all(self):
        """
        Adds support to remember the three dropdowns and cloze state (if any),
        in addition to the service options handled by the superclass.
        """

        combos = {
            name: widget.itemData(widget.currentIndex())
            for name in ['field', 'hide', 'target']
            for widget in [self.findChild(QtWidgets.QComboBox, name)]
        }

        return dict(
            list(super(Templater, self)._get_all().items()) +
            [('templater_' + name, value) for name, value in combos.items()] +
            (
                [(
                    'templater_cloze',
                    self.findChild(Checkbox, 'cloze').isChecked(),
                )]
                if self._is_cloze and combos['field']
                else []
            )
        )
