#!/usr/bin/env python3
# system function
from optparse import OptionParser
import os
import subprocess as sp
import time

from dictionary.dictionary import Word
from dictionary.hal.ecdict import *

from core.data import FileData
from core.settings import Settings
from core.wordbank import *

from utility.cli import CommandLineInterface as cli 
from utility.debug import *

from plugins.operation import *

psettings = Settings()

def main():
    parser = OptionParser(usage='Usage: pydict [options] ......')
    parser.add_option("-f", "--file", dest="file_name",
                    help="file that you would like to parse", action="store")
    parser.add_option("-F", "--Frequency", dest="word_freq",
                    help="Filter for word frequency", default=0, action="store")
    parser.add_option("-w", "--word", dest="word",
                    help="word that you would like to get its meaning", action="store")
    parser.add_option("-l", "--list", dest="list",
                    help="List words on wordbank", action="store_true")
    parser.add_option("-t", "--test", dest="test",
                    help="testing function", action="store_true")
    parser.add_option("-d", "--debug", dest="debug",
                    help="debug mode on!!", action="store_true")
    parser.add_option("-L", "--word-level", dest="word_level",
                    help="Setup Word Level", action="store")
    #parser.add_option("-L", "--word-level", dest="word_level",
    #                help="Setup Word Level", default=[], action="append")

    (options, args) = parser.parse_args()

    # set up settings.py!
    # mode settings
    if options.word is not None:
        psettings.set('mode', EUIMode.WORD)
        word_list = list([options.word])
    elif options.file_name is not None:
        psettings.set('mode', EUIMode.FILE)
        psettings.set('file_name', options.file_name)
    elif options.test is not None:
        psettings.set('mode', 'TEST')
        # psettings.set('file_name', options.test)
        psettings.set('debug', True)
        psettings.set('database', 'debug.db')
    elif options.list is not None:
        psettings.set('mode', EUIMode.LIST)
    else:
        psettings.set('mode', EUIMode.INTERCTIVE)

    if options.debug:
        DebugSetting.debug_level = DebugLevel.MAX
        dbg_info('Enable Debug mode')
        psettings.set('debug', True)
        psettings.set('database', 'debug.db')
    # other setting
    if options.word_level is not None:
        word_level = [int(each_level) for each_level in options.word_level.split(',')]
    else:
        word_level = [0,1,2,3,4,5]


    # init
    word_freq = int(options.word_freq)
    psettings.set('config_path', os.environ['HOME']+'/'+'.list_config'+'/')
    os.makedirs(psettings.get('config_path'), exist_ok=True)

    # setup dictionary file
    dict_db = os.path.join(os.path.dirname(__file__), "dict.db")
    my_dict = SECDict(dict_db=dict_db)

    wordbank = WordBank()
    wordbank.connect()
    wordbank.db__init()

    # open file
    try:
        op = Operation(settings = psettings, wordbank = wordbank, dictionary = my_dict)

        op_legacy = Operation_legacy(settings = psettings, wordbank = wordbank, dictionary = my_dict)
        op_legacy.set_filter(level = word_level, freq = word_freq)

        dbg_info("Mode: ", psettings.get('mode'))
        if psettings.get('mode') == EUIMode.WORD:
            op.def_search({'word':word_list[0]})
        elif psettings.get('mode') == EUIMode.INTERCTIVE:
            # get into interative mode
            pdcli = cli(promote='PYD')
            pdcli.one_command = True
            # pdcli.regist_cmd()
            pdcli.regist_default_cmd(op.def_search)
            pdcli.regist_cmd("fuzzy", op.fuzzy, description="fuzzy search")
            pdcli.regist_cmd("search", op.search, description="regular search")
            pdcli.regist_cmd("vocabulary", op.vocabulary, description="my vocabulary")
            # pdcli.regist_cmd("file", op.file, description="file ")
            pdcli.run()
        elif psettings.get('mode') == EUIMode.LIST:
            # query all words on the database
            op_legacy.set_mode(EUIMode.LIST)
            word_list = [ each_word[0] for each_word in wordbank.quer_for_all_word()]
            op_legacy.set_list(word_list)
            op_legacy.run()
        elif psettings.get('mode') == EUIMode.FILE:
            # get file mode, ex. subtitle
            op_legacy.set_mode(EUIMode.FILE)
            op_legacy.read_file()
            op_legacy.run()
        elif psettings.get('mode') == 'TEST':

            op_test = Operation(settings = psettings, wordbank = wordbank, dictionary = my_dict)

            pdcli = cli(promote='PYD Test ')
            pdcli.one_command = True
            # pdcli.regist_cmd("fuzzy", op_test.fuzzy, description="fuzzy search", arg_list=['project', 'task', 'name', 'description']  )
            pdcli.regist_cmd("fuzzy", op_test.fuzzy, description="fuzzy search")
            pdcli.regist_cmd("search", op_test.search, description="regular search")
            pdcli.regist_cmd("vocabulary", op.vocabulary, description="my vocabulary")
            pdcli.regist_default_cmd(op_test.def_search)
            pdcli.run()

        # finialize
        wordbank.commit()

    except (OSError, KeyboardInterrupt):
        print(psettings.get('msg_exit'))
    except:
        raise
if __name__ == '__main__':
    main()
