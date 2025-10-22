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
        self.regist_cmd("fuzzy", operation.fuzzy, description="Fuzzy search for a word in the dictionary.")
        self.regist_cmd("search", operation.search, description="Search for a word in the dictionary and display its meaning.")
        self.regist_cmd("dictionary", operation.dictionary_search, description="Interactive dictionary search and vocabulary grading.")
        self.regist_cmd("memorize", operation.vocabulary_memorize, arg_list = [0, 1, 2, 3, 4, 5], description="Help user memorize vocabulary based on familiarity level.")
        self.regist_cmd("vocabulary", operation.vocabulary, description="Display all words in the user's vocabulary bank.")
        self.regist_cmd("file", operation.file, description="Read words from a file and start an interactive learning session.")
        self.regist_cmd("text", operation.textfile, description="Read word list from input and start an interactive learning session.")

        # debug commands
        self.regist_cmd("dump_config", appcgm.dump, description="Dump all config.", group = 'debug')
        self.regist_cmd("dump_db", self.debug_cmd_dump_db, description="Dump all table.", group = 'debug')
        self.regist_cmd("dump_dict", dict_mgr.list_dictionary, description="Dump all dictionary.", group = 'debug')
    def debug_cmd_dump_db(self, args):
        self.wordbank.dump_all()
        return True

