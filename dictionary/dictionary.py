# from util import *
from utility.debug import *
from dictionary.word import Word

class Dictionary:

    def __init__(self, dict_name = ""):
        self.dict_name = dict_name
        self.dict_file=None

    def search(self, query_word):
        w = Word(query_word = query_word, dict_name = self.NAME)
        # return None if no word found.
        return w

    def suggest(self, query_word):
        return []

    def info(self):
        print(f"{self.dict_name}@{self.dict_file}")

