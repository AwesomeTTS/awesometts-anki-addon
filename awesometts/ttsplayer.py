"""
Register AwesomeTTS voices with the Anki {{tts}} tag.
code modeled after 
https://ankiweb.net/shared/info/391644525 
https://github.com/ankitects/anki-addons/blob/master/code/gtts_player/__init__.py
"""

import os
import sys
from concurrent.futures import Future
from dataclasses import dataclass
from typing import List, cast
import threading

import anki.sound
from anki.lang import compatMap
from anki.sound import AVTag, TTSTag
from aqt import mw
from aqt.taskman import TaskManager
from aqt.sound import OnDoneCallback, av_player
from aqt.tts import TTSProcessPlayer, TTSVoice
import aqt.utils


class AwesomeTTSPlayer(TTSProcessPlayer):
    def __init__(self, taskman: TaskManager, addon) -> None:
        super(TTSProcessPlayer, self).__init__(taskman)
        self._addon = addon

    # this is called the first time Anki tries to play a TTS file
    def get_available_voices(self) -> List[TTSVoice]:

        # register a voice for every possible language AwesomeTTS supports. This avoids forcing the user to do a restart when
        # they configure a new TTS tag
        
        voices = []
        for language in self._addon.language:
            language_name = language.name
            voices.append(TTSVoice(name="AwesomeTTS", lang=language_name))

        return voices  # type: ignore

    # this is called on a background thread, and will not block the UI
    def _play(self, tag: AVTag) -> None:
        self.audio_file_path = None
        self.playback_error = False
        self.playback_error_message = None

        assert isinstance(tag, TTSTag)
        match = self.voice_for_tag(tag)
        assert match
        voice = match.voice
        language = voice.lang
        language_human = self._addon.language[language].lang_name
        
        self._addon.logger.debug(f"playing back for language {language}, tag: {tag} text: {tag.field_text}")

        # is the field blank?
        if not tag.field_text.strip():
            self._addon.logger.debug("field empty, not playing anything")
            return

        text = tag.field_text

        # load awesometts preset
        tts_voices = self._addon.config['tts_voices']
        if language not in tts_voices:
            # language not configured
            self.playback_error = True
            self.playback_error_message = f"Language {language} ({language_human}) not configured for on-the-fly TTS, please add TTS tag in Card template editor to register this language."
            return

        #print(f"* playing back: {self._addon.config['tts_voices'][language]}")

        # this allows us to block until the asynchronous callback is done
        self.done_event = threading.Event()

        is_group = self._addon.config['tts_voices'][language]['is_group']

        # sanitize text
        text = self._addon.strip.from_template(text)

        if not is_group:
            # playback with preset

            awesometts_preset_name = self._addon.config['tts_voices'][language]['preset']
            self._addon.logger.info(f"playing back text with preset: {awesometts_preset_name}, text: {text}.")

            self.awesometts_preset = awesometts_preset_name
            preset = self._addon.config['presets'][awesometts_preset_name]

            self._addon.router(
                svc_id=preset['service'],
                text=text,
                options=preset,
                callbacks=dict(
                    okay=self.audio_file_ready,
                    fail=self.failure,
                )
            )

        else:
            # playback with group

            group_name = self._addon.config['tts_voices'][language]['group']

            self._addon.logger.info(f"playing back text with group: {group_name}, text: {text}.")

            groups = self._addon.config['groups']
            group = groups[group_name]
            if group_name not in groups:
                self.failure(f"group {group_name} not found")
                return

            #print(f"** playing back group {self._addon.config['tts_voices'][language]}")

            self._addon.router.group(
                text=text,
                group=group,
                presets=self._addon.config['presets'],
                callbacks=dict(
                    okay=self.audio_file_ready,
                    fail=self.failure,
                ),
            )    


        # need to wait until we get either a successful callback, or
        self.done_event.wait(timeout=60)

    def failure(self, exception, text):
        # don't do anything, can't popup any dialogs
        # print(f"* failure: {exception}")
        self.playback_error = True
        self.playback_error_message = f"Could not play back {text}: {exception}"
        self._addon.logger.error(self.playback_error_message)
        self.done_event.set()

    def audio_file_ready(self, path):
        self._addon.logger.debug("done playing")
        self.audio_file_path = path
        self.done_event.set()

    # this is called on the main thread, after _play finishes
    def _on_done(self, ret: Future, cb: OnDoneCallback) -> None:
        ret.result()

        # inject file into the top of the audio queue
        if self.audio_file_path != None:
            av_player.insert_file(self.audio_file_path)

        if self.playback_error:
            aqt.utils.showWarning("AwesomeTTS: " + self.playback_error_message)

        # then tell player to advance, which will cause the file to be played
        cb()

    # we don't support stopping while the file is being downloaded
    # (but the user can interrupt playing after it has been downloaded)
    def stop(self):
        pass


def register_tts_player(addon):
    # register our handler
    av_player.players.append(AwesomeTTSPlayer(mw.taskman, addon))
