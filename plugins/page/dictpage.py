from utility.pcli import PageCommandLineInterface, PageShareData
from utility.debug import *
from dictionary.manager import Manager as DictMgr

class DictData(PageShareData):
    def __init__(self):
        self.current_word = ''
    pass

class DictPage(PageCommandLineInterface):
    def __init__(self, wordbank):
        dict_data = DictData()
        super().__init__(share_data = dict_data)

        self.wordbank = wordbank
        self.dict_mgr = DictMgr()

        ## local variables
        self.dict_word_idx = 0
        self.dict_word_idx = 0
        self.dict_word_list = []

        ## reg functions
        self.regist_key(["h", "l"], self.key_move, "Selecte dictionary.")
    def key_move(self, key_press, data = None):
        if key_press in ("h"):
            if self.dict_word_idx > 0:
                self.dict_word_idx -= 1
        elif key_press in ("l"):
            if self.dict_word_idx + 1 < len(self.dict_word_list):
                self.dict_word_idx += 1
        return True

    def def_content_handler(self, data = None):
        # query_word = input("Searching Word: ")
        query_word = self.command_buffer
        self.command_buffer = ""

        ## Dictionary query.
        if query_word != "":
            self.dict_word_list = self.dict_mgr.search(query_word)
            # reset dict variables.
            self.dict_word_idx = 0
            if self.dict_word_list == []:
                dbg_warning("The word haven't been found in dictionary")
            # else:
            #     self.dict_word_list[self.dict_word_idx].show_meaning()
        if len(self.dict_word_list) > 0:
            self.dict_word_list[self.dict_word_idx].show_meaning()
            self.print(f"\nPage: {self.dict_word_idx + 1}/{len(self.dict_word_list)}, {self.dict_word_list[self.dict_word_idx].dict_name}")

        self.share_data.current_word = query_word

        ## Debug.
        # self.print(f"key_move: {self.dict_word_idx}")

        return True
