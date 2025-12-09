import os
import json
import time
import traceback
import threading
from openai import OpenAI
from dictionary.word import PureWord
from dictionary.dictionary import Dictionary
from utility.debug import *
from core.config import AppConfigManager

class LLM(Dictionary):
    language = ""
    cached_data = {}
    cached_dict_path = ""
    pending_searches = set()
    _ask_lock = threading.Lock()

    def __init__(self, dict_name = "LLM", dict_file=None, language = None):
        self.dict_name = dict_name

        if language is not None:
            LLM.language = language
        if dict_file is not None:
            LLM.cached_dict_path = dict_file
        dbg_debug(f"LLM init with {LLM.language}")
        if len(LLM.language ) == 0 or len(LLM.cached_dict_path ) == 0:
            dbg_error('Please init LLM first.')
            raise Exception("LLM not initialized properly.")

        ## Cached data
        if len(LLM.cached_data) == 0:
            self._load_cache()

    def _load_cache(self):
        """Loads the LLM cache from the cached_dict_path."""
        LLM.cached_data = {}
        if os.path.exists(LLM.cached_dict_path):
            try:
                with open(LLM.cached_dict_path, 'r', encoding='utf-8') as f:
                    LLM.cached_data = json.load(f)
            except json.JSONDecodeError:
                dbg_error(f"Warning: LLM cache file '{LLM.cached_dict_path}' is corrupted. Starting with an empty cache.")
                LLM.cached_data = {}
            except Exception as e:
                dbg_error(f"Error loading LLM cache file: {e}")
                LLM.cached_data = {}
        return LLM.cached_data

    def _save_cache(self):
        """Saves the LLM cache to the cached_dict_path."""
        try:
            with open(LLM.cached_dict_path, 'w', encoding='utf-8') as f:
                json.dump(LLM.cached_data, f, ensure_ascii=False, indent=4)
            dbg_info(f"LLM cache saved to '{LLM.cached_dict_path}'.")
        except Exception as e:
            dbg_error(f"Error saving LLM cache file: {e}")
    def remove(self, query_word):
        try:
            if query_word in LLM.cached_data:
                del LLM.cached_data[query_word]
                self._save_cache()
                return True
        except KeyError:
            return False
        return False
    def search(self, query_word):
        try:
            if query_word in LLM.cached_data:
                # print(f"Retrieving '{query_word}' from LLM cache.")
                word_obj = PureWord()
                word_obj.word = query_word
                word_obj.dict_name = self.dict_name
                word_obj.meaning = LLM.cached_data[query_word].lstrip('\n')
                return word_obj
            else:
                return None

        except KeyError:
            return None
        return None

    def ask(self, message, prompt = "You are a helpful assistant.", extra_delay = 0):
        ret = "Query fail."
        with LLM._ask_lock:
            ret = self._ask(message = message, prompt = prompt)
            # FIXME: Temporary solution to avoid hitting rate limits.
            time.sleep(1 + extra_delay)
        return ret

    def _ask(self, message, prompt = "You are a helpful assistant."):
        appcgm = AppConfigManager()
        api_key=appcgm.get("llm.api_key")
        server_url=appcgm.get("llm.server_url")
        model=appcgm.get("llm.model")
        dbg_debug(f"{model}@{server_url}")

        client = OpenAI(
            api_key=api_key,
            base_url=server_url
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ]
        )
        dbg_debug(f"system: {prompt}")
        dbg_debug(f"user: {message}")

        # print(response.choices[0].message.content)
        return response.choices[0].message.content

    def _search_worker(self, query_word, store = True, notify = None):
        prompt_definition = f""" 
 * Translation/Definition: This part should include the traslation and definition.
            """
        prompt_core = ""

        if LLM.language == 'english':
            prompt_core = """
 - English: Core meaning in English
 - Chinese: Core meaning in Chinese traditional
            """
            prompt_definition += f""" 
  - English: Translation/Definition in English
  - Chinese: Translation/Definition in Chinese traditional
 * Example sentences:
  - {LLM.language} sentence
    (Chinese traditional translation)
            """
        elif LLM.language == 'chinese':
            prompt_core = """
 - Chinese: Core meaning in Chinese traditional
 - English: Core meaning in English
            """
            prompt_definition += f""" 
  - Chinese: Translation/Definition in Chinese traditional
  - English: Translation/Definition in English
 * Example sentences:
  - {LLM.language} sentence
    (English translation)
            """
        else:
            prompt_core = """
 - {LLM.language}: Core meaning in {LLM.language}
 - Chinese: Core meaning in Chinese traditional
 - English: Core meaning in English
            """
            prompt_definition += f""" 
  - {LLM.language}: Translation/Definition in {LLM.language}
  - Chinese: Translation/Definition in Chinese traditional
  - English: Translation/Definition in English
 * Example sentences:
  - {LLM.language} sentence
    (English translation / Chinese translation)
            """

        # Verb Conjugations: (include only if the word is a verb)
        prompt = f"""
You are a detailed multilingual dictionary engine.
When the user gives you a {LLM.language} word, provide the following details in plain text:
Word: the exact word typed and its original form.

Core meaning: Extract the core meaning of the word. The core meaning is the most basic, original, and central conceptual idea from which all extended senses, metaphorical uses, and phrasal uses can logically develop. Provide the core meaning as a single, concise English definition with an appropriate level of abstraction, avoiding overly specific contexts or examples. Show it on the following languages.
{prompt_core}

Meaning 1: For each meaning, provide the following in this exact order and style (if multiple meanings exist, sort them by frequency of use, labeling subsequent meanings as 2, 3, etc.):
 * Part of Speech: List all applicable parts of speech, including gender if present.
{prompt_definition}

Related phrases: list start with ' - ', include the one-lined meaning with it.

Related words: list start with ' - ', include the one-lined meaning with it.

Original form and origin: include lemma, verb tense, other forms, and etymology

Story / interesting facts: if the word has notable history, anecdotes, or cultural context, include it. If not, skip this section.

Word Forms: List all grammatical inflections and morphological variations of the word, including tenses, conjugations, plurals, and comparative forms if applicable.

Please adhere to the following rules:
1. Present each meaning separately, accompanied by its own examples.
2. Use only spaces for indentation; avoid bullets, dashes, or any other special formatting.
3. Do not use Markdown syntax; provide plain, readable text only.
4. If the word is not valid in {LLM.language}, respond with "WORD NOT FOUND".
5. Unless otherwise specified, provide explanations in English/Chinese.
        """
        message = f"Please provide the dictionary content for the {LLM.language} word '{query_word}'"

        appcgm = AppConfigManager()
        extra_delay = appcgm.get('llm.request_delay')
        response = "query_word. Query fail."
        try:
            response = self.ask(message = message, prompt = prompt, extra_delay = extra_delay)

            if len(response) < len(query_word) or response == "WORD NOT FOUND":
                dbg_debug(f"{query_word} not found.")
                notify(query_word + ". Word not found.")
            else:
                if notify is not None:
                    notify(query_word)
                dbg_info(f"Cached '{query_word}' to LLM cache.")
                if store:
                    LLM.cached_data[query_word] = response.lstrip('\n')
                    self._save_cache()
        except Exception as e:
            if query_word is not None:
                notify(query_word + ". Connection error.")
            dbg_debug(e)

            traceback_output = traceback.format_exc()
            dbg_debug(traceback_output)
        finally:
            LLM.pending_searches.discard(query_word)

        return response

    def openai_dict(self, query_word, cached = True, blocking = True, store = True, notify = None):
        if query_word == "":
            dbg_debug("Not query_word.")
            return None

        # if cached:
        if cached and query_word in LLM.cached_data:
            dbg_info(f"Retrieving '{query_word}' from LLM cache.")
            word_obj = PureWord()
            word_obj.word = query_word
            word_obj.dict_name = "LLM Cached"
            word_obj.meaning = LLM.cached_data[query_word]
            return word_obj

        if blocking is True:
            response = self._search_worker(query_word, store = store)

            word_obj = PureWord()
            word_obj.word = query_word
            word_obj.dict_name = "LLM Dictionary"
            word_obj.meaning = response
            return word_obj
        else:
            if query_word in LLM.pending_searches:
                word_obj = PureWord()
                word_obj.word = query_word
                word_obj.dict_name = "LLM Search"
                word_obj.meaning = "Searching..."
                return word_obj
            LLM.pending_searches.add(query_word)

            thread = threading.Thread(target=self._search_worker, args=(query_word, store, notify))
            thread.daemon = True
            thread.start()

            word_obj = PureWord()
            word_obj.word = query_word
            word_obj.dict_name = "LLM Search"
            word_obj.meaning = "Background searching..."
            return word_obj
