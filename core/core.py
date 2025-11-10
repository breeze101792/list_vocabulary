from utility.cli import CommandLineInterface
from plugins.operation import *
from core.config import AppConfigManager
from dictionary.manager import Manager as DictMgr

class Core(CommandLineInterface):
    def __init__(self, promote='PYD'):
        appcgm = AppConfigManager()

        wellcome_message = "Hi, enjoy learning " + appcgm.get('variable.language')
        super().__init__(promote, wellcome_message = wellcome_message)

        # pre init.

        dict_mgr = DictMgr()

        self.wordbank = WordBank()
        self.wordbank.connect()
        self.wordbank.setup()
        # TODO, remove it after all db updated.
        self.wordbank.alter_table_add_columns()

        operation = Operation(wordbank = self.wordbank)

        # setup command line
        self.history_path = os.path.join(appcgm.get_path('log'), 'command.history')

        # register commands
        self.regist_cmd("fuzzy", operation.fuzzy, description="Fuzzy search for a word in the dictionary and display suggestions.")
        self.regist_cmd("search", operation.search, description="Search for a specific word in the dictionary and display its meaning.")

        # legacy commands
        # self.regist_cmd("dictionary", operation.dictionary_search, description="Interactive dictionary search and vocabulary grading.")
        # self.regist_cmd("memorize", operation.vocabulary_memorize, arg_list = [0, 1, 2, 3, 4, 5], description="Help user memorize vocabulary based on familiarity level.")
        # self.regist_cmd("file", operation.file, description="Read words from a file and start an interactive learning session.")
        # self.regist_cmd("text", operation.textfile, description="Read word list from input and start an interactive learning session.")

        # new ui functions
        self.regist_cmd("dictionary", operation.cmd_search_dictionary, description="Interactive dictionary search and vocabulary grading.", group='ui')

        # memorize words
        self.regist_cmd("memorize", operation.cmd_memorize_words, description="Memorize vocabulary based on familiarity level and other criteria.", arg_list = ['times', 'familiar', 'number', 'reverse', 'new'],  group='ui')
        self.regist_cmd("forgotten", operation.cmd_forgotten_words, description="Memorize forgotten vocabulary based on familiarity level.", arg_list = ['familiar', 'number'],  group='ui')

        # input
        self.regist_cmd("file", operation.cmd_file_input, description="Read words from a specified file and start an interactive learning session.", group='input')
        self.regist_cmd("text", operation.cmd_text_input, description="Input a list of words directly and start an interactive learning session.", group='input')
        self.regist_cmd("vbuilder", operation.cmd_vocabs_builder_input, description="Read vocabulary from a Koreader sqlite3 database file.", group='input')
        self.regist_cmd("json", operation.cmd_json_input, description="Read vocabulary from a customize dictionary/json file, and show memorize list.", group='input')

        # debug commands
        self.regist_cmd("dump_vocabulary", operation.dump_vocabulary, description="Display all words currently stored in the user's vocabulary bank.", group = 'debug')
        self.regist_cmd("dump_config", appcgm.dump, description="Display the current application configuration settings.", group = 'debug')
        self.regist_cmd("dump_db", self.debug_cmd_dump_db, description="Display all tables and their contents in the vocabulary database.", group = 'debug')
        self.regist_cmd("dump_dict", dict_mgr.list_dictionary, description="List all available dictionaries.", group = 'debug')
    def debug_cmd_dump_db(self, args):
        self.wordbank.dump_all()
        return True

