from utility.debug import *

from core.config import AppConfigManager
from dictionary.hal.ecdict import SECDict
# from dictionary.hal.local_dict import LocalDict
from dictionary.hal.jsondict import JsonDict
from dictionary.hal.stardict import StartDict

class Manager:
    def __init__(self):
        dbg_info("Dictionary Manager")

        appcgm = AppConfigManager()
        self.__language = appcgm.get('variable.language')

        if self.__language == "spanish":
            # dict_file=os.path.join(appcgm.get_path('dictionary'), 'spanish_basic_vocabs.json')
            # self.def_dict = JsonDict(dict_name = "spanish basic vocabs", dict_file=dict_file)

            # https://github.com/doozan/spanish_data?tab=readme-ov-file
            # FIXME, pleaes remove it in the future.
            dict_file="/Users/shaowu/Downloads/Spanish-English-Wiktionary-2025-10-20/es-en.enwikt"
            self.def_dict = StartDict(dict_name = "es-en.enwikt", dict_file=dict_file)
        else:
            # if self.__language == "english":
            dict_file=os.path.join(appcgm.get_path('dictionary'), 'secdict.db')
            self.def_dict = SECDict(dict_file=dict_file)

    def search(self, query_word):
        # return word class list of dictionary.
        dict_word = self.def_dict.search(query_word)
        if dict_word is None:
            dbg_warning("The word haven't been found in dictionary")
            return []
        return [dict_word]
    def suggest(self, query_word):
        # return a list of possiable words.
        suggest_list = self.def_dict.suggest(query_word = query_word)
        return suggest_list
