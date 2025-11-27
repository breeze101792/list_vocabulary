from utility.pcli import PageCommandLineInterface, PageShareData
from utility.debug import *
from dictionary.manager import Manager as DictMgr
from core.config import AppConfigManager

from plugins.pronunciation import Pronunciation
# from plugins.llm import LLM
from dictionary.hal.llm import LLM

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
        self.__flag_llm_search = False # default false

        ## reg functions
        # NOTE. currently, 3~5 is reserved.
        self.regist_key(["0", "1", "2"], self.key_rating, "Rate the familiarity of the current word.")
        self.regist_key(["h", "l"], self.key_move, "Navigate through dictionary entries.")
        self.regist_key(["s"], self.key_cmd_search, "Initiate a dictionary search.")
        self.regist_key(["L"], self.key_cmd_llm, "Search the dictionary using an LLM.")
        self.regist_key(["v"], self.key_cmd_pronounce, "Pronounce the current word.")
        self.regist_cmd("search", self.cmd_search, "Search for words in the dictionary.")
        self.regist_cmd("llm", self.cmd_llm, "Search for words using an LLM.", arg_list = ['remove', 'async', 'search', 'store', 'on', 'off'])
        self.regist_cmd("pronounce", self.cmd_pronounce, "Pronounce a specified word.")

    def refresh(self, data = None):
        self.dict_word_idx = 0
        self.dict_word_list = []
        self.check_dictionary(data.current_word)
        return self.def_content_handler(data)

    def check_dictionary(self, query_word):
        self.page_reset()
        if query_word != "":
            self.dict_word_list = self.dict_mgr.search(query_word)
            # reset dict variables.
            self.dict_word_idx = 0
            if self.dict_word_list is not None and self.dict_word_list != []:
                # self.print(f"{query_word} haven't been found in dictionary")
                # If we get words, then try llm search.
                if self.__flag_llm_search:
                    llm = LLM()
                    # Perform background search silently
                    query = llm.openai_dict(query_word, cached = True, blocking = False, notify = lambda word: self.status_print(f"Finish updating LLM for {query_word}.") )
                    # self.status_print(f"LLM search {query_word}, {query.meaning}")
                return True

        return False
    def cmd_search(self, args):
        query_word = ""
        if args["#"] >= 1 :
            query_word = args["1"]

        self.check_dictionary(query_word)
        self.share_data.current_word = query_word

        return True
    def cmd_llm(self, args = None):
        query_word = ""
        flag_cached = False
        flag_async = True
        flag_store = True
        if args is not None and args["#"] == 2 and args["1"] == "remove":
            query_word = args["2"]
            llm = LLM()
            llm.remove(query_word)

            # update words.
            if query_word == self.share_data.current_word:
                self.check_dictionary(query_word)
            return True
        elif args is not None and args["#"] >= 1 :
            query_word = args["1"]
        else:
            query_word = self.share_data.current_word

        # Default use non-cached data on search.
        if args and 'async' in args:
            flag_switch = args['async']
            if flag_switch == 'on':
                flag_async = True
            elif flag_switch == 'off':
                flag_async = False

        if args and 'store' in args:
            flag_switch = args['store']
            if flag_switch == 'on':
                flag_store = True
            elif flag_switch == 'off':
                flag_store = False
            else:
                flag_store = False
            flag_cached = False
            flag_async = False

        if args and 'search' in args:
            flag_switch = args['search']
            if flag_switch == 'on':
                self.__flag_llm_search = True
                self.status_print(f"Enable background llm dict search.")
            elif flag_switch == 'off':
                self.__flag_llm_search = False
                self.status_print(f"Disable background llm dict search.")
            return True

        llm = LLM()
        if flag_async is True:
            self.status_print(f"Search {query_word} on background.")
            llm.openai_dict(query_word, cached = flag_cached, blocking = not flag_async, store = flag_store, notify = lambda word: self.status_print(f"LLM Finishe: {word}") )
        else:
            self.dict_word_idx = 0
            self.status_print("Thinking...")

            self.dict_word_list = [llm.openai_dict(query_word, cached = flag_cached, blocking = True)]

            self.share_data.current_word = query_word
            self.status_print("")

        return True
    def cmd_pronounce(self, args = None):
        query_word = ""
        if args is not None and args["#"] >= 1 :
            query_word = args["1"]
        else:
            query_word = self.share_data.current_word

        appcgm = AppConfigManager()
        language = appcgm.get("variable.language")

        if query_word is not None and query_word != "":
            proun = Pronunciation()
            proun.speak_text(query_word, lang = language)

        return True
    def key_cmd_prefix(self, key_press, data = None, prefix = ""):
        # Save current cursor position
        self.print("\033[s", end="")
        self.set_cursor_visibility(True)

        # Get terminal size
        columns, rows = os.get_terminal_size()
        # Move cursor to the last line
        self.print(f"\033[{rows};1H", end="")

        # Clear the reset of the line.
        self.print("\033[K", end="")

        func_ret = self.command_line.run_once(prefix = prefix)
        if func_ret is False:
            self.command_buffer = f"Execute return fail. {func_ret}"

        self.set_cursor_visibility(False)
        # Restore cursor position
        self.print("\033[u", end="")

        return True
    def key_cmd_llm(self, key_press, data = None):
        # TODO, add notify message to user.
        self.cmd_llm()
        return True
    def key_cmd_pronounce(self, key_press, data = None):
        # TODO, add notify message to user.
        self.cmd_pronounce()
        return True
    def key_cmd_search(self, key_press, data = None):
        self.key_cmd_prefix(key_press, data, "search ")
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

        # currently we only set it from 0 to 2, check wordbank for related meanings.
        if int(key_press) < 0 or int(key_press) > 3:
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
            # default pronounce.
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
            self.print(f"Empty query, Enter key '?' for more help.\n")

        return True
