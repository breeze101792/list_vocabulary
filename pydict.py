#!/usr/bin/env python3
# system function
from optparse import OptionParser
import os
import subprocess as sp
import time

from dictionary.dictionary import Word
from dictionary.hal.ecdict import *

from core.data import FileData
from core.wordbank import *
from core.core import Core
from core.config import AppConfigManager

from utility.cli import CommandLineInterface as cli 
from utility.debug import *

from plugins.operation import *

def main():
    parser = OptionParser(usage='Usage: pydict [options] ......')
    parser.add_option("-l", "--lang", dest="lang",
                    help="Set language, default english.", action="store", default = "english")
    parser.add_option("-d", "--debug", dest="debug",
                    help="debug mode on!!", action="store_true")

    # variables
    (options, args) = parser.parse_args()
    appcgm = AppConfigManager()

    if options.debug:
        DebugSetting.debug_level = DebugLevel.MAX
        dbg_info('Enable Debug mode')
        appcgm.enable_debug()
    else:
        DebugSetting.debug_level = DebugLevel.WARNING

    # load config
    appcgm.set_lang(options.lang)
    appcgm.load()

    # open file
    try:
        if not options.debug:
            pdcli = Core(promote = f"{options.lang.lower()}@pyd ")
            pdcli.run()

        elif options.debug:
            dbg_info("Enable debug mode.")
            pdcli = Core(promote='pydebug')
            pdcli.run()
    except:
        raise
    finally:
        appcgm.save()
if __name__ == '__main__':
    main()
