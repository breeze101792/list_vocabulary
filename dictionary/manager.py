import traceback

import os

from utility.debug import *
from core.config import AppConfigManager
from dictionary.hal.ecdict import SECDict
# from dictionary.hal.local_dict import LocalDict
from dictionary.hal.jsondict import JsonDict
from dictionary.hal.stardict import StartDict

class Manager:
    word_list_dict = None
    dict_list = []
    def_dict = None
    def __init__(self, language = None):
        dbg_info("Dictionary Manager")

        appcgm = AppConfigManager()
        if language is None:
            self.__language = appcgm.get('variable.language')
        else:
            self.__language = language

        self.__dict_root_path = appcgm.get_path('dictionary')
        # Manager.dict_list = []
        # self.def_dict = none

        # post init
        if len(Manager.dict_list) == 0:
            self.dict_init()

    def __dict_search_file(self, ext, dict_root_path):
        if not os.path.exists(dict_root_path):
            return []
        found_files = []
        for root, _, files in os.walk(dict_root_path):
            for file in files:
                if file.endswith(ext):
                    found_files.append(os.path.join(root, file))
        # dbg_print(found_files)
        return found_files
        # return []
    def __dict_init_stardict(self, root_path):
        # init stardict
        startdict_ifo_list = self.__dict_search_file(ext = 'ifo', dict_root_path = root_path)
        for each_ifo in startdict_ifo_list:
            try:
                dict_file=os.path.splitext(each_ifo)[0]
                book_name = "NA"
                with open(each_ifo, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith("bookname="):
                            book_name = line.strip().split('=', 1)[1]
                            break
                dbg_info(f"dictionary: {book_name}@{dict_file}")

                tmp_dict = StartDict(dict_name = book_name, dict_file=dict_file)
                Manager.dict_list.append(tmp_dict)
            except Exception as e:
                dbg_warning(e)

                traceback_output = traceback.format_exc()
                dbg_warning(traceback_output)

    def dict_init(self):
        # reset before init.
        Manager.dict_list = []
        Manager.def_dict = None

        if Manager.word_list_dict is None:
            # NOTE. word list dictionary, don't init at the begining
            Manager.word_list_dict = JsonDict(dict_name = f"{self.__language} lesson word list.")
        Manager.dict_list.append(Manager.word_list_dict)

        # language depends dict.
        if self.__language == "spanish":
            pass
        else:
            # if self.__language == "english":
            dict_file=os.path.join(self.__dict_root_path, 'secdict.db')
            if os.path.exists(dict_file):
                tmp_dict = SECDict(dict_file=dict_file)
                Manager.dict_list.append(tmp_dict)
            else:
                dbg_warning(f"SECDict file not found: {dict_file}, skipping setup.")

        # NOTE. customize dictionary
        dict_file=os.path.join(self.__dict_root_path, f"lexicon/{self.__language}_LexExpand.json")
        if not os.path.exists(dict_file):
            os.makedirs(os.path.dirname(dict_file), exist_ok=True)
        tmp_dict = JsonDict(dict_name = f"{self.__language} lexicon expand", dict_file=dict_file)
        Manager.dict_list.append(tmp_dict)

        # language specify dicts
        dict_root_path = os.path.join(self.__dict_root_path, f"stardict/{self.__language}")
        self.__dict_init_stardict(root_path = dict_root_path)

        # general dict
        dict_root_path = os.path.join(self.__dict_root_path, f"stardict/all")
        self.__dict_init_stardict(root_path = dict_root_path)

        Manager.def_dict = Manager.dict_list[0]
    def list_dictionary(self, args = None):
        for each_dict in Manager.dict_list:
            each_dict.info()
            # dbg_print(f"Dictionary: {each_dict.dict_name}")
        return True
    def search(self, query_word):
        dict_word_list = []

        for each_dict in Manager.dict_list:
            # return word class list of dictionary.
            tmp_dict_word = each_dict.search(query_word)
            if tmp_dict_word is not None:
                dict_word_list.append(tmp_dict_word)

        return dict_word_list

    def suggest(self, query_word):
        # return a list of possiable words.
        suggest_list = Manager.def_dict.suggest(query_word = query_word)
        return suggest_list
