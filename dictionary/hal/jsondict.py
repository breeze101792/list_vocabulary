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
    def __init__(self, dict_name = "json dict", dict_file=""):
        self.dict_name = dict_name
        self.dict_file=dict_file
        if self.dict_file != "" and not os.path.exists(self.dict_file):
            self.create_template(self.dict_file)
            dbg_debug(f"Dictionary file not found: {self.dict_file}, create a template.")

        self.dict = dict()
        self.buildDict(self.dict_file)
    def create_template(self, template_file):
        # AI Hint ---------------------------------------------------------------
        # Generate vocabulary entries using the following data structure.
        #
        # template_data is a list. Each item in the list represents one vocabulary entry.
        #
        # Each entry must follow this structure:
        #
        #     {
        #         "word": "<the base word or lemma>",
        #         "definitions": [
        #             {
        #                 "part_of_speech": "<noun | verb | adjective | adverb | etc.>",
        #                 "meaning": "<meaning explained in another language>",
        #                 "example": "<example sentence in the target language> (<translation>)",
        #
        #                 # Optional fields (include only when relevant):
        #                 "gender": "<grammatical gender if the language uses it>",
        #                 "phrase": "<compound form, expression, or phrase>",
        #                 "notes": "<usage notes, irregular forms, or cultural context>"
        #             }
        #         ]
        #     }
        #
        # Rules:
        #     1. “definitions” is always a list, even if there is only a single definition.
        # 2. Optional fields (gender, phrase, notes) should appear only when they apply
        # to the target language or word type.
        # 3. Example sentences must always include the original sentence and a translation.
        # 4. Meanings must be concise and clearly understandable for learners.
        # 5. If multiple definitions exist, order them from most common to least common.
        #
        # Output ONLY entries using this structure.
        # ----------------------------------------------------------------------
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
            },
            {
                "word": "trabajar",
                "definitions": [
                    {
                        "part_of_speech": "verb",
                        "meaning": "to work",
                        "example": "Necesito trabajar mucho hoy. (I need to work a lot today.)"
                    },
                    {
                        "phrase": "trabajar en",
                        "meaning": "to work on",
                        "example": "Voy a trabajar en mi proyecto. (I am going to work on my project.)"
                    }
                ]
            }
        ]
        with open(template_file, "w", encoding="utf-8") as f:
            json.dump(template_data, f, ensure_ascii=False, indent=4)

    def cleanAll(self):
        self.dict = dict()
        self.dict_file = ""
    def buildDict(self, dict_file):
        self.dict = dict()
        if not os.path.exists(dict_file):
            return

        with open(dict_file, "r", encoding="utf-8") as jfile:
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
