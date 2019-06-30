#!/usr/bin/env python3
# system function
from optparse import OptionParser
import os
import subprocess as sp
import time
# local function
from data import FileData
from dictionary import Word
#from ydict import ydict
#from local_dict import LocalDict
from ecdict import *
from settings import Settings
from wordbank import WordBank
import settings
from utils import getch
from cli import *
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
                    help="testing function", action="store")
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
        psettings.set('word', options.word)
    elif options.file_name is not None:
        psettings.set('mode', EUIMode.FILE)
        psettings.set('file_name', options.file_name)
    elif options.test is not None:
        psettings.set('mode', 'test')
        psettings.set('file_name', options.test)
        psettings.set('debug', True)
        psettings.set('database', 'debug.db')
    elif options.list is not None:
        psettings.set('mode', EUIMode.LIST)
    else:
        psettings.set('mode', EUIMode.INTERCTIVE)
    if options.debug:
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

    my_dict = SECDict()
    wordbank = WordBank()
    wordbank.db__init()
    wordbank.connect()

    # open file
    try:
        cli = CommandLineInterface(settings = psettings, wordbank = wordbank, dictionary = my_dict)
        cli.set_filter(level = word_level, freq = word_freq)
        if psettings.get('mode') == EUIMode.WORD:
            cli.set_mode(EUIMode.WORD)
        elif psettings.get('mode') == EUIMode.INTERCTIVE:
            cli.set_mode(EUIMode.INTERCTIVE)
        elif psettings.get('mode') == EUIMode.FILE:
            cli.set_mode(EUIMode.FILE)
            cli.read_file()
        cli.run()
    except (OSError, KeyboardInterrupt):
        print(psettings.get('msg_exit'))
    except:
        raise
if __name__ == '__main__':
    main()
