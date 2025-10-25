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
        self.regist_key(["s"], self.key_cmd_search, "Search dictionary.")
        self.regist_cmd("search", self.cmd_search, "Search dictionary.")
    def cmd_search(self, args):
        query_word = ""
        if args["#"] >= 1 :
            query_word = args["1"]

        ## Dictionary query.
        if query_word != "":
            self.dict_word_list = self.dict_mgr.search(query_word)
            # reset dict variables.
            self.dict_word_idx = 0
            if self.dict_word_list == []:
                # dbg_warning("The word haven't been found in dictionary")
                self.print(f"{query_word} haven't been found in dictionary")

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

    def def_content_handler(self, data = None):

        if len(self.dict_word_list) > 0:
            self.dict_word_list[self.dict_word_idx].show_meaning()
            self.print(f"\nPage: {self.dict_word_idx + 1}/{len(self.dict_word_list)}, {self.dict_word_list[self.dict_word_idx].dict_name}")

        return True
