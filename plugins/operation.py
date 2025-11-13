from enum import Enum, auto
import random
import threading
import traceback
import json
import time
import subprocess as sp
import sqlite3

from utility.utils import getch
from utility.debug import *

# from dictionary.hal.ecdict import *
from dictionary.manager import Manager as DictMgr

from core.wordbank import WordBank
from core.data import FileData

from plugins.page.dictpage import DictPage 
from plugins.page.listpage import MemorizeListPage

class Operation:
    def __init__(self, wordbank = None):
        self.wordbank = wordbank
        self.dict_mgr = DictMgr()

    def __ui_print(self, *args):
        print("".join(map(str,args)), end="")
    def __ui_print_line(self, *args):
        print("".join(map(str,args)))

    def __suggest(self, query_word, filter_flag = True):
        # searching in dictionary
        word_list = self.dict_mgr.suggest(query_word)
        if word_list == False:
            dbg_warning("The word haven't been found in dictionary")
            return False
        # self.__ui_print("{} ".format(query_word))
        if word_list:
            return word_list
        else:
            return False
    def __search_word(self, query_word, filter_flag = True):
        # searching in dictionary
        dict_word = self.dict_mgr.search(query_word)
        if dict_word == []:
            dbg_warning("The word haven't been found in dictionary")
            return []
        # searching in databas
        db_word = self.wordbank.get_word(query_word)

        if dict_word:
            # dict_word.show_meaning()
            return dict_word
        else:
            return []

    def def_search(self, args):

        dict_word=None
        # dbg_trace(args)
        # arg_dict = ArgParser.args_parser(args)
        arg_dict = args
        arg_key = list(arg_dict.keys())

        # print(arg_dict[arg_key[0]])
        dict_word = self.__search_word(arg_dict[arg_key[0]])
        if dict_word is []:
            word_list = self.__suggest(arg_dict[arg_key[0]])
            if word_list is False:
                return False
            else:
                self.__ui_print_line(word_list)
            # self.__ui_print_line('No such word.')
        else:
            dict_word.show_meaning()
            if self.wordbank.insert(dict_word.word):
                self.wordbank.commit()
            return True
    def search(self, args):

        dict_word_list=None
        # dbg_trace(args)
        # arg_dict = ArgParser.args_parser(args)
        arg_dict = args
        arg_key = list(arg_dict.keys())

        # print(arg_dict[arg_key[0]])
        dict_word_list = self.__search_word(arg_dict[arg_key[1]])
        if len(dict_word_list) > 0:
            dict_word_list[0].show_meaning()
            if self.wordbank.insert(dict_word_list[0].word):
                self.wordbank.commit()
            return True
        else:
            word_list = self.__suggest(arg_dict[arg_key[1]])
            if word_list is False:
                return False
            else:
                self.__ui_print_line(word_list)
            # self.__ui_print_line('No such word.')
    def fuzzy(self, args):
        # dbg_trace(args)
        # arg_dict = ArgParser.args_parser(args)
        arg_dict = args
        arg_key = list(arg_dict.keys())

        # print(arg_dict[arg_key[0]])
        word_list = self.__suggest(arg_dict[arg_key[1]])
        dbg_debug('word list: ', word_list)
        if word_list is False:
            self.__ui_print_line('No such word.')
            return False
        else:
            self.__ui_print_line(word_list)
            return True
    def dump_vocabulary(self, args):

        file_name = ""
        if args['#'] == 1:
            file_name = os.path.abspath(args['1'])

        word_list = self.wordbank.quer_for_all_word()
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    for each_word in word_list:
                        f.write(",".join([each_item.__str__() for each_item in each_word]) + '\n')
                self.__ui_print_line(f"Vocabulary dumped to '{file_name}' successfully.")
            except IOError as e:
                self.__ui_print_line(f"Error writing to file '{file_name}': {e}")
                return False
        else:
            for each_word in word_list:
                self.__ui_print_line(each_word)

        return True

        return True
    def cmd_search_dictionary(self, args = None):
        page_dict = DictPage(self.wordbank)

        page_dict.run()

        return True
    def cmd_memorize_words(self, args = None):
        word_idx = 0
        times_idx = 1
        familiar_idx = 2

        familiar_target = 1
        times_target = -1
        list_number = 0
        flag_reverse = False
        flag_meaning = False
        # default not show reviewed words.
        flag_reviewed_word = False
        flag_forgotten_word = None

        for each_idx in range(1, args['#'] + 1):
            if args[str(each_idx)] == 'reverse':
                flag_reverse = True

            if args[str(each_idx)] == 'new':
                familiar_target = 1
                times_target = 1

            if args[str(each_idx)] == 'forgotten':
                flag_forgotten_word = True

        if 'familiar' in args:
            familiar_target = int(args['familiar'])

        if 'times' in args:
            times_target = int(args['times'])

        if 'number' in args:
            list_number = int(args['number'])

        # dbg_info("Change familiar level to {}.".format(familiar_target))

        word_list = []
        for each_word in self.wordbank.quer_for_all_word(familiar = familiar_target, forgotten = flag_forgotten_word):
            if len(each_word) < 3:
                continue
            if times_target != -1 and each_word[times_idx] > times_target:
                continue

            if each_word[familiar_idx] == familiar_target:
                word_list.append(each_word[word_idx])

        if flag_reverse is True:
            word_list.reverse()

        if list_number != 0 and list_number < len(word_list):
            word_list = word_list[-list_number:]

        random.shuffle(word_list)
        # dbg_info(word_list)

        # self.__memorize_list(word_list)

        list_page = MemorizeListPage(wordlist = word_list, wordbank = self.wordbank, title = 'Vocabs Builder.', reviewed = flag_reviewed_word, meaning = False, announce = True)
        list_page.run()

        return True
    def cmd_forgotten_words(self, args = None):
        word_idx = 0
        times_idx = 1
        familiar_idx = 2
        forgotten_idx = 3

        familiar_target = 1
        list_number = 0

        if 'familiar' in args:
            familiar_target = int(args['familiar'])

        if 'number' in args:
            list_number = int(args['number'])

        word_list = []
        for each_word in self.wordbank.quer_for_all_word(familiar = familiar_target, forgotten = True):
            if len(each_word) < 3:
                continue
            if each_word[familiar_idx] == familiar_target:
                word_list.append(each_word[word_idx])

        if list_number != 0 and list_number < len(word_list):
            word_list = word_list[-list_number:]

        random.shuffle(word_list)

        list_page = MemorizeListPage(wordlist = word_list, wordbank = self.wordbank, title = 'Forgotten Words.', meaning = True, announce = True)
        list_page.run()

        return True
    def cmd_text_input(self, args = None):
        input_lines = []
        self.__ui_print_line("Enter word list (press Enter on an empty line to finish):")
        while True:
            line = input()
            if not line:
                break
            input_lines.append(line)
        text = "\n".join(input_lines)

        # self.__ui_print_line(text)
        file_data = FileData(text)
        file_data.do_word_list(sorting = False)

        # self.__listing_word(file_data.word_list, file_data.word_counter)

        # dbg_info(f"Len of list: {len(file_data.word_list)}", file_data.word_list)
        list_page = MemorizeListPage(wordlist = file_data.word_list, wordbank = self.wordbank)

        list_page.run()

        return True
    def cmd_file_input(self, args):
        file_name = ""
        if args['#'] == 1:
            file_name = args['1']
            if file_name == "sample":
                file_name = "./data/i_have_a_dream.txt"
        else:
            self.__ui_print_line(f"Error: No file specified.")
            return False

        # read file
        if not os.path.exists(file_name):
            self.__ui_print_line(f"Error: File '{file_name}' not found.")
            return False
        # file_name = "/mnt/data/workspace/code/list_vocabulary/data/i_have_a_dream.txt"
        # self.__ui_print_line(file_name)
        file_raw = open(file_name)
        text = file_raw.read()
        file_raw.close()

        # self.__ui_print_line(text)
        file_data = FileData(text)
        file_data.do_word_list()

        # self.__listing_word(file_data.word_list, file_data.word_counter)
        list_page = MemorizeListPage(wordlist = file_data.word_list, wordbank = self.wordbank)

        list_page.run()

        return True
    def cmd_vocabs_builder_input(self, args):
        file_name = ""
        if args['#'] == 1:
            file_name = args['1']
        else:
            self.__ui_print_line(f"Error: No file specified.")
            return False

        # for koreader.
        con = sqlite3.connect(file_name)
        cur = con.cursor()
        word_list = []
        for word, prev_context, next_context in cur.execute("SELECT word, prev_context, next_context FROM vocabulary;"):
            word_list.append(word)
        con.close()

        list_page = MemorizeListPage(wordlist = word_list, wordbank = self.wordbank)

        list_page.run()
        return True
    def cmd_json_input(self, args = None):
        file_name = ""
        if args['#'] == 1:
            file_name = args['1']
        else:
            self.__ui_print_line(f"Error: No file specified.")
            return False

        # read file
        if not os.path.exists(file_name):
            self.__ui_print_line(f"Error: File '{file_name}' not found.")
            return False

        try:
            # setup customize dictionary
            self.dict_mgr.word_list_dict.cleanAll()
            self.dict_mgr.word_list_dict.buildDict(file_name)

            # # read word list.
            # file_raw = open(file_name)
            # text = file_raw.read()
            # file_raw.close()
            json_word_list = []
            with open(file_name, "r", encoding="utf-8") as jfile:
                # Load the entire JSON file as a list of entries
                data = json.load(jfile)
                for entry in data:
                    word = entry["word"]
                    json_word_list.append(word)

            list_page = MemorizeListPage(wordlist = json_word_list, wordbank = self.wordbank, title = 'Json Words.', meaning = True)
            list_page.run()

        except Exception as e:
            dbg_error(e)

            traceback_output = traceback.format_exc()
            dbg_error(traceback_output)
        finally:
            self.dict_mgr.word_list_dict.cleanAll()
        return True

#
# class EUIMode(Enum):
#     WORD = auto()
#     INTERCTIVE = auto()
#     FILE = auto()
#     LIST = auto()
#     MAX = auto()

if __name__ == '__main__':
    psettings = Settings()
    psettings.set('debug', True)
    psettings.set('database', 'debug.db')
    psettings.set('file_name', "./data/i_have_a_dream.txt")

    my_dict = SECDict()

    wordbank = WordBank()
    wordbank.db__init()
    wordbank.connect()
    my_dict = SECDict()

    test_cli = CommandLineInterface(settings = psettings, wordbank = wordbank, dictionary = my_dict)
    test_cli.ui_print_line("CLI Initailization")
    test_cli.read_file()
    # test_cli.set_mode(EUIMode.FILE)
    test_cli.set_mode(EUIMode.INTERCTIVE)
    test_cli.run()
