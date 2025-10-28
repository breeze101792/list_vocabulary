
from utility.pcli import PageCommandLineInterface, PageShareData
from utility.debug import *
from dictionary.manager import Manager as DictMgr
from plugins.page.dictpage import DictPage, DictData 

class ListPage(DictPage):
    def __init__(self, wordlist, wordbank, title = "List Words"):
        super().__init__(wordbank = wordbank, title = title)
        
        ### local vars ###
        self.word_list = wordlist
        self.word_idx = -1
        # init first word.
        dbg_error(f"len: {len(wordlist)}")
        # query_word = self.word_list[self.word_idx]
        self.share_data.current_word = ""
        # manual trigger first update.
        # self.def_content_handler()

        self.regist_key(["n", "p"], self.key_walk_list, "Rate word familiarity.")

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
