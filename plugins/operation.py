from enum import Enum, auto
import random
import threading
import time
import subprocess as sp

from utility.utils import getch
from utility.debug import *

from dictionary.hal.ecdict import *

from core.settings import Settings
from core.wordbank import WordBank
from core.settings import Settings
from core.data import FileData

class Operation:
    def __init__(self, settings = None, wordbank = None, dictionary = None):
        # self.settings = settings
        self.wordbank = wordbank
        self.dictionary = dictionary

        ### local vars ###
        # self.__mode = EUIMode.FILE
        # self.__word_list = None
        # self.__list_idx = 0
        # self.__file_data = None
        # self.__filter_level = [0,1,2,3,4,5]
        # self.__filter_freq = 0

        # counter for all levels, 0 for not in the db
        # self.__statistic_list = [0,0,0,0,0,0]
        # self.__statistic_flag = False

        ## Familiar Level
        # 0: do not need to remember it. too easy or useless word.
        # 1. New word need to memorize it.
        # 2. Memorize words or easy-remembered words, but still need to review again.
        # 3. Words that already memorized.

    def __ui_print(self, *args):
        print("".join(map(str,args)), end="")
    def __ui_print_line(self, *args):
        print("".join(map(str,args)))

    def __listing_word(self, word_list = [], word_counter = []):
        word_idx = 0
        key_delay=0.01
        while True:
            if word_idx > len(word_list) - 1:
                word_idx = len(word_list) - 1
            elif word_idx == -1:
                word_idx = 0

            word = word_list[word_idx]
            if len(word_counter) == len(word_list):
                counter = word_counter[word_idx]
            else:
                counter = 0

            familiar = 0
            word_info = self.wordbank.get_word(word)
            if word_info and len(word_info) == 2:
                familiar = self.wordbank.get_word(word)[1]

            # cls
            print('\x1bc')
            self.__ui_print_line("== Listing words. ==")
            self.__ui_print_line("== Word:{}, Familiar:{}, Count:{} ==\n".format(word, familiar,counter))
            self.search({'arg_0': 'file', 'arg_1': word})
            self.__ui_print_line("Enter a key(q:Exit, j:Next, k:Previous, f:Familiar, n:New words, 0-5:Grade, ::Search):")
            while True:

                key_press = getch()
                time.sleep(key_delay)

                if key_press in ("j"):
                    word_idx += 1
                    break
                elif key_press in ("k"):
                    word_idx -= 1
                    break
                elif key_press in ("q", "Q") or key_press == chr(0x04):
                    # ctrl + d
                    return True
                elif key_press in ("f"):
                    familiar_index = 2
                    if not self.wordbank.update_familiar(word, int(familiar_index)):
                        self.wordbank.insert(word, int(familiar_index))
                    self.wordbank.commit()
                    word_idx += 1
                    break
                elif key_press in ("n"):
                    memorize_index = 1
                    if not self.wordbank.update_familiar(word, int(memorize_index)):
                        self.wordbank.insert(word, int(memorize_index))
                    self.wordbank.commit()
                    word_idx += 1
                    break
                elif key_press in ("0"):
                    if self.wordbank.update_familiar(word, int(key_press)):
                        self.wordbank.commit()
                        self.__ui_print_line("Remove {} from list".format(word))

                elif key_press in ("1", "2", "3", "4", "5"):
                    if not self.wordbank.update_familiar(word, int(key_press)):
                        self.wordbank.insert(word, int(key_press))
                    self.wordbank.commit()
                    self.__ui_print_line("Set {} to {}".format(word,int(key_press)))
                elif key_press in (":"):
                    self.__ui_print_line("\n== Enter Dictionary ==")
                    self.__ui_print_line("=====================================")
                    word = input("Searching Word: ")
                    self.dictionary_search(word = word, clear = False)
                    print('\x1bc')
                    break

                elif key_press == chr(0x0c):
                    # ctrl + l
                    break
                # else:
                #     print("Unknown key>" + key_press)
                #     continue
    def __memorize_list(self, word_list = []):
        word_idx = 0
        key_delay=0.01
        meaning_showed = False
        while True:
            if word_idx > len(word_list) - 1:
                word_idx = len(word_list) - 1
            elif word_idx == -1:
                word_idx = 0

            word = word_list[word_idx]

            familiar = 0
            word_info = self.wordbank.get_word(word)
            if word_info and len(word_info) == 2:
                familiar = self.wordbank.get_word(word)[1]

            # cls
            print('\x1bc')
            self.__ui_print_line("== Memorize words. ==")
            self.__ui_print_line("=> Word:{}, Familiar:{}".format(word, familiar))
            if meaning_showed is True:
                self.search({'arg_0': 'file', 'arg_1': word})

            self.__ui_print_line("Enter a key(q:Exit, j:Next, k:Previous, m:Show meaning, M: Default show meanings, 0-5:Grade, ::Search):")

            tmp_meaning_showed = meaning_showed
            while True:
                key_press = getch()
                time.sleep(key_delay)

                if key_press in ("j"):
                    word_idx += 1
                    break
                elif key_press in ("k"):
                    word_idx -= 1
                    break
                elif key_press in ("M"):
                    meaning_showed = not meaning_showed
                    break
                elif key_press in ("m") and tmp_meaning_showed is False:
                    tmp_meaning_showed = True
                    self.__ui_print_line("")
                    self.search({'arg_0': 'file', 'arg_1': word})
                    continue
                elif key_press in ("q", "Q") or key_press == chr(0x04):
                    # ctrl + d
                    return True
                elif key_press in ("0"):
                    if self.wordbank.update_familiar(word, int(key_press)):
                        self.wordbank.commit()
                        self.__ui_print_line("Remove {} from list".format(word))

                elif key_press in ("1", "2", "3", "4", "5"):
                    if not self.wordbank.update_familiar(word, int(key_press)):
                        self.wordbank.insert(word, int(key_press))
                    self.wordbank.commit()
                    self.__ui_print_line("Set {} to {}".format(word,int(key_press)))
                elif key_press in (":"):
                    self.__ui_print_line("\n== Enter Dictionary ==")
                    self.__ui_print_line("=====================================")
                    word = input("Searching Word: ")
                    self.dictionary_search(word = word, clear = False)
                    print('\x1bc')
                    break

                elif key_press == chr(0x0c):
                    # ctrl + l
                    break
                # else:
                #     print("Unknown key>" + key_press)
                #     continue
    # FIXME, unify function with listing_word
    def dictionary_search(self, args = None, word = "", clear = True):
        key_delay=0.01

        self.__ui_print("== Dictionary Search ==")
        while True:

            if word != "":
                # cls
                if clear:
                    print('\x1bc')
                    self.__ui_print_line("== Dictionary Search ==\n")
                else:
                    print("\n")
                # self.__ui_print_line("File List. Word:{}".format(word))
                self.search({'arg_0': 'file', 'arg_1': word})
            self.__ui_print_line("Enter a key(q:Exit, 0-5:Grade, ::Search):")
            while True:

                key_press = getch()
                time.sleep(key_delay)

                if key_press in ("q", "Q") or key_press == chr(0x04):
                    # ctrl + d
                    return True
                elif key_press in ("0"):
                    if self.wordbank.update_familiar(word, int(key_press)):
                        self.wordbank.commit()
                        self.__ui_print_line("Remove {} from list".format(word))

                elif key_press in ("1", "2", "3", "4", "5"):
                    if not self.wordbank.update_familiar(word, int(key_press)):
                        self.wordbank.insert(word, int(key_press))
                    self.wordbank.commit()
                    self.__ui_print_line("Set {} to {}".format(word,int(key_press)))
                elif key_press in (":"):
                    word = input("Searching Word: ")
                    break

                elif key_press == chr(0x0c):
                    # ctrl + l
                    break
                # else:
                #     print("Unknown key>" + key_press)
                #     continue
        return False
    def vocabulary_memorize(self, args):
        word_idx = 0
        familiar_idx = 2

        familiar_target = 1
        if args["#"] == 1 and args["1"] and args["1"].isdigit():
            familiar_target = int(args["1"])
        dbg_info("Change familiar level to {}.".format(familiar_target))

        word_list = []
        for each_word in self.wordbank.quer_for_all_word():
            if len(each_word) != 3:
                continue
            if each_word[familiar_idx] == familiar_target:
                word_list.append(each_word[word_idx])

        random.shuffle(word_list)
        self.__memorize_list(word_list)

        return True
    def __fuzzy_search(self, query_word, filter_flag = True):
        # searching in dictionary
        word_list = self.dictionary.fuzzySearch(query_word)
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
        dict_word = self.dictionary.search(query_word)
        if dict_word == False:
            dbg_warning("The word haven't been found in dictionary")
            return False
        # searching in databas
        db_word = self.wordbank.get_word(query_word)

        if dict_word:
            # dict_word.show_meaning()
            return dict_word
        else:
            return False

    def def_search(self, args):

        dict_word=None
        # dbg_trace(args)
        # arg_dict = ArgParser.args_parser(args)
        arg_dict = args
        arg_key = list(arg_dict.keys())

        # print(arg_dict[arg_key[0]])
        dict_word = self.__search_word(arg_dict[arg_key[0]])
        if dict_word is False:
            word_list = self.__fuzzy_search(arg_dict[arg_key[0]])
            if word_list is False:
                return False
            else:
                self.__ui_print_line(word_list)
            # self.__ui_print_line('No such word.')
        else:
            dict_word.show_meaning()
            self.wordbank.update(dict_word.word)
            return True
    def search(self, args):

        dict_word=None
        # dbg_trace(args)
        # arg_dict = ArgParser.args_parser(args)
        arg_dict = args
        arg_key = list(arg_dict.keys())

        # print(arg_dict[arg_key[0]])
        dict_word = self.__search_word(arg_dict[arg_key[1]])
        if dict_word is False:
            word_list = self.__fuzzy_search(arg_dict[arg_key[1]])
            if word_list is False:
                return False
            else:
                self.__ui_print_line(word_list)
            # self.__ui_print_line('No such word.')
        else:
            dict_word.show_meaning()
            self.wordbank.update(dict_word.word)
            return True
    def fuzzy(self, args):
        dict_word=None
        # dbg_trace(args)
        # arg_dict = ArgParser.args_parser(args)
        arg_dict = args
        arg_key = list(arg_dict.keys())

        # print(arg_dict[arg_key[0]])
        word_list = self.__fuzzy_search(arg_dict[arg_key[1]])
        dbg_debug('word list: ', word_list)
        if word_list is False:
            self.__ui_print_line('No such word.')
            return False
        else:
            self.__ui_print_line(word_list)
            return True
    def vocabulary(self, args):
        dict_word=None

        arg_dict = args
        arg_key = list(arg_dict.keys())

        word_list = self.wordbank.quer_for_all_word()
        for each_word in word_list:
            self.__ui_print_line(each_word)
        # dbg_info(word_list)
        # self.wordbank.dump_table("WORD")

        return True

    def file(self, args):
        dict_word=None

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

        self.__listing_word(file_data.word_list, file_data.word_counter)

        return True

    def textfile(self, args):
        dict_word=None


        input_lines = []
        self.__ui_print_line("Enter word list (press Enter on an empty line to finish):")
        while True:
            line = input()
            if not line:
                break
            input_lines.append(line)
        text = "\n".join(input_lines)

        self.__ui_print_line(text)
        file_data = FileData(text)
        file_data.do_word_list(sorting = False)

        self.__listing_word(file_data.word_list, file_data.word_counter)

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
