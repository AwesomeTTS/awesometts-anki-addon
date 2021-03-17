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
File generation dialogs
"""

from re import compile as re
from PyQt5 import QtCore, QtWidgets

from .base import Dialog, ServiceDialog
from .common import Checkbox, Label, Note

__all__ = ['BrowserGenerator', 'EditorGenerator']


class BrowserGenerator(ServiceDialog):
    """
    Provides a dialog for generating many media files to multiple cards
    from the card browser.
    """

    HELP_USAGE_DESC = "Adding audio to multiple notes"

    HELP_USAGE_SLUG = 'Batch-Generation'

    _RE_WHITESPACE = re(r'\s+')

    __slots__ = [
        '_browser',  # reference to the current Anki browser window
        '_notes',    # list of Note objects selected when window opened
        '_process',  # state during processing; see accept() method below
    ]

    def __init__(self, browser, *args, **kwargs):
        """
        Sets our title.
        """

        self._browser = browser
        self._notes = None  # set in show()
        self._process = None  # set in accept()

        super(BrowserGenerator, self).__init__(
            title="Add TTS Audio to Selected Notes",
            *args, **kwargs
        )

    # UI Construction ########################################################

    def _ui_control(self):
        """
        Returns the superclass's text and preview buttons, adding our
        inputs to control the mass generation process, and then the base
        class's cancel/OK buttons.
        """

        header = Label("Fields and Handling")
        header.setFont(self._FONT_HEADER)

        intro = Note()  # see show() for where the text is initialized
        intro.setObjectName('intro')

        layout = super(BrowserGenerator, self)._ui_control()
        layout.addWidget(header)
        layout.addWidget(intro)
        layout.addStretch()
        layout.addLayout(self._ui_control_fields())
        layout.addWidget(self._ui_control_handling())
        layout.addStretch()
        layout.addWidget(self._ui_buttons())

        return layout

    def _ui_control_fields(self):
        """
        Returns a grid layout with the source and destination fields.

        Note that populating the field dropdowns is deferred to the
        show() event handler because the available fields might change
        from call to call.
        """

        source_label = Label("Source Field:")
        source_label.setFont(self._FONT_LABEL)

        source_dropdown = QtWidgets.QComboBox()
        source_dropdown.setObjectName('source')

        dest_label = Label("Destination Field:")
        dest_label.setFont(self._FONT_LABEL)

        dest_dropdown = QtWidgets.QComboBox()
        dest_dropdown.setObjectName('dest')

        layout = QtWidgets.QGridLayout()
        layout.addWidget(source_label, 0, 0)
        layout.addWidget(source_dropdown, 0, 1)
        layout.addWidget(dest_label, 1, 0)
        layout.addWidget(dest_dropdown, 1, 1)

        return layout

    def _ui_control_handling(self):
        """
        Return the append/overwrite radio buttons and behavior checkbox.
        """

        append = QtWidgets.QRadioButton(
            "&Append [sound:xxx] Tag onto Destination Field"
        )
        append.setObjectName('append')
        append.toggled.connect(self._on_handling_toggled)

        overwrite = QtWidgets.QRadioButton(
            "Over&write the Destination Field w/ Media Filename"
        )
        overwrite.setObjectName('overwrite')
        overwrite.toggled.connect(self._on_handling_toggled)

        behavior = Checkbox(object_name='behavior')
        behavior.stateChanged.connect(
            lambda status: self._on_behavior_changed(),
        )

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(append)
        layout.addWidget(overwrite)
        layout.addSpacing(self._SPACING)
        layout.addWidget(behavior)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        return widget

    def _ui_buttons(self):
        """
        Adjust title of the OK button.
        """

        buttons = super(BrowserGenerator, self)._ui_buttons()
        buttons.findChild(QtWidgets.QAbstractButton, 'okay').setText("&Generate")

        return buttons

    # Events #################################################################

    def show(self, *args, **kwargs):
        """
        Populate the source and destination dropdowns, recall the
        handling and behavior inputs, and focus the source dropdown.

        Note that the fields are dumped and repopulated each time,
        because the list of fields might change between displays of the
        window.
        """

        self._notes = [
            self._browser.mw.col.getNote(note_id)
            for note_id in self._browser.selectedNotes()
        ]

        self.findChild(Note, 'intro').setText(
            '%d note%s selected. Click "Help" for usage hints.' %
            (len(self._notes), "s" if len(self._notes) != 1 else "")
        )

        fields = sorted({
            field
            for note in self._notes
            for field in note.keys()
        })

        config = self._addon.config

        source = self.findChild(QtWidgets.QComboBox, 'source')
        source.clear()
        for field in fields:
            source.addItem(field, field)
        source.setCurrentIndex(
            max(source.findData(config['last_mass_source']), 0)
        )

        dest = self.findChild(QtWidgets.QComboBox, 'dest')
        dest.clear()
        for field in fields:
            dest.addItem(field, field)
        dest.setCurrentIndex(
            max(dest.findData(config['last_mass_dest']), 0)
        )

        self.findChild(
            QtWidgets.QRadioButton,
            'append' if config['last_mass_append'] else 'overwrite',
        ).setChecked(True)

        self.findChild(Checkbox, 'behavior') \
            .setChecked(config['last_mass_behavior'])

        super(BrowserGenerator, self).show(*args, **kwargs)

        source.setFocus()

    def accept(self):
        """
        Check to make sure that we have at least one note, pull the
        service options, and kick off the processing.
        """

        now = self._get_all()
        source = now['last_mass_source']
        dest = now['last_mass_dest']
        append = now['last_mass_append']
        behavior = now['last_mass_behavior']

        eligible_notes = [
            note
            for note in self._notes
            if source in note and dest in note
        ]

        if not eligible_notes:
            self._alerts(
                f"Of the {len(self._notes)} notes selected in the browser, "
                f"none have both '{source}' and '{dest}' fields."
                if len(self._notes) > 1
                else f"The selected note does not have both "
                     f"'{source}' and '{dest}' fields.",
                self,
            )
            return

        self._disable_inputs()

        svc_id = now['last_service']
        options = (None if svc_id.startswith('group:') else
                   now['last_options'][now['last_service']])

        self._process = {
            'all': now,
            'aborted': False,
            'progress': _Progress(
                maximum=len(eligible_notes),
                on_cancel=self._accept_abort,
                title="Generating MP3s",
                addon=self._addon,
                parent=self,
            ),
            'service': {
                'id': svc_id,
                'options': options,
            },
            'fields': {
                'source': source,
                'dest': dest,
            },
            'handling': {
                'append': append,
                'behavior': behavior,
            },
            'queue': eligible_notes,
            'counts': {
                'total': len(self._notes),
                'elig': len(eligible_notes),
                'skip': len(self._notes) - len(eligible_notes),
                'done': 0,  # all notes processed
                'okay': 0,  # calls which resulted in a successful MP3
                'fail': 0,  # calls which resulted in an exception
            },
            'failednotes': [],
            'exceptions': {},
            'throttling': {
                'calls': {},  # unthrottled download calls made per service
                'sleep': self._addon.config['throttle_sleep'],
                'threshold': self._addon.config['throttle_threshold'],
            },
        }

        self._browser.mw.checkpoint("AwesomeTTS Batch Update")
        self._process['progress'].show()

        self._accept_next()

    def _accept_abort(self):
        """
        Flags that the user has requested that processing stops.
        """

        self._process['aborted'] = True

    def _accept_next(self):
        """
        Pop the next note off the queue, if not throttled, and process.
        """

        self._accept_update()

        proc = self._process
        throttling = proc['throttling']

        if proc['aborted'] or not proc['queue']:
            self._accept_done()
            return

        if throttling['calls'] and \
           max(throttling['calls'].values()) >= throttling['threshold']:
            # at least one service needs a break

            timer = QtCore.QTimer()
            throttling['timer'] = timer
            throttling['countdown'] = throttling['sleep']

            timer.timeout.connect(self._accept_throttled)
            timer.setInterval(1000)
            timer.start()
            return

        note = proc['queue'].pop(0)
        phrase = note[proc['fields']['source']]
        phrase = self._addon.strip.from_note(phrase)
        self._accept_update(phrase)

        def done():
            """Count the processed note."""

            proc['counts']['done'] += 1

        def okay(path):
            """Count the success and update the note."""

            filename = self._browser.mw.col.media.addFile(path)
            dest = proc['fields']['dest']
            note[dest] = self._accept_next_output(note[dest], filename)
            proc['counts']['okay'] += 1
            note.flush()

        def fail(exception, text="Not available by _accept_next.fail"):
            """Count the failure and the unique message."""

            proc['counts']['fail'] += 1
            proc['failednotes'].append(text)

            message = str(exception)
            if isinstance(message, str):
                message = self._RE_WHITESPACE.sub(' ', message).strip()

            try:
                proc['exceptions'][message] += 1
            except KeyError:
                proc['exceptions'][message] = 1

        def miss(svc_id, count):
            """Count the cache miss."""

            try:
                throttling['calls'][svc_id] += count
            except KeyError:
                throttling['calls'][svc_id] = count

        callbacks = dict(
            done=done, okay=okay, fail=fail, miss=miss,

            # The call to _accept_next() is done via a single-shot QTimer for
            # a few reasons: keep the UI responsive, avoid a "maximum
            # recursion depth exceeded" exception if we hit a string of cached
            # files, and allow time to respond to a "cancel".
            then=lambda: QtCore.QTimer.singleShot(0, self._accept_next),
        )

        svc_id = proc['service']['id']
        want_human = (self._addon.config['filenames_human'] or '{{text}}' if
                      self._addon.config['filenames'] == 'human' else False)

        if svc_id.startswith('group:'):
            config = self._addon.config
            self._addon.router.group(text=phrase,
                                     group=config['groups'][svc_id[6:]],
                                     presets=config['presets'],
                                     callbacks=callbacks,
                                     want_human=want_human,
                                     note=note)
        else:
            self._addon.router(svc_id=svc_id,
                               text=phrase,
                               options=proc['service']['options'],
                               callbacks=callbacks,
                               want_human=want_human,
                               note=note)

    def _accept_next_output(self, old_value, filename):
        """
        Given a note's old value and our current handling options,
        returns a new note value using the passed filename.
        """

        proc = self._process

        if proc['handling']['append']:
            if proc['handling']['behavior']:
                return self._addon.strip.sounds.univ(old_value).strip() + \
                    ' [sound:%s]' % filename
            elif filename in old_value:
                return old_value
            else:
                return old_value + ' [sound:%s]' % filename

        else:
            if proc['handling']['behavior']:
                return '[sound:%s]' % filename
            else:
                return filename

    def _accept_throttled(self):
        """
        Called for every "timeout" of the timer during a throttling.
        """

        proc = self._process

        if proc['aborted']:
            proc['throttling']['timer'].stop()
            self._accept_done()
            return

        proc['throttling']['countdown'] -= 1
        self._accept_update()

        if proc['throttling']['countdown'] <= 0:
            proc['throttling']['timer'].stop()
            del proc['throttling']['countdown']
            del proc['throttling']['timer']
            proc['throttling']['calls'] = {}
            self._accept_next()

    def _accept_update(self, detail=None):
        """
        Update the progress bar and message.
        """

        proc = self._process

        proc['progress'].update(
            label="finished %d of %d%s\n"
                  "%d successful, %d failed\n"
                  "\n"
                  "%s" % (
                      proc['counts']['done'],
                      proc['counts']['elig'],

                      " (%d skipped)" % proc['counts']['skip']
                      if proc['counts']['skip']
                      else "",

                      proc['counts']['okay'],
                      proc['counts']['fail'],

                      "sleeping for %d second%s" % (
                          proc['throttling']['countdown'],
                          "s"
                          if proc['throttling']['countdown'] != 1
                          else ""
                      )
                      if (
                          proc['throttling'] and
                          'countdown' in proc['throttling']
                      )
                      else " "
                  ),
            value=proc['counts']['done'],
            detail=detail,
        )

    def _accept_done(self):
        """
        Display statistics and close out the dialog.
        """

        self._browser.model.reset()

        proc = self._process
        proc['progress'].accept()

        messages = [
            "The %d note%s you selected %s been processed. " % (
                proc['counts']['total'],
                "s" if proc['counts']['total'] != 1 else "",
                "have" if proc['counts']['total'] != 1 else "has",
            )
            if proc['counts']['done'] == proc['counts']['total']
            else "%d of the %d note%s you selected %s processed. " % (
                proc['counts']['done'],
                proc['counts']['total'],
                "s" if proc['counts']['total'] != 1 else "",
                "were" if proc['counts']['done'] != 1 else "was",
            ),

            "%d note%s skipped for not having both the source and "
            "destination fields. Of those remaining, " % (
                proc['counts']['skip'],
                "s were" if proc['counts']['skip'] != 1
                else " was",
            )
            if proc['counts']['skip']
            else "During processing, "
        ]

        if proc['counts']['fail']:
            if proc['counts']['okay']:
                messages.append(
                    "%d note%s successfully updated, but "
                    "%d note%s failed while processing." % (
                        proc['counts']['okay'],
                        "s were" if proc['counts']['okay'] != 1
                        else " was",
                        proc['counts']['fail'],
                        "s" if proc['counts']['fail'] != 1
                        else "",
                    )
                )
            else:
                messages.append("no notes were successfully updated.")

            messages.append("\n\n")

            if len(proc['exceptions']) == 1:
                messages.append("The following problem was encountered:")
                messages += [
                    "\n%s (%d time%s)" %
                    (message, count, "s" if count != 1 else "")
                    for message, count
                    in proc['exceptions'].items()
                ]
            else:
                messages.append("The following problems were encountered:")
                messages += [
                    "\n- %s (%d time%s)" %
                    (message, count, "s" if count != 1 else "")
                    for message, count
                    in proc['exceptions'].items()
                ]
            messages.append("\n\nThe following note(s) have failed:\n")
            messages.append("".join(f"'{note}', " for note in proc['failednotes']))

        else:
            messages.append("there were no errors.")

        if proc['aborted']:
            messages.append("\n\n")
            messages.append(
                "You aborted processing. If you want to rollback the changes "
                "to the notes that were already processed, use the Undo "
                "AwesomeTTS Batch Update option from the Edit menu."
            )

        self._addon.config.update(proc['all'])
        self._disable_inputs(False)
        self._notes = None
        self._process = None

        super(BrowserGenerator, self).accept()

        # this alert is done by way of a singleShot() callback to avoid random
        # crashes on Mac OS X, which happen <5% of the time if called directly
        QtCore.QTimer.singleShot(
            0,
            lambda: self._alerts("".join(messages), self._browser),
        )

    def _get_all(self):
        """
        Adds support for fields and behavior.
        """

        source, dest, append, behavior = self._get_field_values()

        # TODO: could be rewritten with {**, **} syntax
        return dict(
            list(super(BrowserGenerator, self)._get_all().items()) +
            [
                ('last_mass_append', append),
                ('last_mass_behavior', behavior),
                ('last_mass_dest', dest),
                ('last_mass_source', source),
            ]
        )

    def _get_field_values(self):
        """
        Returns the user's source and destination fields, append state,
        and handling mode.
        """

        return (
            self.findChild(QtWidgets.QComboBox, 'source').currentText(),
            self.findChild(QtWidgets.QComboBox, 'dest').currentText(),
            self.findChild(QtWidgets.QRadioButton, 'append').isChecked(),
            self.findChild(Checkbox, 'behavior').isChecked(),
        )

    def _on_handling_toggled(self):
        """
        Change the text on the behavior checkbox based on the append
        or overwrite behavior.
        """

        append = self.findChild(QtWidgets.QRadioButton, 'append')
        behavior = self.findChild(Checkbox, 'behavior')
        behavior.setText(
            "Remove Existing [sound:xxx] Tag(s)" if append.isChecked()
            else "Wrap the Filename in [sound:xxx] Tag"
        )
        behavior.setChecked(True)

    def _on_behavior_changed(self):
        """
        Display a warning about bare filenames if user selects the
        override option and disables wrapping the field with a [sound]
        tag.
        """

        if self.isVisible():
            append = self.findChild(QtWidgets.QRadioButton, 'append')
            behavior = self.findChild(Checkbox, 'behavior')

            if not (append.isChecked() or behavior.isChecked()):
                self._alerts(
                    'Please note that if you use bare filenames, the "Check '
                    'Media" feature in Anki will not detect those audio '
                    "files as in-use, even if you insert the field into your "
                    "templates.",
                    self,
                )


class EditorGenerator(ServiceDialog):
    """
    Provides a dialog for adding single media files from the editors.
    """

    HELP_USAGE_DESC = "Adding audio to a single note"

    HELP_USAGE_SLUG = 'editor'

    __slots__ = [
        '_editor',  # reference to one of the editors in the Anki GUI
    ]

    def __init__(self, editor, *args, **kwargs):
        """
        Sets our title.
        """

        self._editor = editor
        super(EditorGenerator, self).__init__(
            title="Add TTS Audio to Note",
            *args, **kwargs
        )
    # UI Construction ########################################################

    def _ui_control(self):
        """
        Replaces the superclass's version of this with a version that
        returns a "Preview and Record" header, larger text input area,
        and preview button on its own line.
        """

        header = Label("Preview and Record")
        header.setFont(self._FONT_HEADER)

        text = QtWidgets.QTextEdit()
        text.setAcceptRichText(False)
        text.setObjectName('text')
        text.setTabChangesFocus(True)
        text.keyPressEvent = lambda key_event: \
            self.accept() if (
                key_event.modifiers() & QtCore.Qt.ControlModifier and
                key_event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]
            ) \
            else QtWidgets.QTextEdit.keyPressEvent(text, key_event)

        button = QtWidgets.QPushButton("&Preview")
        button.setObjectName('preview')
        button.clicked.connect(self._on_preview)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(header)
        layout.addWidget(Note("This will be inserted as a [sound] tag and "
                              "synchronized with your collection."))
        layout.addWidget(text)
        layout.addWidget(button)
        layout.addWidget(self._ui_buttons())

        return layout

    def _ui_buttons(self):
        """
        Adjust title of the OK button.
        """

        buttons = super(EditorGenerator, self)._ui_buttons()
        buttons.findChild(QtWidgets.QAbstractButton, 'okay').setText("&Record")

        return buttons

    # Events #################################################################

    def show(self, *args, **kwargs):
        """
        Focus the text area after displaying the dialog.
        """

        super(EditorGenerator, self).show(*args, **kwargs)

        QtCore.QTimer.singleShot(0, self._populate_input_field)

    def _populate_input_field(self):
        text = self.findChild(QtWidgets.QTextEdit, 'text')
        text.setFocus()

        editor = self._editor
        web = editor.web
        from_note = self._addon.strip.from_note
        from_unknown = self._addon.strip.from_unknown
        app = QtWidgets.QApplication

        def try_clipboard(subtype):
            """Fetch from given system clipboard."""
            return from_unknown(app.clipboard().text(subtype)[0])

        def js_callback(val):
            self.callback_message = val
            self.javascript_is_ready = True

        def exec_javascript():
            self.javascript_is_ready = False

            web.page().runJavaScript(
                    # for jQuery, this needs to be html() instead of text() as
                    # $('<div>hi<br>there</div>').text() yields "hithere"
                    # whereas if we have the original HTML, we can convert the
                    # line break tag into whitespace during input sanitization
                    'getCurrentField().fieldHTML', js_callback)

            while not self.javascript_is_ready:
                app.instance().processEvents()

            return self.callback_message

        for origin in [
                lambda: from_note(web.selectedText()),
                lambda: from_note(exec_javascript()),
                lambda: try_clipboard('html'),
                lambda: try_clipboard('text'),
        ]:
            try:
                prefill = origin()
            except BaseException:  # e.g. old Qt version, system errors
                continue

            if prefill:
                text.setPlainText(prefill)
                text.selectAll()
                break

    def accept(self):
        """
        Given the user's options and text, calls the service to make a
        recording. If successful, the options are remembered and the MP3
        inserted into the field.
        """

        now = self._get_all()
        text_input, text_value = self._get_service_text()

        svc_id = now['last_service']
        text_value = self._addon.strip.from_user(text_value)
        callbacks = dict(
            done=lambda: self._disable_inputs(False),
            okay=lambda path: (
                self._addon.config.update(now),
                super(EditorGenerator, self).accept(),
                self._editor.addMedia(path),
            ),
            fail=lambda exception, text_value: (
                self._alerts("Cannot record the input phrase with these "
                             "settings.\n\n%s" % exception, self),
                text_input.setFocus(),
            ),
        )

        want_human = (self._addon.config['filenames_human'] or '{{text}}' if
                      self._addon.config['filenames'] == 'human' else False)

        self._disable_inputs()
        if svc_id.startswith('group:'):
            config = self._addon.config
            self._addon.router.group(text=text_value,
                                     group=config['groups'][svc_id[6:]],
                                     presets=config['presets'],
                                     callbacks=callbacks,
                                     want_human=want_human,
                                     note=self._editor.note)
        else:
            options = now['last_options'][now['last_service']]
            self._addon.router(svc_id=svc_id,
                               text=text_value,
                               options=options,
                               callbacks=callbacks,
                               want_human=want_human,
                               note=self._editor.note)


class _Progress(Dialog):
    """
    Provides a dialog that can be displayed while processing.
    """

    __slots__ = [
        '_maximum'    # the value we are counting up to
        '_on_cancel'  # callable to invoke if the user hits cancel
    ]

    def __init__(self, maximum, on_cancel, *args, **kwargs):
        """
        Configures our bar's maximum and registers a cancel callback.
        """

        self._maximum = maximum
        self._on_cancel = on_cancel
        super(_Progress, self).__init__(*args, **kwargs)

    # UI Construction ########################################################

    def _ui(self):
        """
        Builds the interface with a status label and progress bar.
        """

        self.setMinimumWidth(500)

        status = Note("Please wait...")
        status.setAlignment(QtCore.Qt.AlignCenter)
        status.setObjectName('status')

        progress_bar = QtWidgets.QProgressBar()
        progress_bar.setMaximum(self._maximum)
        progress_bar.setObjectName('bar')

        detail = Note("")
        detail.setAlignment(QtCore.Qt.AlignCenter)
        detail.setFixedHeight(100)
        detail.setFont(self._FONT_INFO)
        detail.setObjectName('detail')
        detail.setScaledContents(True)

        layout = super(_Progress, self)._ui()
        layout.addStretch()
        layout.addWidget(status)
        layout.addStretch()
        layout.addWidget(progress_bar)
        layout.addStretch()
        layout.addWidget(detail)
        layout.addStretch()
        layout.addWidget(self._ui_buttons())

        return layout

    def _ui_buttons(self):
        """
        Overrides the default behavior to only have a cancel button.
        """

        buttons = QtWidgets.QDialogButtonBox()
        buttons.setObjectName('buttons')
        buttons.rejected.connect(self.reject)
        buttons.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel)
        buttons.button(QtWidgets.QDialogButtonBox.Cancel).setAutoDefault(False)

        return buttons

    # Events #################################################################

    def reject(self):
        """
        On cancel, disable the button and call our registered callback.
        """

        self.findChild(QtWidgets.QDialogButtonBox, 'buttons').setDisabled(True)
        self._on_cancel()

    def update(self, label, value, detail=None):
        """
        Update the status text and bar.
        """

        self.findChild(Note, 'status').setText(label)
        self.findChild(QtWidgets.QProgressBar, 'bar').setValue(value)
        if detail:
            self.findChild(Note, 'detail').setText(detail)
