from utility.cli import CommandLineInterface
from plugins.operation import *
from core.config import AppConfigManager
from dictionary.manager import Manager as DictMgr

class Core(CommandLineInterface):
    def __init__(self, promote='PYD'):
        appcgm = AppConfigManager()

        welcome_message = (
            "**********************************************************************\n"
            f"Hi, enjoy learning {appcgm.get('variable.language')}! \n"
            "To finish your daily learning, here are some suggestions:\n"
            "1. The words on your memorize list shouldn't exceed 100; try to keep it under 80.\n"
            "2. Daily new words shouldn't exceed 30; 20 is a moderate number.\n"
            "**********************************************************************"
        )
        super().__init__(promote, wellcome_message = welcome_message)

        # pre init.
        dict_mgr = DictMgr()

        self.wordbank = WordBank()
        self.wordbank.connect()
        self.wordbank.setup()
        # TODO, remove it after all db updated.
        self.wordbank.alter_table_add_columns()

        operation = Operation(wordbank = self.wordbank)

        # setup command line
        language = appcgm.get('variable.language')
        self.history_path = os.path.join(appcgm.get_path('log'), f'{language}_command.history')

        # register commands
        # legacy
        self.regist_cmd("fuzzy", operation.fuzzy, description="Fuzzy search for a word in the dictionary and display suggestions.", group = 'legacy')
        self.regist_cmd("search", operation.search, description="Search for a specific word in the dictionary and display its meaning.", group = 'legacy')


        # ui functions
        self.regist_cmd("dictionary", operation.cmd_search_dictionary, description="Interactive dictionary search and vocabulary grading.", group='ui')
        self.regist_cmd("stats", operation.cmd_statistic, description="Display vocabulary statistics.")

        # memorize words
        self.regist_cmd("memorize", operation.cmd_memorize_words, description="Memorize vocabulary based on familiarity level and other criteria.", arg_list = ['times', 'familiar', 'number', 'reverse', 'new', 'forgotten'],  group='ui')
        self.regist_cmd("forgotten", operation.cmd_forgotten_words, description="Memorize forgotten vocabulary based on familiarity level.", arg_list = ['familiar', 'number'],  group='ui')
        self.regist_cmd("new", operation.cmd_new_words, description="Display today's newly added vocabulary.", arg_list = ['familiar'],  group='ui')

        # input
        self.regist_cmd("text", operation.cmd_text_input, description="Input a list of words directly and start an interactive learning session.", group='input')
        self.regist_cmd("json", operation.cmd_json_input, description="Read vocabulary from a customize dictionary/json file, and show memorize list.", group='input')
        self.regist_cmd("file", operation.cmd_file_input, description="Read words from a specified file and start an interactive learning session.", arg_list = ['state'], group='input')
        self.regist_cmd("vbuilder", operation.cmd_vocabs_builder_input, description="Read vocabulary from a Koreader sqlite3 database file.", arg_list = ['state'], group='input')

        # debug commands
        self.regist_cmd("dump_vocabulary", operation.dump_vocabulary, description="Display all words currently stored in the user's vocabulary bank.", group = 'debug')
        self.regist_cmd("dump_config", appcgm.dump, description="Display the current application configuration settings.", group = 'debug')
        self.regist_cmd("dump_db", self.debug_cmd_dump_db, description="Display all tables and their contents in the vocabulary database.", group = 'debug')
        self.regist_cmd("dump_dict", dict_mgr.list_dictionary, description="List all available dictionaries.", group = 'debug')
    def debug_cmd_dump_db(self, args):
        self.wordbank.dump_all()
        return True

