#!/bin/env python
from optparse import OptionParser
from data import Data
from dictionary import Word
from ydict import ydict
from settings import Settings
from wordbank import WordBank

import settings


def printfun(it, s='', e='\n'):
    for i in it:
        print(s + i + e)


def main():
    parser = OptionParser(usage='Usage: login ......')
    parser.add_option("-f", "--file", dest="file_name",
                      help="file that you would like to parse", action="store")
    parser.add_option("-w", "--word", dest="word",
                      help="word that you would like to get its meaning", action="store")
    parser.add_option("-l", "--list", dest="list",
                      help="List words on wordbank", action="store_true")
    parser.add_option("-t", "--test", dest="test",
                      help="testing function", action="store")
    parser.add_option("-d", "--debug", dest="debug",
                      help="debug mode on!!", action="store_true")

    # parser.add_option("-p", "--password", dest="user_password", help="User password for log in", action="store")
    # parser.add_option("-s", "--serial-number", dest="serial_number", help="Project's serial number", action="store")
    # parser.add_option("-a", dest="job_type_long", help="Job for logn term",default=False, action="store_true")
    # parser.add_option("-w", dest="job_type_short", help="Job for short term",default=False, action="store_true")
    # parser.add_option("-q", dest="quiet", help="Make script more quiet",default=False, action="store_true")
    # parser.add_option("-i", "--sign-in", dest="sign_in", help="Sign in",default=False, action="store_true")
    # parser.add_option("-o", "--sign-out", dest="sign_out", help="Sign out",default=False, action="store_true")
    (options, args) = parser.parse_args()
    psettings = Settings()

    # set up settings.py!
    # mode settings
    if options.word is not None:
        psettings.set('mode', 'word')
        psettings.set('word', options.word)
    if options.file_name is not None:
        psettings.set('mode', 'file')
        psettings.set('file_name', options.file_name)
    if options.file_name is not None:
        psettings.set('mode', 'test')
        psettings.set('file_name', options.file_name)
    if options.list is not None:
        psettings.set('mode', 'list')
    if options.debug:
        psettings.set(debug, True)
        psettings.set(database, 'debug.db')
    # print("list all vocabulary")
    # print("file name\t", settings.file_name)

    # init
    my_dict = ydict()
    wordbank = WordBank()
    wordbank.db__init()
    wordbank.connect()


    # open file
    try:
        if psettings.get('mode') == 'interactive':
            try:
                while True:
                    word = input(psettings.get('name').__str__() + ">")
                    if my_dict.search(word):
                        if not wordbank.update(word):
                            wordbank.insert(word)
                        wordbank.commit()
            except EOFError:
                print(psettings.get('msg_exit'))
            except:
                raise
        elif psettings.get('mode') == 'word':
            # print("search single word!")
            my_dict.search(options.word)
        elif psettings.get('mode') == 'list':
            # print("search single word!")
            for word in wordbank.quer_for_all_word():
                print(word)
        elif psettings.get('mode') == 'file':
            f = open(settings.file_name)
            text = f.read()
            f.close()
            data = Data(text)
            data.do_word_list()

            for w in data.get_word_list():
                my_dict.search(w)
        elif psettings.get('mode') == 'test':
            f = open(settings.file_name)
            text = f.read()
            f.close()
            data = Data(text)
            data.do_word_list()
            data.word_report()
    except OSError:
        print(psettings.get('msg_err_connection'))
    except:
        raise
if __name__ == '__main__':
    main()
