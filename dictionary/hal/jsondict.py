import json
import os

from utility.debug import *
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
            self.create_template(self.dict_file)
            dbg_warning(f"Dictionary file not found: {self.dict_file}, create a template.")
        self.dict = None
        self.__buildDict()
    def create_template(self, template_file):
        template_data = [
            {
                "word": "manzana",
                "definitions": [
                    {
                        "part_of_speech": "noun",
                        "gender": "feminine",
                        "meaning": "apple",
                        "example": "Me gusta comer una manzana roja. (I like to eat a red apple.)"
                    }
                ]
            }
        ]
        with open(template_file, "w", encoding="utf-8") as f:
            json.dump(template_data, f, ensure_ascii=False, indent=4)

    def __buildDict(self):
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

        return word_obj
    def search(self, query_word):
        try:
            return self.__search(query_word)
        except KeyError:
            return None
        return None
