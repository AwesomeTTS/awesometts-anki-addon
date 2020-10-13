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

def tts_preset_name_valid(preset_name: str) -> bool:
    if "," in preset_name:
        return (False, f"preset name [{preset_name}] cannot contain any commas (,)")
    return (True, None)

# we subclass the default voice object to store the gtts language code
@dataclass
class AwesomeTTSVoice(TTSVoice):
    atts_preset: str


class AwesomeTTSPlayer(TTSProcessPlayer):
    def __init__(self, taskman: TaskManager, addon) -> None:
        super(TTSProcessPlayer, self).__init__(taskman)
        self._addon = addon

    # this is called the first time Anki tries to play a TTS file
    def get_available_voices(self) -> List[TTSVoice]:
        print("* get_available_voices")
        # can we list awesome TTS presets here ?
        config = self._addon.config
        config_presets = config['presets']
        preset_keys = config_presets.keys()
        voices = []
        for preset_name in preset_keys:
            (is_valid, reason) = tts_preset_name_valid(preset_name)
            if is_valid:
                std_code="en_US"
                voices.append(AwesomeTTSVoice(name=preset_name, lang=std_code, atts_preset=preset_name))

        return voices  # type: ignore

    # this is called on a background thread, and will not block the UI
    def _play(self, tag: AVTag) -> None:
        self.audio_file_path = None

        assert isinstance(tag, TTSTag)
        match = self.voice_for_tag(tag)
        assert match
        voice = cast(AwesomeTTSVoice, match.voice)

        # is the field blank?
        if not tag.field_text.strip():
            return

        text = tag.field_text

        # load preset
        awesometts_preset = voice.atts_preset
        self.awesometts_preset = awesometts_preset
        config = self._addon.config
        config_presets = config['presets']
        preset = config_presets[awesometts_preset]

        self.done_event = threading.Event()

        self._addon.router(
            svc_id=preset['service'],
            text=text,
            options=preset,
            callbacks=dict(
                okay=self.audio_file_ready,
                fail=self.failure,
            )
        )

        # need to wait until we get either a successful callback, or
        self.done_event.wait(timeout=60)

    def failure(self, exception, text):
        #print(f"could not play text: {exception}")
        aqt.utils.showWarning(f"could not play audio: {exception} (preset: {self.awesometts_preset})")
        self.done_event.set()

    def audio_file_ready(self, path):
        self.audio_file_path = path
        self.done_event.set()

    # this is called on the main thread, after _play finishes
    def _on_done(self, ret: Future, cb: OnDoneCallback) -> None:
        ret.result()

        # inject file into the top of the audio queue
        if self.audio_file_path != None:
            av_player.insert_file(self.audio_file_path)

        # then tell player to advance, which will cause the file to be played
        cb()

    # we don't support stopping while the file is being downloaded
    # (but the user can interrupt playing after it has been downloaded)
    def stop(self):
        pass


def register_tts_player(addon):
    # register our handler
    av_player.players.append(AwesomeTTSPlayer(mw.taskman, addon))
