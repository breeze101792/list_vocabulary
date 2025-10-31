
import time
from utility.pcli import PageCommandLineInterface, PageShareData
from utility.debug import *
from dictionary.manager import Manager as DictMgr
from dictionary.word import PureWord
from plugins.page.dictpage import DictPage, DictData 

class ListPage(DictPage):
    def __init__(self, wordlist, wordbank, title = "List Words"):
        super().__init__(wordbank = wordbank, title = title)

        ### local vars ###
        self.word_list = wordlist
        self.word_idx = -1
        # init first word.
        # dbg_error(f"len: {len(wordlist)}")
        # query_word = self.word_list[self.word_idx]
        self.share_data.current_word = ""
        # manual trigger first update.
        # self.def_content_handler()

        self.regist_key(["n", "p"], self.key_walk_list, "Walk through the word list.")

    def def_status_handler(self, data = None):
        if self.dict_word_list != None and len(self.dict_word_list) > 0 and self.dict_word_idx >= 0 and self.dict_word_idx < len(self.dict_word_list):
            status_left = f"Page: {self.dict_word_idx + 1}/{len(self.dict_word_list)}, {self.dict_word_list[self.dict_word_idx].dict_name} "
        else:
            status_left = f"Page: 0/0 "
        status_middle = f"{self.share_data.current_word}"
        status_right = f"{self.word_idx + 1}/{len(self.word_list)} "
        # tupple (left, right)
        return (status_left,status_middle, status_right)

    def refresh(self, data = None):
        self.dict_word_list = []
        return self.def_content_handler(data)

    def key_walk_list(self, key_press, data = None):
        # move index
        if key_press in ("n"):
            self.word_idx += 1
        elif key_press in ("p"):
            self.word_idx -= 1

        # check index
        if self.word_idx > len(self.word_list) - 1:
            self.word_idx = len(self.word_list) - 1
        elif self.word_idx == -1:
            self.word_idx = 0

        # choose words by index.
        query_word = self.word_list[self.word_idx]
        self.check_dictionary(query_word)

        self.share_data.current_word = query_word
        return True

class NewWordListPage(ListPage):
    def __init__(self, wordlist, wordbank, title = "List Words"):
        super().__init__(wordlist = wordlist, wordbank = wordbank, title = title)
        
        ### control vars ###
        self.__flag_ignore_knowing_words = True

        # ### local vars ###
        # self.word_list = wordlist
        # self.word_idx = -1
        # # init first word.
        # # dbg_error(f"len: {len(wordlist)}")
        # # query_word = self.word_list[self.word_idx]
        # self.share_data.current_word = ""
        # # manual trigger first update.
        # # self.def_content_handler()
        #
        # self.regist_key(["n", "p"], self.key_walk_list, "Walk through the word list.")
        self.regist_cmd("ignore", self.cmd_ignore_knowing_words, "Control to show knowing words or not.", arg_list = ["on", "off"])


    def cmd_ignore_knowing_words(self, args):
        query_word = ""
        if args["#"] >= 1 :
            flag_switch = args["1"]
            if flag_switch == 'on':
                self.__flag_ignore_knowing_words = True
            elif flag_switch == 'off':
                self.__flag_ignore_knowing_words = False

        # refresh words
        return self.key_walk_list(key_press = key_press)

    def key_walk_list(self, key_press, data = None):
        # move index
        if key_press in ("n"):
            self.word_idx += 1
        elif key_press in ("p"):
            self.word_idx -= 1

        # check index
        # if self.word_idx > len(self.word_list) - 1:
        #     self.word_idx = len(self.word_list) - 1
        # elif self.word_idx == -1:
        #     self.word_idx = 0
        while True:
            # check index
            if self.word_idx > len(self.word_list) - 1:
                self.word_idx = len(self.word_list) - 1
                # don't jump if touch boundary.
                break
            elif self.word_idx == -1:
                self.word_idx = 0
                # don't jump if touch boundary.
                break

            word = self.word_list[self.word_idx]
            # check words.
            familiar = 0
            times = 0
            timestamp = 0
            word_info = self.wordbank.get_word(word)
            if word_info and len(word_info) != 0:
                times = self.wordbank.get_word(word)[0]
                familiar = self.wordbank.get_word(word)[1]
                timestamp = self.wordbank.get_word(word)[2]

            if self.__flag_ignore_knowing_words is True and familiar > 0:
                # print(familiar , familiar_filter, key_press)
                if key_press in ("n"):
                    self.word_idx += 1
                elif key_press in ("p"):
                    self.word_idx -= 1
                else:
                    # default go to next one.
                    self.word_idx += 1
                continue
            else:
                # found one.
                break

        # choose words by index.
        query_word = self.word_list[self.word_idx]

        # choose words by index.
        query_word = self.word_list[self.word_idx]
        self.check_dictionary(query_word)

        self.share_data.current_word = query_word
        return True

class MemoryListPage(ListPage):
    def __init__(self, wordlist, wordbank, title = "List Words"):
        super().__init__(wordlist = wordlist, wordbank = wordbank, title = title)
        
        ### control vars ###
        self.__flag_show_meaning = False
        self.__flag_ignore_memorized_words = True

        # ### local vars ###
        # self.word_list = wordlist
        # self.word_idx = -1
        # # init first word.
        # # dbg_error(f"len: {len(wordlist)}")
        # # query_word = self.word_list[self.word_idx]
        # self.share_data.current_word = ""
        # # manual trigger first update.
        # # self.def_content_handler()
        #
        # self.regist_key(["n", "p"], self.key_walk_list, "Rate word familiarity.")
        self.regist_key(["f", "d"], self.key_familiar, "Mark word is familiar or not.")
        self.regist_key(["m"], self.key_show_meanings, "Showing meanings.")

        self.regist_cmd("meanings", self.cmd_meaning, "Set whether to show meanings.", arg_list = ["on", "off"])
        self.regist_cmd("ignore", self.cmd_ignore_meorized_words, "Control to show memorized words or not.", arg_list = ["on", "off"])

    def cmd_meaning(self, args):
        query_word = ""
        if args["#"] >= 1 :
            flag_switch = args["1"]
            if flag_switch == 'on':
                self.__flag_show_meaning = True
            elif flag_switch == 'off':
                self.__flag_show_meaning = False


        # refresh words
        return self.key_walk_list(key_press = key_press)
    def cmd_ignore_meorized_words(self, args):
        query_word = ""
        if args["#"] >= 1 :
            flag_switch = args["1"]
            if flag_switch == 'on':
                self.__flag_ignore_memorized_words = True
            elif flag_switch == 'off':
                self.__flag_ignore_memorized_words = False

        # refresh words
        return self.key_walk_list(key_press = key_press)


    def key_show_meanings(self, key_press, data = None):
        # choose words by index.
        query_word = self.word_list[self.word_idx]
        self.check_dictionary(query_word)
        return True

    def key_familiar(self, key_press, data = None):

        if len(self.dict_word_list) == 0 or self.share_data.current_word == "":
            dbg_warning('Word not found on the dictionary, anction ignored.')
            return False

        word = self.share_data.current_word
        familiar_index = 1
        if key_press == 'f':
            isFamiliar = True
        else:
            isFamiliar = False

        if not self.wordbank.update_and_mark_familiar(word, isFamiliar):
            self.wordbank.insert(word, familiar = int(familiar_index))
        self.wordbank.commit()

        # move to next word.
        self.word_idx += 1
        return self.key_walk_list(key_press = key_press)

    def key_walk_list(self, key_press, data = None):
        # check if list is empty or not.
        if len(self.word_list) == 0:
            dbg_warning("Now words on the list.")
            return False

        # move index
        if key_press in ("n"):
            self.word_idx += 1
        elif key_press in ("p"):
            self.word_idx -= 1

        while True and len(self.word_list) != 0:
            # check index
            if self.word_idx > len(self.word_list) - 1:
                self.word_idx = len(self.word_list) - 1
                # don't jump if touch boundary.
                break
            elif self.word_idx == -1:
                self.word_idx = 0
                # don't jump if touch boundary.
                break

            word = self.word_list[self.word_idx]
            # check words.
            familiar = 0
            times = 0
            timestamp = 0
            word_info = self.wordbank.get_word(word)
            if word_info and len(word_info) != 0:
                times = self.wordbank.get_word(word)[0]
                familiar = self.wordbank.get_word(word)[1]
                timestamp = self.wordbank.get_word(word)[2]

            if self.__flag_ignore_memorized_words is True and datetime.fromtimestamp(timestamp).date() == datetime.now().date():
                # print(familiar , familiar_filter, key_press)
                if key_press in ("n"):
                    self.word_idx += 1
                elif key_press in ("p"):
                    self.word_idx -= 1
                else:
                    # default go to next one.
                    self.word_idx += 1
                continue
            else:
                # found one.
                break

        # choose words by index.
        query_word = self.word_list[self.word_idx]

        if self.__flag_show_meaning:
            self.check_dictionary(query_word)
        else:
            self.dict_word_idx = 0
            mock_word = PureWord(word = query_word, dict_name = "Vocabs builder")
            self.dict_word_list = [mock_word]

        self.share_data.current_word = query_word
        return True
