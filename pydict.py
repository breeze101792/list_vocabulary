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
from core.core import Core

from utility.cli import CommandLineInterface as cli 
from utility.debug import *

from plugins.operation import *

psettings = Settings()

def main():
    parser = OptionParser(usage='Usage: pydict [options] ......')
    parser.add_option("-w", "--word", dest="word",
                    help="word that you would like to get its meaning", action="store")
    parser.add_option("-t", "--test", dest="test",
                    help="testing function", action="store_true")
    parser.add_option("-d", "--debug", dest="debug",
                    help="debug mode on!!", action="store_true")

    (options, args) = parser.parse_args()

    # set up settings.py!
    # mode settings
    if options.test is not None:
        psettings.set('mode', 'TEST')
        # psettings.set('file_name', options.test)
        psettings.set('debug', True)
        psettings.set('database', 'debug.db')
    else:
        psettings.set('mode', "CORE")

    if options.debug:
        DebugSetting.debug_level = DebugLevel.MAX
        dbg_info('Enable Debug mode')
        psettings.set('debug', True)
        psettings.set('database', 'debug.db')

    # init
    psettings.set('config_path', os.environ['HOME']+'/'+'.list_config'+'/')
    os.makedirs(psettings.get('config_path'), exist_ok=True)

    # open file
    try:
        dbg_debug("Mode: ", psettings.get('mode'))
        if psettings.get('mode') == "CORE":
            pdcli = Core()
            pdcli.run()

        elif psettings.get('mode') == 'TEST':
            pdcli = Core(promote='ptest')
            pdcli.run()

    except (OSError, KeyboardInterrupt):
        print(psettings.get('msg_exit'))
    except:
        raise
if __name__ == '__main__':
    main()
