import os
import pydub
import azure.cognitiveservices.speech as speechsdk
import tempfile

# validate the audio files we retrieve against the Azure Speech To Text service

AZURE_SERVICES_KEY_ENVVAR_NAME = 'AZURE_SERVICES_KEY'


def recognition_available():
    # make sure the azure key
    return AZURE_SERVICES_KEY_ENVVAR_NAME in os.environ

"""
language should be 'en-US' or 'zh-CN'
supported languages: https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support#speech-to-text
"""
def recognize_speech(mp3_filepath, language):
    assert AZURE_SERVICES_KEY_ENVVAR_NAME in os.environ

    speech_key = os.environ[AZURE_SERVICES_KEY_ENVVAR_NAME]
    service_region = "eastus"
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

    sound = pydub.AudioSegment.from_mp3(mp3_filepath)
    wav_filepath = tempfile.NamedTemporaryFile(suffix='.wav').name
    sound.export(wav_filepath, format="wav")

    audio_input = speechsdk.audio.AudioConfig(filename=wav_filepath)

    # Creates a recognizer with the given settings
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input, language=language)

    # Starts speech recognition, and returns after a single utterance is recognized. The end of a
    # single utterance is determined by listening for silence at the end or until a maximum of 15
    # seconds of audio is processed.  The task returns the recognition text as result. 
    # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
    # shot recognition like command or query. 
    # For long-running multi-utterance recognition, use start_continuous_recognition() instead.
    result = speech_recognizer.recognize_once()

    # Checks result.
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        error_message = "No speech could be recognized: {}".format(result.no_match_details)
        raise Exception(error_message)
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        error_message = "Speech Recognition canceled: {}".format(cancellation_details)
        raise Exception(error_message)

    raise "unknown error"