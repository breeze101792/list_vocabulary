import argparse
import time
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import simpleaudio as sa
import io

def generate_audio_stream(text: str, lang: str) -> io.BytesIO:
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
    print(f"gTTS start generation")
    tts = gTTS(text, lang=lang)
    end_time = time.time()
    print(f"gTTS generation time: {end_time - start_time:.2f} seconds")
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    print(f"audio size: {mp3_fp.getbuffer().nbytes}")
    if mp3_fp.getbuffer().nbytes == 0:
        print("Warning: gTTS generated an empty audio stream.")
    return mp3_fp

def save_audio_stream_to_file(audio_io: io.BytesIO, output_path: str):
    """
    Saves an audio stream to a specified file.

    Args:
        audio_io (io.BytesIO): A BytesIO object containing the audio data.
        output_path (str): The path to the file where the audio should be saved.
    """
    try:
        with open(output_path, "wb") as f:
            f.write(audio_io.getvalue())
        print(f"Audio successfully saved to {output_path}")
    except IOError as e:
        print(f"Error saving audio to file {output_path}: {e}")

def play_audio_stream(audio_io: io.BytesIO):
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

def speak_text(text: str, lang: str):
    """
    Converts text to speech using Google TTS and plays it.
    This function orchestrates the generation and playback of audio.

    Args:
        text (str): The text to convert to speech.
        lang (str): The language code for the text (e.g., 'en', 'es').
    """
    audio_stream = generate_audio_stream(text, lang)
    play_audio_stream(audio_stream)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert text to speech and play it.")
    parser.add_argument("-t", "--text", type=str, default="Hello Shaun, how are you today?",
                        help="The text to convert to speech.")
    parser.add_argument("-l", "--lang", type=str, default="en",
                        help="The language code for the text (e.g., 'en', 'es').")
    parser.add_argument("-o", "--output", type=str,
                        help="Optional: Path to save the generated audio file (e.g., 'output.mp3').")
    args = parser.parse_args()

    audio_stream = generate_audio_stream(args.text, args.lang)

    if args.output:
        save_audio_stream_to_file(audio_stream, args.output)
    else:
        play_audio_stream(audio_stream)
