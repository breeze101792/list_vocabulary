from utility.cli import CommandLineInterface
from plugins.operation import *

class Core(CommandLineInterface):
    def __init__(self, promote='PYD'):
        wellcome_message = "Hi, enjoy learning a language."
        super().__init__(promote, wellcome_message = wellcome_message)

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
        self.regist_cmd("fuzzy", operation.fuzzy, description="Fuzzy search for a word in the dictionary.")
        self.regist_cmd("search", operation.search, description="Search for a word in the dictionary and display its meaning.")
        self.regist_cmd("dictionary", operation.dictionary_search, description="Interactive dictionary search and vocabulary grading.")
        self.regist_cmd("memorize", operation.vocabulary_memorize, description="Help user memorize vocabulary based on familiarity level.")
        self.regist_cmd("vocabulary", operation.vocabulary, description="Display all words in the user's vocabulary bank.")
        self.regist_cmd("file", operation.file, description="Read words from a file and start an interactive learning session.")
        self.regist_cmd("text", operation.textfile, description="Read word list from input and start an interactive learning session.")
