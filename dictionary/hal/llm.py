import os
import json
import traceback
from core.config import AppConfigManager
from openai import OpenAI
from dictionary.word import PureWord
from dictionary.dictionary import Dictionary
from utility.debug import *

class LLM(Dictionary):
    cached_data = {}

    def __init__(self, dict_name = "LLM", dict_file="", language = "english"):
        self.dict_name = dict_name

        # appcgm = AppConfigManager()
        # self.language = appcgm.get("variable.language")
        # dictionar_path = appcgm.get_path("dictionary")
        # llm_cached_path = os.path.join(dictionar_path, "llm")
        # if not os.path.exists(llm_cached_path):
        #     os.makedirs(llm_cached_path, exist_ok=True)
        #
        # self.cached_dict_path = os.path.join(llm_cached_path ,f"{self.language}_cached.json")

        self.cached_dict_path = dict_file
        self.language = language
        self.dict_name = dict_name

        ## Cached data
        if len(LLM.cached_data) == 0:
            self._load_cache()

        # this is for gemini.
        google_api_key=os.environ.get("GEMINI_API_KEY")
        if google_api_key != "":
            self.api_key=google_api_key
            self.server_url="https://generativelanguage.googleapis.com/v1beta"
            self.model="gemini-2.5-flash"

        openai_api_key=os.environ.get("OPENAI_API_KEY")
        if openai_api_key != "" and google_api_key == "":
            self.api_key=openai_api_key
            self.server_url="https://api.openai.com/v1"
            self.model="GPT-5"

    def _load_cache(self):
        """Loads the LLM cache from the cached_dict_path."""
        LLM.cached_data = {}
        if os.path.exists(self.cached_dict_path):
            try:
                with open(self.cached_dict_path, 'r', encoding='utf-8') as f:
                    LLM.cached_data = json.load(f)
            except json.JSONDecodeError:
                dbg_error(f"Warning: LLM cache file '{self.cached_dict_path}' is corrupted. Starting with an empty cache.")
                LLM.cached_data = {}
            except Exception as e:
                dbg_error(f"Error loading LLM cache file: {e}")
                LLM.cached_data = {}
        return LLM.cached_data

    def _save_cache(self):
        """Saves the LLM cache to the cached_dict_path."""
        try:
            with open(self.cached_dict_path, 'w', encoding='utf-8') as f:
                json.dump(LLM.cached_data, f, ensure_ascii=False, indent=4)
            dbg_info(f"LLM cache saved to '{self.cached_dict_path}'.")
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
                word_obj.meaning = LLM.cached_data[query_word]
                return word_obj
            else:
                return None

        except KeyError:
            return None
        return None

    def ask(self, message, prompt = "You are a helpful assistant."):

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.server_url
        )

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ]
        )

        # print(response.choices[0].message.content)
        return response.choices[0].message.content

    def openai_dict(self, query_word, cached = True):

        # if cached:
        if cached and query_word in LLM.cached_data:
            dbg_info(f"Retrieving '{query_word}' from LLM cache.")
            word_obj = PureWord()
            word_obj.word = query_word
            word_obj.dict_name = "LLM Cached"
            word_obj.meaning = LLM.cached_data[query_word]
            return word_obj

        prompt = """
You are a detailed multilingual dictionary engine.
When the user gives you a word in any language, provide the following details in plain text:

Word: the exact word typed
Meaning 1: for each meaning, give the following in this exact order and style(could have multiple meaning. Lebal other as 2,3...):
 * Part of Speech: List all applicable parts of speech, including gender if present.
 * Definition:
  - Original: (if original language is Spanish, then we give the definition of it with Spanish and change the label to Spanish)
  - English:
  - Chinese: (traditional)
 * Example sentences:(Note. ignore the orignal language traslation. ex. If the original is englsih, then we ignore english traslation.)
  - original-language sentence
    (English translation / Chinese translation)
Related phrases: list start with ' - ', include the one-lined meaning with it.
Related words: list start with ' - ', include the one-lined meaning with it.
Original form and origin: include lemma, verb tense, other forms, and etymology
Story / interesting facts: if the word has notable history, anecdotes, or cultural context, include it. If not, skip this section.

Format each meaning separately with its own examples.
Use only spaces for indentation. No bullets, dashes, or special formatting.
Do not use bold or italics. Return plain readable text only.
If no language is specified, use English to explain it.
If this word is not valid in this language, return an empty response.
        """
        message = f"Please provide the dictionary content for the {self.language} word '{query_word}'"

        response = self.ask(message = message, prompt = prompt)

        word_obj = PureWord()
        try:
            word_obj.word = query_word
            word_obj.dict_name = "LLM Search"
            if len(response) < len(query_word):
                word_obj.meaning = f"Word not found. rep: {response}"
            else:
                word_obj.meaning = response

                # Save the new response to the cache
                LLM.cached_data[query_word] = response
                self._save_cache()
                dbg_info(f"Cached '{query_word}' to LLM cache.")
        except Exception as e:
            if query_word is not None:
                word_obj.meaning = f"Connection error. {query_word} not found."
            dbg_error(e)

            traceback_output = traceback.format_exc()
            dbg_error(traceback_output)
        # finally:
        #     pass

        return word_obj
