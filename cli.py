from enum import Enum, auto
import threading
from utils import getch
import time
from debug import *
from ecdict import *
from settings import Settings
from wordbank import WordBank
import settings
import subprocess as sp
from data import FileData

class EUIMode(Enum):
    WORD = auto()
    INTERCTIVE = auto()
    FILE = auto()
    LIST = auto()
    MAX = auto()

class CommandLineInterface:
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
        else:
            self.ui_print_line()
        self.ui_print_line("---------------------------------------------------")
        if dict_word:
            dict_word.show_meaning()
        self.ui_print_line("---------------------------------------------------")
        return dict_word
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

            # operations
            while self.__flag_running == True and self.__mode != EUIMode.WORD:
                self.ui_print_line("Enter a key(x/Exit, n/Next, P/Previous, s/Searching):")
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
