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

import anki.sound
from anki.lang import compatMap
from anki.sound import AVTag, TTSTag
from aqt import mw
from aqt.taskman import TaskManager
from aqt.sound import OnDoneCallback, av_player
from aqt.tts import TTSProcessPlayer, TTSVoice

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
        voices = []
        std_code="en_US"
        preset_name = "Microsoft Azure Neural Guy"
        #voices.append(AwesomeTTSVoice(name="aTTS", lang=std_code, atts_preset=preset_name))
        #voices.append(AwesomeTTSVoice(name="aTTS_preset_1", lang=std_code, atts_preset=preset_name))
        voices.append(AwesomeTTSVoice(name=preset_name, lang=std_code, atts_preset=preset_name))

        return voices  # type: ignore

    # this is called on a background thread, and will not block the UI
    def _play(self, tag: AVTag) -> None:
        try:
            assert isinstance(tag, TTSTag)
            match = self.voice_for_tag(tag)
            assert match
            voice = cast(AwesomeTTSVoice, match.voice)

            # is the field blank?
            if not tag.field_text.strip():
                return
            
            awesometts_preset = voice.atts_preset

            #sys.stderr.write(f"need to play audio: [{tag.field_text}], preset: {awesometts_preset}")

            # load the preset from the above name
            text = tag.field_text
            print("*step1")

            config = self._addon.config
            print("*step2")

            config_presets = config['presets']

            print("*step3")

            preset = config_presets[awesometts_preset]

            print("*step4")

            #sys.stderr.write(preset)
            print(preset)

            self._addon.router(
                svc_id=preset['service'],
                text=text,
                options=preset,
                callbacks=dict(
                    okay=anki.sound.play,
                    fail=lambda exception, text: (
                        print(f"could not play text: {exception}")
                    ),
                ),
            )        
        except:
            e = sys.exc_info()[0]            
            sys.stderr.write(e)


    # this is called on the main thread, after _play finishes
    def _on_done(self, ret: Future, cb: OnDoneCallback) -> None:
        pass

    # we don't support stopping while the file is being downloaded
    # (but the user can interrupt playing after it has been downloaded)
    def stop(self):
        pass


def register_tts_player(addon):
    # register our handler
    av_player.players.append(AwesomeTTSPlayer(mw.taskman, addon))
