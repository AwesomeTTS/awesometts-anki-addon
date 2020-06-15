import pydub
import azure.cognitiveservices.speech as speechsdk
import os

# documentation:
# https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/index-speech-to-text
# https://docs.microsoft.com/en-us/python/api/azure-cognitiveservices-speech/azure.cognitiveservices.speech?view=azure-python

# Creates an instance of a speech config with specified subscription key and service region.
# Replace with your own subscription key and region identifier from here: https://aka.ms/speech/sdkregion
if 'AZURE_TTS_KEY' not in os.environ:
    print(f'must set AZURE_TTS_KEY environment variable')
    sys.exit(1)
speech_key = os.environ['AZURE_TTS_KEY']
service_region = "eastus"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Creates an audio configuration that points to an audio file.
# Replace with your own audio filename.
#audio_filename_mp3 = "successful.mp3"
audio_filename_mp3 = "sample-chinese.mp3"
sound = pydub.AudioSegment.from_mp3(audio_filename_mp3)
sound.export("successful.wav", format="wav")
audio_filename_wav = "successful.wav"

audio_input = speechsdk.audio.AudioConfig(filename=audio_filename_wav)

# setup source language
language='zh-CN'

# Creates a recognizer with the given settings
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input, language=language)

print("Recognizing first result...")

# Starts speech recognition, and returns after a single utterance is recognized. The end of a
# single utterance is determined by listening for silence at the end or until a maximum of 15
# seconds of audio is processed.  The task returns the recognition text as result. 
# Note: Since recognize_once() returns only a single utterance, it is suitable only for single
# shot recognition like command or query. 
# For long-running multi-utterance recognition, use start_continuous_recognition() instead.
result = speech_recognizer.recognize_once()

# Checks result.
if result.reason == speechsdk.ResultReason.RecognizedSpeech:
    print("Recognized: {}".format(result.text))
elif result.reason == speechsdk.ResultReason.NoMatch:
    print("No speech could be recognized: {}".format(result.no_match_details))
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    print("Speech Recognition canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print("Error details: {}".format(cancellation_details.error_details))