from utility.pcli import PageCommandLineInterface, PageShareData
from utility.debug import *
from dictionary.manager import Manager as DictMgr

class DictData(PageShareData):
    def __init__(self):
        self.current_word = ''
    pass

class DictPage(PageCommandLineInterface):
    def __init__(self, wordbank, title = 'Dictionary'):
        dict_data = DictData()
        super().__init__(share_data = dict_data, title = title)

        self.wordbank = wordbank
        self.dict_mgr = DictMgr()

        ## local variables
        self.dict_word_idx = 0
        self.dict_word_list = []

        ## reg functions
        self.regist_key(["0", "1", "2", "3", "4", "5"], self.key_rating, "Rate word familiarity.")
        self.regist_key(["h", "l"], self.key_move, "Navigate dictionary entries.")
        self.regist_key(["s"], self.key_cmd_search, "Search the dictionary.")
        self.regist_cmd("search", self.cmd_search, "Search the dictionary.")
    def check_dictionary(self, query_word):
        if query_word != "":
            self.dict_word_list = self.dict_mgr.search(query_word)
            # reset dict variables.
            self.dict_word_idx = 0
            if self.dict_word_list is not None and self.dict_word_list != []:
                # self.print(f"{query_word} haven't been found in dictionary")
                return True
        return False
    def cmd_search(self, args):
        query_word = ""
        if args["#"] >= 1 :
            query_word = args["1"]

        ## Dictionary query.
        # if self.check_dictionary(query_word):
        #     self.share_data.current_word = query_word
        # else:
        #     self.share_data.current_word = ""
        self.check_dictionary(query_word)
        self.share_data.current_word = query_word

        return True
    def key_cmd_search(self, key_press, data = None):
        # Save current cursor position
        self.print("\033[s", end="")
        self.set_cursor_visibility(True)

        # Get terminal size
        columns, rows = os.get_terminal_size()
        # Move cursor to the last line
        self.print(f"\033[{rows};1H", end="")

        # Clear the reset of the line.
        self.print("\033[K", end="")

        func_ret = self.command_line.run_once(prefix = "search ")
        if func_ret is False:
            self.command_buffer = f"Execute return fail. {func_ret}"

        self.set_cursor_visibility(False)
        # Restore cursor position
        self.print("\033[u", end="")

        return True
    def key_move(self, key_press, data = None):
        if key_press in ("h"):
            if self.dict_word_idx > 0:
                self.dict_word_idx -= 1
        elif key_press in ("l"):
            if self.dict_word_idx + 1 < len(self.dict_word_list):
                self.dict_word_idx += 1
        return True
    def key_rating(self, key_press, data = None):
        word = self.share_data.current_word
        if len(self.dict_word_list) == 0 or word == '':
            # dbg_warning('Word not found on the dictionary, anction ignored.')
            return False

        if not self.wordbank.update_familiar(word, int(key_press)):
            self.wordbank.insert(word, familiar = int(key_press))
        self.wordbank.commit()
        # self.__ui_print_line("Set {} to {}".format(word,int(key_press)))

        return True

    def def_status_handler(self, data = None):
        if self.dict_word_list != None and len(self.dict_word_list) > 0 and self.dict_word_idx >= 0 and self.dict_word_idx < len(self.dict_word_list):
            status_left = f"Page: {self.dict_word_idx + 1}/{len(self.dict_word_list)}, {self.dict_word_list[self.dict_word_idx].dict_name} "
        else:
            status_left = f"Page: 0/0 "
        status_middle = f"{self.share_data.current_word}"
        status_right = f" "
        # tupple (left, middle, right)
        return (status_left,status_middle,status_right)

    def def_content_handler(self, data = None):

        word = self.share_data.current_word
        if len(self.dict_word_list) > 0:

            familiar = 0
            times = 0
            timestamp = 0
            word_info = self.wordbank.get_word(word)
            # # times, familiar, timestamp = self.wordbank.get_word(word)
            if word_info and len(word_info) != 0:
                times = self.wordbank.get_word(word)[0]
                familiar = self.wordbank.get_word(word)[1]
                timestamp = self.wordbank.get_word(word)[2]
                self.print(f"Query Word: {word}, familiar:{familiar}, times:{times}\n")
            else:
                self.print(f"Query Word: {word}\n")

            self.dict_word_list[self.dict_word_idx].show_meaning()
        elif word != "":
            self.print(f"'{word}' not found\n")
        else:
            self.print(f"Empty query, you could search with key '?' for hlep.\n")

        return True
