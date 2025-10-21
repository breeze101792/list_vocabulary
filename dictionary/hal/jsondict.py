import json
import os

from dictionary.word import JWord
from dictionary.dictionary import Dictionary

def ischinese(test_str):
    for ch in test_str:
        if ord(ch) < 0x4e00 or ord(ch) > 0x9fff:
            return False
    return True

class JsonDict(Dictionary):
    def __init__(self, dict_name = "json dict", dict_file="./local.json"):
        self.dict_name = dict_name
        self.dict_file=dict_file
        if not os.path.exists(self.dict_file):
            raise FileNotFoundError(f"Dictionary file not found: {self.dict_file}")
        self.dict = None
        self.__buildDict()
    def __buildDict(self):
        # dict_file="/Users/shaowu/projects/list_vocabulary/dictionary/hal/example/spanish_basic_vocabs.json"
        self.dict = dict()
        with open(self.dict_file, "r", encoding="utf-8") as jfile:
            # Load the entire JSON file as a list of entries
            data = json.load(jfile)
            for entry in data:
                word = entry["word"]
                self.dict[word] = entry["definitions"]

    def __search(self, query_word):
        definitions = self.dict[query_word] # This is now a list of definition dictionaries
        word_obj = JWord()
        word_obj.word = query_word
        word_obj.dict_name = self.dict_name
        word_obj.definitions = definitions

        # for definition in definitions:
        #     part_of_speech = definition.get("part_of_speech") # Use .get to avoid KeyError if key is missing
        #     meaning = definition.get("meaning")
        #     example = definition.get("example", "") # Default to empty string for example
        #
        #     if not part_of_speech or not meaning:
        #         print(f"Warning: Incomplete definition for word '{query_word}': {definition}")
        #         continue
        #
        #     part_list = None
        #     if part_of_speech == 'noun':
        #         part_list = word_obj.noun
        #     elif part_of_speech == 'verb':
        #         part_list = word_obj.verb
        #     elif part_of_speech == 'adverb':
        #         part_list = word_obj.adverb
        #     elif part_of_speech == 'adjective':
        #         part_list = word_obj.adjective
        #     else:
        #         # Default to 'other' for any unhandled part of speech
        #         part_list = word_obj.other
        #         print(f"Warning: Unrecognized part of speech '{part_of_speech}' for word '{query_word}'. Storing under 'other'.")
        #
        #     if part_list is not None:
        #         # Append meaning and example in the format expected by the Word class
        #         part_list.append([meaning, [[example, ""]]])
        return word_obj
    def search(self, query_word):
        try:
            return self.__search(query_word)
        except KeyError:
            return None
        return None
