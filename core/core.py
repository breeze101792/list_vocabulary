from utility.cli import CommandLineInterface
from plugins.operation import *
from core.config import AppConfigManager
from dictionary.manager import Manager as DictMgr
from core.config import AppConfigManager

# save status
from plugins.pronunciation import Pronunciation
from dictionary.hal.llm import LLM

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
        self.config_action_list = ['dump', 'set', 'get', 'save', 'reload']
        self.regist_cmd("config", self.cmd_config, description="Config command.", arg_list = self.config_action_list, group='config')
        self.regist_cmd("save", self.cmd_data_save, description="Save data.", group='config')

        # freq
        self.regist_cmd("freq", operation.cmd_freq, description="Set frequency list.", arg_list = ['set', 'enable', 'disable', 'show'], group='freq')
        self.regist_cmd("compare", operation.cmd_freq_cmp, description="Compare frequency list with files, adjust freq for you progress.", arg_list = ['freq', 'save'], group='freq')

        # ui functions
        self.regist_cmd("dictionary", operation.cmd_search_dictionary, description="Interactive dictionary search and vocabulary grading.", group='ui')
        self.regist_cmd("stats", operation.cmd_statistic, description="Display vocabulary statistics.", arg_list = ['times', 'familiar'], group='ui')

        # memorize words
        self.regist_cmd("vocabulary", operation.cmd_vocabulary, description="Memorize vocabulary based on familiarity level and other criteria.", arg_list = ['times', 'familiar', 'number', 'reverse', 'new', 'forgotten', 'review', 'interval', 'reinforce'],  group='ui')
        self.regist_cmd("forgotten", operation.cmd_forgotten_words, description="Memorize forgotten vocabulary based on familiarity level.", arg_list = ['familiar', 'number'],  group='ui')
        self.regist_cmd("new", operation.cmd_new_words, description="Display today's newly added vocabulary.", arg_list = ['familiar'],  group='ui')

        self.regist_cmd("reinforce", operation.cmd_reinforce_words, description="Reinforce memorize word in level 1.",  group='ui')
        self.regist_cmd("review", operation.cmd_review_words, description="Review memorize word in level 2.",  group='ui')

        # input
        input_args = ['state', 'reviewed', 'known', 'stats']
        self.regist_cmd("text", operation.cmd_text_input, description="Input a list of words directly and start an interactive learning session.", arg_list = input_args, group='input')
        self.regist_cmd("json", operation.cmd_json_input, description="Read vocabulary from a customize dictionary/json file, and show memorize list.", arg_list = ['file'] + input_args, group='input')
        self.regist_cmd("file", operation.cmd_file_input, description="Read words from a specified file and start an interactive learning session.", arg_list = ['file'] + input_args, group='input')
        self.regist_cmd("vbuilder", operation.cmd_vocabs_builder_input, description="Read vocabulary from a Koreader sqlite3 database file.", arg_list = ['file'] + input_args, group='input')

        self.regist_cmd("list", operation.cmd_list, description="Set list for memorize.", arg_list = ['set', 'file', 'stats'], group='input')

        # debug commands
        self.regist_cmd("dump_vocabulary", operation.dump_vocabulary, description="Display all words currently stored in the user's vocabulary bank.", arg_list = ['file_name'], group = 'debug')
        self.regist_cmd("dump_config", appcgm.dump, description="Display the current application configuration settings.", group = 'debug')
        self.regist_cmd("dump_db", self.debug_cmd_dump_db, description="Display all tables and their contents in the vocabulary database.", group = 'debug')
        self.regist_cmd("dump_dict", dict_mgr.list_dictionary, description="List all available dictionaries.", group = 'debug')
    def debug_cmd_dump_db(self, args):
        self.wordbank.dump_all()
        return True
    def cmd_config(self, args):
        appcgm = AppConfigManager()
        var_action_list = self.config_action_list
        var_action = ""

        var_args = []
        for each_idx in range(1, args['#'] + 1):
            each_args = args[str(each_idx)]

            if each_args in var_action_list:
                var_action = each_args
            else:
                var_args.append(each_args)
        dbg_debug(f"{var_action}: {len(var_args), var_args}")
        if var_action == 'dump':
            appcgm.dump()
        elif var_action == 'save':
            appcgm.save()
        elif var_action == 'reload':
            print("Some function may not be affected after restarted.")
            appcgm.load()
        elif var_action == 'set':
            if len(var_args) == 2:
                appcgm.set(var_args[0], var_args[1])
                print(f"{var_args[0]}: {appcgm.get(var_args[0])}") 
        elif var_action == 'get':
            if len(var_args) == 1:
                print(f"{var_args[0]}: {appcgm.get(var_args[0])}") 

        return True
    def cmd_data_save(self, args = None, quite = False):
        # we have save on page exit, but still have this api for user to call.
        # print("Saving Core status...")
        Pronunciation.save()
        LLM.save_cache()
        if not quite:
            print("Data saved.")
        return True
    def quit(self):
        self.cmd_data_save(quite = True)
        print("GoodBye!")

