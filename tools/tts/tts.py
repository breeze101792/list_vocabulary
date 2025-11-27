# pip install TTS playsound
import sys
import argparse
import datetime
from TTS.api import TTS

try:
    import simpleaudio as sa
    simpleaudio_available = True
except ImportError:
    print("Warning: 'simpleaudio' library not found. Audio playback will be skipped.")
    simpleaudio_available = False
    def play_audio_file(file_path):
        pass # Dummy play_audio_file function

def select_speaker(tts_model):
    """
    Allows the user to select a speaker from the available list.
    Args:
        tts_model: The TTS model instance.
    Returns:
        str: The name of the selected speaker.
    """
    print("Available speakers:")
    for i, speaker_name in enumerate(tts_model.speakers):
        print(f"{i}: {speaker_name}")

    while True:
        try:
            speaker_index = int(input("Please choose a speaker by entering the corresponding number: "))
            if 0 <= speaker_index < len(tts_model.speakers):
                selected_speaker = tts_model.speakers[speaker_index]
                print(f"You have selected speaker: {selected_speaker}")
                return selected_speaker
            else:
                print("Invalid number. Please enter a number within the range.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def select_language(tts_model):
    """
    Allows the user to select a language from the available list.
    Args:
        tts_model: The TTS model instance.
    Returns:
        str: The name of the selected language.
    """
    print("Available languages:")
    for i, lang_code in enumerate(tts_model.languages):
        print(f"{i}: {lang_code}")

    while True:
        try:
            lang_index = int(input("Please choose a language by entering the corresponding number: "))
            if 0 <= lang_index < len(tts_model.languages):
                selected_language = tts_model.languages[lang_index]
                print(f"You have selected language: {selected_language}")
                return selected_language
            else:
                print("Invalid number. Please enter a number within the range.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def generate_and_play_tts(tts_model, text, file_path, speaker, language="en", speed=1):
    """
    Generates speech from text and plays the audio file.
    Args:
        tts_model: The TTS model instance.
        text (str): The text to convert to speech.
        file_path (str): The path to save the generated audio file.
        speaker (str): The name of the speaker to use.
        language (str): The language of the text.
    """
    print(f"Generating speech for: '{text}' with speaker '{speaker}'...")
    tts_model.tts_to_file(text=text, file_path=file_path, speaker=speaker, language=language, speed=speed )

    if simpleaudio_available:
        print(f"Playing {file_path}...")
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        play_obj = wave_obj.play()
        play_obj.wait_done() # Wait until sound has finished playing
    else:
        print(f"Simpleaudio not available. Skipping playback of {file_path}.")

def main():
    """
    Main function to run the TTS application.
    """

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate and play TTS audio.")
    parser.add_argument("-o", "--output", type=str, default=f"audio_generation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav",
                        help="Output audio file name (e.g., output.wav)")
    
    # Add mutually exclusive group for text input
    text_group = parser.add_mutually_exclusive_group()
    text_group.add_argument("-t", "--text", type=str,
                            help="Text to convert to speech.")
    text_group.add_argument("-f", "--text-file", type=str,
                            help="Path to a file containing the text to convert to speech.")
    
    parser.add_argument("-s", "--select-speaker", action="store_true",
                        help="Interactively select a speaker from available options.")
    
    parser.add_argument("-l", "--language", type=str, default=None,
                        help="Language of the text (e.g., en, es, fr). Default is None/en.")
    parser.add_argument("-L", "--select-language", action="store_true",
                        help="Interactively select a language from available options.")
    parser.add_argument("--speed", type=float, default=1.0,
                        help="Speed of the generated speech (e.g., 1.0 for normal, 1.5 for faster). Default is 1.0.")
    parser.add_argument("-m", "--model", type=str, default="en_vctk_vits",
                        help="Name of the TTS model to use. Use --list-models to see available models.")
    parser.add_argument("--list-models", action="store_true",
                        help="List available TTS models and exit.")

    args = parser.parse_args()

    # Define available TTS models
    TTS_MODELS = {
        "en": "tts_models/en/ljspeech/vits",
        "en_ljspeech_vits": "tts_models/en/ljspeech/vits",
        "en_vctk_vits": "tts_models/en/vctk/vits",
        "es": "tts_models/es/css10/vits",
        "es_css10_vits": "tts_models/es/css10/vits",
        # "es_mai_tacotron2": "tts_models/es/mai/tacotron2-DDC",
        "multilingual_your_tts": "tts_models/multilingual/multi-dataset/your_tts",
        "multilingual_xtts_v2": "tts_models/multilingual/multi-dataset/xtts_v2",
    }
    # # Choose a Spanish model (Iberian Spanish)
    # mix English and FR
    # tts = TTS("tts_models/multilingual/multi-dataset/your_tts", progress_bar=True, gpu=False)
    # tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False, gpu=False)
    # es
    # tts = TTS("tts_models/es/css10/vits", progress_bar=False, gpu=False)
    # tts = TTS("tts_models/es/mai/tacotron2-DDC", progress_bar=False, gpu=False)
    # en
    # tts = TTS("tts_models/en/ljspeech/vits", progress_bar=False, gpu=False)
    # tts = TTS("tts_models/en/vctk/vits", progress_bar=False, gpu=False)
    # didn't work
    # tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False, gpu=False)
    # tts = TTS("tts_models/multilingual/multi‑dataset/xtts_v1", progress_bar=False, gpu=False)
    # tts = TTS("tts_models/multilingual/multi-dataset/bark", progress_bar=False, gpu=False)

    if args.list_models:
        print("Available TTS models:")
        for name, path in TTS_MODELS.items():
            print(f"- {name}: {path}")
        sys.exit(0)

    file_name = args.output
    
    # Determine the text to be converted
    if args.text:
        input_text = args.text
    elif args.text_file:
        try:
            with open(args.text_file, 'r') as f:
                input_text = f.read().strip()
        except FileNotFoundError:
            print(f"Error: Text file '{args.text_file}' not found.")
            sys.exit(1)
    elif args.model == 'es' or args.language == 'es':
        input_text = "¡Hola a todos! Es un placer estar aquí hoy. Espero que estén disfrutando de este momento. La vida está llena de oportunidades para aprender y crecer. Me encanta explorar nuevas ideas y compartir conocimientos. Estoy emocionado de ver lo que el futuro nos depara y de seguir adelante con entusiasmo. ¡Gracias por su atención!" # Default text
    else:
        # input_text = "Hey, how are you." # Default text
        input_text = """Hello there! It’s such a pleasure to meet you today. I hope you’re having a wonderful time wherever you are. Life moves quickly, so it’s nice to pause for a moment, take a deep breath, and appreciate the simple things around us — like good music, a warm cup of coffee, or a friendly conversation. I’m really glad you’re here, and I’m excited for the journey ahead. Let’s learn something new, share a few laughs, and make this day a little brighter together. Wishing you happiness, peace, and inspiration in everything you do."""

    # Initialize TTS model
    model_path = TTS_MODELS.get(args.model)
    if not model_path:
        print(f"Error: Model '{args.model}' not found. Use --list-models to see available options.")
        sys.exit(1)

    print(f"Initializing TTS model: {args.model} ({model_path})...")
    tts = TTS(model_path, progress_bar=False, gpu=False)

    selected_speaker = None
    if tts.speakers:
        if len(tts.speakers) == 1:
            selected_speaker = tts.speakers[0]
            print(f"Using the only available speaker: {selected_speaker}")
        elif args.select_speaker:
            selected_speaker = select_speaker(tts)
        else:
            selected_speaker = tts.speakers[0] # Use the first speaker as default
            print(f"Using default speaker: {selected_speaker}")
    else:
        print("Warning: No speakers available for the selected model. This might be expected for some models.")

    selected_language = None
    if tts.languages:
        if len(tts.languages) == 1:
            selected_language = tts.languages[0]
            print(f"Using the only available language: {selected_language}")
        elif args.select_language:
            selected_language = select_language(tts)
        elif args.language:
            if args.language in tts.languages:
                selected_language = args.language
                print(f"Using specified language: {selected_language}")
            else:
                print(f"Warning: Specified language '{args.language}' not available for this model. Using default.")
                selected_language = tts.languages[0]
        else:
            selected_language = tts.languages[0]
            print(f"Using default language: {selected_language}")
    else:
        print("Warning: No languages available for the selected model. This might be expected for some models.")
        if args.language:
            print(f"Attempting to use specified language '{args.language}' anyway.")
            selected_language = args.language


    # Convert text to speech and play
    generate_and_play_tts(tts, input_text, file_name, selected_speaker, language=selected_language, speed=args.speed)


if __name__ == "__main__":
    main()

    """
    Generates speech from text and plays the audio file.
    Args:
        tts_model: The TTS model instance.
        text (str): The text to convert to speech.
        file_path (str): The path to save the generated audio file.
        speaker (str): The name of the speaker to use.
    generate_and_play_tts(tts, input_text, file_name, selected_speaker, language=selected_language, speed=args.speed)
        speed (float): The speed of the generated speech.
    """
