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

    HELP_USAGE_SLUG = 'On-the-fly-TTS'

    FIELD_TYPE_REGULAR = "regular"
    FIELD_TYPE_CLOZE = "cloze"
    FIELD_TYPE_CLOZE_HIDDEN = "cloze_hidden"

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
        layout.addWidget(Note("Configure TTS tag settings"))
        layout.addStretch()
        layout.addLayout(self._ui_control_fields())
        layout.addStretch()
        layout.addWidget(Note("This feature will use AwesomeTTS on Anki desktop, and will fallback to other voices (based on the selected language) " +
        "where AwesomeTTS is not available."))
        layout.addStretch()
        layout.addWidget(self._ui_buttons())

        return layout

    def _ui_control_fields(self):
        """
        Returns a dropdown box to let the user select a source field.
        """

        widgets = {}
        layout = QtWidgets.QGridLayout()

        full_language_list = [(x.name, x.lang_name) for x in self._addon.language]
        # sort by human name
        full_language_list.sort(key=lambda x:x[1])

        for row, label, name, options in [
                (0, "Field:", 'field', [
                    (field, field)
                    for field in sorted({field['name']
                                         for field
                                         in self._card_layout.model['flds']})
                ]),

                (1, "Type:", 'type', [
                    (Templater.FIELD_TYPE_REGULAR, "Regular field"),
                    (Templater.FIELD_TYPE_CLOZE, "Cloze field: speak non-hidden parts of front, speak everything on back"),
                    (Templater.FIELD_TYPE_CLOZE_HIDDEN, "Cloze field: hidden part only, on back side only"),
                ]),

                (2, "Language:", 'language', full_language_list),


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

        settings = self._get_all()

        is_group = settings['is_group']
        preset_name = settings['preset_name']
        group_name = settings['group_name']
        # get language
        language = settings['language']
        language_enum = self._addon.language[language]        

        #print(settings)

        if not is_group and preset_name == None:
            aqt.utils.showCritical("You must select a service preset", self)
            return

        # prepare the config update diff, which will be applied later
        # need to clone the data, otherwise setting an attribute will update the cache
        tts_voices = dict(self._addon.config['tts_voices'])
        tts_voices[language] = {'is_group': is_group, 'preset': preset_name, 'group': group_name}

        tform = self._card_layout.tform
        # there's now a single edit area, as of anki 2.1.28
        target = getattr(tform, 'edit_area')

        field_syntax = settings['field']
        field_type = settings['type']
        if field_type == Templater.FIELD_TYPE_CLOZE:
            field_syntax = f"cloze:{settings['field']}"
        elif field_type == Templater.FIELD_TYPE_CLOZE_HIDDEN:
            field_syntax = f"cloze-only:{settings['field']}"

        language = settings['language']
        tag_syntax = f"tts {language} voices=AwesomeTTS:{field_syntax}"

        target.setPlainText('\n'.join([target.toPlainText(), '{{' + tag_syntax + '}}'] ))

        if is_group:
            aqt.utils.showInfo(f"You have now associated the {language_enum.lang_name} language with the [{group_name}] group. To change this association, "+ 
        "delete the tag and add it again.", self)
        else:
            aqt.utils.showInfo(f"You have now associated the {language_enum.lang_name} language with the [{preset_name}] preset. To change this association, "+ 
        "delete the tag and add it again.", self)

        self._addon.config['tts_voices'] = tts_voices

        super(Templater, self).accept()

    def _get_all(self):
        """
        Adds support to remember the three dropdowns and cloze state (if any),
        in addition to the service options handled by the superclass.
        """

        combos = {
            name: widget.itemData(widget.currentIndex())
            for name in ['field', 'type', 'language']
            for widget in [self.findChild(QtWidgets.QComboBox, name)]
        }

        presets = self.findChild(QtWidgets.QComboBox, 'presets_dropdown')
        
        #service
        services = self.findChild(QtWidgets.QComboBox, 'service')
        service_index = services.currentIndex()
        service_id = services.itemData(service_index)

        # did the user select a group ?
        if service_id.startswith('group:'):  # we handle groups differently
            group_name = service_id[6:]
            combos['group_name'] = group_name
            combos['preset_name'] = None
            combos['is_group'] = True
        else:
            combos['is_group'] = False
            combos['group_name'] = None
            if presets.currentIndex() == 0:
                combos['preset_name'] = None
            else:
                preset_name = presets.currentText()
                combos['preset_name'] = preset_name

        return combos
