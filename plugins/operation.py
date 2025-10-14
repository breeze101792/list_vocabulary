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

            word_info = self.wordbank.get_word(word)
            if len(word_info) == 2:
                familiar = self.wordbank.get_word(word)[1]

            # cls
            print('\x1bc')
            self.__ui_print_line("Word:{}, Familiar:{}, Count:{}".format(word, familiar,counter))
            self.search({'arg_0': 'file', 'arg_1': word})
            self.__ui_print_line("Enter a key(x:Exit, n/l:Next, p/h:Previous):")
            while True:

                key_press = getch()
                time.sleep(key_delay)

                if key_press in ("n", "N") or key_press in ("l"):
                    word_idx += 1
                    break
                elif key_press in ("p", "P") or key_press in ("h"):
                    word_idx -= 1
                    break
                elif key_press in ("m"):
                    if word_idx + 1 < len(word_list):
                        next_word = word_list[word_idx + 1]
                        self.__ui_print_line("Next Word: {}".format(next_word))
                    else:
                        self.__ui_print_line("End of list.")
                    continue
                elif key_press in ("x", "X") or key_press == chr(0x04):
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

                elif key_press == chr(0x0c):
                    # ctrl + l
                    break
                else:
                    print("Unknown key>" + key_press)
                    continue
    # FIXME, unify function with listing_word
    def dictionary_search(self, args):
        key_delay=0.01

        word = ""
        while True:

            if word != "":
                # cls
                print('\x1bc')
                self.__ui_print_line("File List. Word:{}".format(word))
                self.search({'arg_0': 'file', 'arg_1': word})
            self.__ui_print_line("Enter a key(x:Exit, n/l:Next, p/h:Previous):")
            while True:

                key_press = getch()
                time.sleep(key_delay)

                if key_press in ("x", "X") or key_press == chr(0x04):
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
                else:
                    print("Unknown key>" + key_press)
                    continue
    def vocabulary_memorize(self, args):
        word_idx = 0
        familiar_idx = 2

        familiar_target = 1

        word_list = []
        for each_word in self.wordbank.quer_for_all_word():
            if len(each_word) != 3:
                continue
            if each_word[familiar_idx] == familiar_target:
                word_list.append(each_word[word_idx])

        random.shuffle(word_list)
        self.__listing_word(word_list)

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
        # if filter_flag and self.__filter(query_word, db_word) == False:
        #     dbg_info("The word has been blocked by filter")
        #     return False
        # dbg_info(db_word)

        # show information
        # self.__ui_print("{} ".format(query_word))
        # if self.__file_data is not None and self.__file_data.get_word_freq(query_word):
        #     self.__ui_print(" +{}/{}".format(len(self.__word_list) - self.__list_idx, self.__file_data.get_word_freq(query_word)))
        # if db_word:
        #     self.__ui_print_line(" (times: {}, familiar: {})".format(db_word[0], db_word[1]))
        #     self.__statistic_list[int(db_word[1])] += 1
        # else:
        #     self.__ui_print_line()
        #     self.__statistic_list[0] += 1

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
        self.wordbank.dump_table("WORD")

        return True

    def file(self, args):
        dict_word=None

        arg_dict = args
        arg_key = list(arg_dict.keys())

        # self.__ui_print_line(args)

        # read file
        file_name = arg_dict[arg_key[1]]
        # file_name = "/mnt/data/workspace/code/list_vocabulary/data/i_have_a_dream.txt"
        # self.__ui_print_line(file_name)
        file_raw = open(file_name)
        text = file_raw.read()
        file_raw.close()

        # self.__ui_print_line(text)
        file_data = FileData(text)
        file_data.do_word_list()

        # self.__ui_print_line(file_data.word_list)
        # self.__ui_print_line(file_data.word_counter)
        # word_len = len(file_data.word_list)

        self.__listing_word(file_data.word_list, file_data.word_counter)

        return True

class EUIMode(Enum):
    WORD = auto()
    INTERCTIVE = auto()
    FILE = auto()
    LIST = auto()
    MAX = auto()

class Operation_legacy:
    def __init__(self, settings = None, wordbank = None, dictionary = None):
        self.settings = settings
        self.wordbank = wordbank
        self.dictionary = dictionary

        #### control vars ###
        self.__flag_running = True
        # 0.5 ms
        self.__key_delay = 0.05

        ### local vars ###
        self.__mode = EUIMode.FILE
        self.__word_list = None
        self.__list_idx = 0
        self.__file_data = None
        self.__filter_level = [0,1,2,3,4,5]
        self.__filter_freq = 0
        # counter for all levels, 0 for not in the db
        self.__statistic_list = [0,0,0,0,0,0]
        self.__statistic_flag = False

    def set_filter(self, level = None, freq = None):
        if level is not None:
            self.__filter_level = level
        if freq is not None:
            self.__filter_freq = freq

    def set_mode(self, mode):
        self.__mode = mode
    def set_list(self, word_list):
        self.__word_list = word_list
    def read_file(self):
        f = open(self.settings.get('file_name'))
        text = f.read()
        f.close()
        self.__file_data = FileData(text)
        self.__file_data.do_word_list()

        self.__word_list = self.__file_data.get_word_list()

    def ui_print(self, *args):
        print("".join(map(str,args)), end="")
    def ui_print_line(self, *args):
        print("".join(map(str,args)))
    def start_thread(self):
        x = threading.Thread(target=self.key_press, args=(0,))
        x.start()
        self.ui_print_line("End of init key thread")
    def __filter(self, query_word, db_word):
        filter_flag = True
        if self.__file_data != None and self.__file_data.get_word_freq(query_word) < self.__filter_freq:
            filter_flag = filter_flag and False
        dbg_debug(query_word, db_word,db_word != False)
        if db_word != False:
            if db_word[1] not in self.__filter_level:
                filter_flag = filter_flag and False
                dbg_debug("db_true:", filter_flag)
            dbg_debug("db_true:", filter_flag, self.__filter_level)
        else:
            # see if it is lelve 0
            if 0 not in self.__filter_level:
                filter_flag = filter_flag and False
                dbg_debug("db_false:", filter_flag)
            dbg_debug("db_false:", filter_flag, self.__filter_level)
        return filter_flag
    def __get_word(self, mode):
        next_word = ""
        # this function handle word list
        if mode == EUIMode.INTERCTIVE:
            next_word = input(self.settings.get('name').__str__() + "> ").strip()
        elif mode == EUIMode.FILE or mode == EUIMode.LIST or mode == EUIMode.WORD:
            if self.__list_idx >= len(self.__word_list) or self.__list_idx < 0:
                return False
            else:
                next_word = self.__word_list[self.__list_idx]
        return next_word
    def __search_word(self, query_word, filter_flag = True):
        # searching in dictionary
        dict_word = self.dictionary.search(query_word)
        if dict_word == False:
            dbg_warning("The word haven't been found in dictionary")
            return False
        # searching in databas
        db_word = self.wordbank.get_word(query_word)
        if filter_flag and self.__filter(query_word, db_word) == False:
            dbg_info("The word has been blocked by filter")
            return False

        # show information
        self.ui_print("{} ".format(query_word))
        if self.__file_data is not None and self.__file_data.get_word_freq(query_word):
            self.ui_print(" +{}/{}".format(len(self.__word_list) - self.__list_idx, self.__file_data.get_word_freq(query_word)))
        if db_word:
            self.ui_print_line(" (times: {}, familiar: {})".format(db_word[0], db_word[1]))
            self.__statistic_list[int(db_word[1])] += 1
        else:
            self.ui_print_line()
            self.__statistic_list[0] += 1
        self.ui_print_line("---------------------------------------------------")
        if dict_word:
            dict_word.show_meaning()
        self.ui_print_line("---------------------------------------------------")
        return dict_word
    def search(self, args):
        func_ret=None
        # dbg_trace(args)
        # arg_dict = ArgParser.args_parser(args)
        arg_dict = args
        arg_key = list(arg_dict.keys())

        # print(arg_dict[arg_key[0]])
        func_ret = self.__search_word(arg_dict[arg_key[0]])
        if func_ret is False:
            self.ui_print_line('No such word.')
            return False
        else:
            return True

    def run(self):
        while self.__flag_running == True:
            # clean screen
            sp.call('clear',shell=False)
            # get next word
            query_word = self.__get_word(self.__mode)
            if query_word == False:
                self.__flag_running == False
                break
            dict_word = self.__search_word(query_word)
            if dict_word == False and (self.__mode == EUIMode.FILE or self.__mode == EUIMode.LIST):
                self.__word_list.remove(self.__word_list[self.__list_idx])
                continue
            if self.__mode == EUIMode.WORD:
                return
            if self.__statistic_flag:
                self.__list_idx += 1
                continue

            # operations
            while self.__flag_running == True and self.__mode != EUIMode.WORD:
                self.ui_print_line("Enter a key(x/Exit, n/Next, P/Previous, s/Searching, num/Grading):")
                key_press = getch()
                time.sleep(self.__key_delay)
                if key_press in ("q", "Q", "x", "X"):
                    self.ui_print_line(self.settings.get('msg_exit'))
                    self.__flag_running = False
                elif key_press in ("d", "D"):
                    self.ui_print_line("Save to database")
                    self.wordbank.commit()
                    continue
                elif key_press in ("s", "S"):
                    if self.__mode == EUIMode.INTERCTIVE:
                        break
                    tmp_word = self.__get_word(EUIMode.INTERCTIVE)
                    self.__search_word(tmp_word, filter_flag = False)
                    continue
                elif key_press in ("n", "N"):
                    self.__list_idx += 1
                    break
                elif key_press in ("p", "P"):
                    self.__list_idx -= 1
                    break
                elif key_press in ("1", "2", "3", "4", "5"):
                    if not self.wordbank.update_familiar(dict_word.word, int(key_press)):
                        self.wordbank.insert(dict_word.word, int(key_press))
                    self.wordbank.commit()
                    self.__list_idx += 1
                    if self.__mode == EUIMode.INTERCTIVE:
                        # clean screen
                        sp.call('clear',shell=False)
                        self.__search_word(query_word)
                        continue
                    else:
                        break
                elif key_press in ("b", "B"):
                    break
                else:
                    print("Unknown key>" + key_press)
                    continue
        self.ui_print_line("Statistic: ", self.__statistic_list)
    def key_press(self, test):
        while True:
            x_tmp = getch()
            self.ui_print_line("KeyPress: {}".format(x_tmp))
            time.sleep(0.05)
            if x_tmp in ("q", "Q", "x", "X"):
                # self.ui_print_line(psettings.get('msg_exit'))
                return


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
