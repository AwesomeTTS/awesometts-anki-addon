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
import aqt.utils

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
                    (field, field)
                    for field in sorted({field['name']
                                         for field
                                         in self._card_layout.model['flds']})
                ]),

                (1, "Type:", 'type', [
                    ('normal', "Regular field"),
                    ('cloze', "Cloze field: pronounce non-hidden part on front side and everything on back side"),
                    ('cloze-hidden', "Cloze field: hidden part only, on back side only"),
                ]),

                (2, "Language:", 'language', [
                    ('en_US', "American English"),
                    ('fr_FR', "French France"),
                ]),


        ]:
            label = Label(label)
            label.setFont(self._FONT_LABEL)

            widgets[name] = self._ui_control_fields_dropdown(name, options)
            layout.addWidget(label, row, 0)
            layout.addWidget(widgets[name], row, 1)

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

    def set_button_label(self):
        target_name = ""
        if self.front_template_selected:
            target_name = "Front Template"
        elif self.back_template_selected:
            target_name = "Back Template"        
        self.findChild(QtWidgets.QAbstractButton, 'okay').setText("&Insert into " + target_name)

    def get_target_selected(self):
        self.front_template_selected = False
        self.back_template_selected = False
        if self._card_layout.tform.front_button.isChecked():
            self.front_template_selected = True
        if self._card_layout.tform.back_button.isChecked():
            self.back_template_selected = True        

    # Events #################################################################

    def show(self, *args, **kwargs):
        """
        Restore the three dropdown's last known state and then focus the
        field dropdown.
        """

        # did we select the front or back template ?
        self.get_target_selected()

        # set the label of the insert button
        self.set_button_label()

        # if the user selected styling, exit as it doesn't make sense to insert a TTS tag there
        if self.front_template_selected == False and self.back_template_selected == False:
            aqt.utils.showCritical("Please Select Front Template or Back Template", title="AwesomeTTS")
            return

        super(Templater, self).show(*args, **kwargs)


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
        # there's now a single edit area, as of anki 2.1.28
        target = getattr(tform, 'edit_area')
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
            for name in ['field', 'hide']
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
