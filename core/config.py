from utility.debug import *
from utility.config import *

class AppConfig(BasicConfig):
    class about:
        program_name = 'list vocabulary'
        version='0.0.1'
    # class debug:
    #     development = False
    class path:
        root = os.path.expanduser(f"~/.config/ConfigManager")
        config = "config.json"
        language = "language/english"
        dictionary = "dictionary"
        log = 'log'
    class variable:
        wordbank = 'wordbank.db'
        language = "english"

    # persistant config
    # class config:
    #     language = "english"

class AppConfigManager(ConfigManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,config=AppConfig, **kwargs)
        self.__supported_language_list = ['english', 'spanish']

        # self.config = AppConfig
        # some config could be seeting here.
        # self.config.set_config('investment')
        self.set('path.root', '~/.config/list_vocbs', save = False)
    def set_lang(self, language = 'english'):
        if language not in self.__supported_language_list:
            # in order to protect data base, we set language to None
            language = 'None'
            dbg_error(f'Language {language} not supported.')

        self.set('path.language', "language/" + language, save = False)
        self.set('variable.language', language, save = False)
        dbg_info(f'Set Language to {language}')

    def enable_debug(self):
        self.set('variable.wordbank', 'debug.db', save = False)
