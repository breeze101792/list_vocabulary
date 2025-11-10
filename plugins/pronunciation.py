
import traceback
import argparse
import time
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import simpleaudio as sa
import io

from utility.debug import *
class Pronunciation:
    def __init__(self):
        self.buffer_word = {}
    def generate_audio_stream(self, text: str, lang: str) -> io.BytesIO:
        """
        Generates an audio stream (MP3 format) from text using Google TTS.

        Args:
            text (str): The text to convert to speech.
            lang (str): The language code for the text (e.g., 'en', 'es').

        Returns:
            io.BytesIO: A BytesIO object containing the MP3 audio data.
        """
        # Create TTS in memory (Google TTS generates MP3)
        start_time = time.time()
        lang_code = self.language_map(lang)
        # print(f"gTTS start generation in {lang_code}")
        tts = gTTS(text, lang=lang_code)
        end_time = time.time()
        # print(f"gTTS generation time: {end_time - start_time:.2f} seconds")
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return mp3_fp

    def play_audio_stream(self, audio_io: io.BytesIO):
        """
        Plays an audio stream (WAV or MP3 format).
        It autodetects the format and uses the appropriate player.

        Args:
            audio_io (io.BytesIO): A BytesIO object containing the audio data.
        """
        # Read the first few bytes to guess the format
        magic_bytes = audio_io.read(4)
        audio_io.seek(0)  # Rewind the stream

        if magic_bytes.startswith(b'RIFF'):  # WAV file
            wave_obj = sa.WaveObject.from_wave_read(audio_io)
            play_obj = wave_obj.play()
            play_obj.wait_done()
        else:  # Assume MP3 or other pydub-compatible format
            song = AudioSegment.from_file(audio_io, format="mp3")
            play(song)

    def language_map(self, lang: str):
        """
        Maps a long language name to its short language code.
        If the input is already a short code, it returns it as is.

        Args:
            lang (str): The language name (e.g., 'English', 'en').

        Returns:
            str: The corresponding short language code.
        """
        lang_map = {
            "english": "en",
            "spanish": "es",
            "french": "fr",
            "german": "de",
            "chinese": "zh-TW",
            "japanese": "ja",
            "korean": "ko",
            "italian": "it",
            "portuguese": "pt",
            "russian": "ru",
            "arabic": "ar",
            "hindi": "hi",
            "bengali": "bn",
            "dutch": "nl",
            "swedish": "sv",
            "norwegian": "no",
            "danish": "da",
            "finnish": "fi",
            "turkish": "tr",
            "vietnamese": "vi",
            "thai": "th",
            "indonesian": "id",
            "malay": "ms",
            "filipino": "fil",
            "greek": "el",
            "hebrew": "iw", # gTTS uses 'iw' for Hebrew
            "polish": "pl",
            "czech": "cs",
            "hungarian": "hu",
            "romanian": "ro",
            "ukrainian": "uk",
        }
        # Convert input to lowercase for case-insensitive matching
        lower_lang = lang.lower()

        # Check if the input is a long name that needs mapping
        if lower_lang in lang_map:
            return lang_map[lower_lang]
        # Otherwise, assume it's already a short code or an unknown language, return as is
        return lang
    def speak_text(self, text: str, lang: str):
        """
        Converts text to speech using Google TTS and plays it.
        This function orchestrates the generation and playback of audio.

        Args:
            text (str): The text to convert to speech.
            lang (str): The language code for the text (e.g., 'en', 'es').
        """
        try:
            if self.buffer_word and self.buffer_word.get('word') == text:
                audio_stream = self.buffer_word['audio']
                audio_stream.seek(0) # Rewind the stream to play from the beginning
            else:
                audio_stream = self.generate_audio_stream(text, lang)
                self.buffer_word = {'word': text, 'audio': audio_stream}

            self.play_audio_stream(audio_stream)
        except Exception as e:
            self.buffer_word = {'word': text, 'audio': audio_stream}
            dbg_error(e)

            traceback_output = traceback.format_exc()
            dbg_error(traceback_output)
            # if anythings happen, we just clear the buffer.
            self.buffer_word = {}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert text to speech and play it.")
    parser.add_argument("-t", "--text", type=str, default="Hello Shaun, how are you today?",
                        help="The text to convert to speech.")
    parser.add_argument("-l", "--lang", type=str, default="en",
                        help="The language code for the text (e.g., 'en', 'es').")
    args = parser.parse_args()

    speak_text(args.text, args.lang)
