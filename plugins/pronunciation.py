
import traceback
import argparse
import time
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import simpleaudio as sa
import io
import threading

from utility.debug import *
class Pronunciation:
    buffer_dictionary = {}
    def __init__(self):
        self.__max_buffer_count = 100
        self.current_playback_thread: threading.Thread | None = None
        self.stop_current_playback_event: threading.Event = threading.Event()
        self.thread_management_lock = threading.Lock()

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
    
    def _speak_text_sync(self, text: str, lang: str):
        """
        Internal synchronous function to convert text to speech and play it.
        This function is designed to be run in a separate thread for asynchronous calls.
        It checks `self.stop_current_playback_event` to see if it should stop early.
        """
        try:
            key = f"{text}-{lang}"
            if key in Pronunciation.buffer_dictionary:
                audio_stream = Pronunciation.buffer_dictionary[key]
                audio_stream.seek(0) # Rewind the stream to play from the beginning
            else:
                audio_stream = self.generate_audio_stream(text, lang)
                # TODO, check if dictionary is too big then we remove some of it.

                Pronunciation.buffer_dictionary[key] = audio_stream
                # If the buffer dictionary grows too large, remove the oldest item
                if len(Pronunciation.buffer_dictionary) > self.__max_buffer_count:
                    # Remove the first item (oldest) to keep the dictionary size manageable
                    oldest_key = next(iter(Pronunciation.buffer_dictionary))
                    del Pronunciation.buffer_dictionary[oldest_key]

            # Check if a new request has come in while generating audio
            if self.stop_current_playback_event.is_set():
                dbg_info(f"Stopping playback for '{text}' due to new request.")
                return

            self.play_audio_stream(audio_stream)
        except Exception as e:
            dbg_error(e)
            traceback_output = traceback.format_exc()
            dbg_error(traceback_output)
            # if anything happens, we just clear the buffer.
            # if anything happens, we just clear the buffer.
            if key in Pronunciation.buffer_dictionary:
                del Pronunciation.buffer_dictionary[key]

    def speak_text(self, text: str, lang: str, is_async: bool = True):
        """
        Converts text to speech using Google TTS and plays it.
        This function orchestrates the generation and playback of audio.

        Args:
            text (str): The text to convert to speech.
            lang (str): The language code for the text (e.g., 'en', 'es').
            is_async (bool): If True, the audio generation and playback will run in a separate thread.
                             If a previous asynchronous request is still ongoing, it will be signaled to stop.
        """
        if is_async:
            with self.thread_management_lock:
                # If there's an existing thread, signal it to stop
                if self.current_playback_thread is not None and self.current_playback_thread.is_alive():
                    self.stop_current_playback_event.set()  # Signal the old thread to stop
                    # Optionally, wait a very short time for the old thread to react.
                    # This join is non-blocking for the main thread if timeout is small.
                    self.current_playback_thread.join(timeout=0.01)
                    dbg_info("Previous pronunciation thread signaled to stop.")

                # Clear the event for the new thread before starting it
                self.stop_current_playback_event.clear()

                # Create and start the new thread
                new_thread = threading.Thread(target=self._speak_text_sync, args=(text, lang))
                self.current_playback_thread = new_thread
                new_thread.start()
        else:
            # For synchronous calls, we don't manage threads or stop events in the same way.
            # The _speak_text_sync will run in the current thread.
            self._speak_text_sync(text, lang)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert text to speech and play it.")
    parser.add_argument("-t", "--text", type=str, default="Hello Shaun, how are you today?",
                        help="The text to convert to speech.")
    parser.add_argument("-l", "--lang", type=str, default="en",
                        help="The language code for the text (e.g., 'en', 'es').")
    parser.add_argument("-a", "--asynchronous", action="store_true", default=False,
                        help="Run speech generation and playback asynchronously.")
    args = parser.parse_args()

    pronunciator = Pronunciation()
    pronunciator.speak_text(args.text, args.lang, is_async = args.asynchronous)
