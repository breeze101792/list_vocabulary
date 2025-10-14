from utility.cli import CommandLineInterface
from plugins.operation import *

class Core(CommandLineInterface):
    def __init__(self, promote='PYD'):
        super().__init__(promote)

        # pre init.
        psettings = Settings()
        psettings.set('config_path', os.environ['HOME']+'/'+'.list_config'+'/')
        os.makedirs(psettings.get('config_path'), exist_ok=True)

        dict_db = os.path.join(os.path.dirname(__file__), "../dict.db")
        my_dict = SECDict(dict_db=dict_db)

        wordbank = WordBank()
        wordbank.setup()
        wordbank.connect()

        operation = Operation(settings = psettings, wordbank = wordbank, dictionary = my_dict)

        # register commands
        self.regist_cmd("fuzzy", operation.fuzzy, description="fuzzy search")
        self.regist_cmd("search", operation.search, description="regular search")
        self.regist_cmd("dictionary", operation.dictionary_search, description="search dictionary, on learning mode.")
        self.regist_cmd("memorize", operation.vocabulary_memorize, description="Help user memorize vocabs.")
        self.regist_cmd("vocabulary", operation.vocabulary, description="my vocabulary")
        self.regist_cmd("file", operation.file, description="Read file do list ")
