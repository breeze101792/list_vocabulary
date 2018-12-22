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
from local_dict import LocalDict
from settings import Settings
from wordbank import WordBank
import settings
from utils import getch

psettings = Settings()

def printfun(it, s='', e='\n'):
    for i in it:
        print(s + i + e)

def interactive(wordbank, my_dict):
    while True:
        query_word = input(psettings.get('name').__str__() + ">")
        word = my_dict.search(query_word)
        if word:
            word.show_meaning()
            if not wordbank.update(word.word):
                wordbank.insert(word.word)
            wordbank.commit()
        else:
            print("can't find %s" % query_word)

def fileCheck(wordbank, my_dict):
    f = open(psettings.get('file_name'))
    text = f.read()
    f.close()
    file_data = FileData(text)
    file_data.do_word_list()
    
    idx_tmp = 0;
    file_word_list = file_data.get_word_list()
    uncheck_word_list = []
    familiar_threshold = 3
    while idx_tmp < len(file_word_list):
        sp.call('clear',shell=False)
        # show word & meaning
        dict_word = my_dict.search(file_word_list[idx_tmp])
        # search databas
        db_word = wordbank.get_word(file_word_list[idx_tmp])

        if db_word and db_word[1] > familiar_threshold:
            file_word_list.remove(file_word_list[idx_tmp])
            idx_tmp += 1
            continue

        if dict_word:
            dict_word.show_meaning()
        if db_word:
            print("The word {} is found in db.".format(file_word_list[idx_tmp]))
            print("times: {}, familiar: {}".format(db_word[0], db_word[1]))
        if not db_word and not dict_word:
            uncheck_word_list.extend(file_word_list[idx_tmp])
            file_word_list.remove(file_word_list[idx_tmp])
            idx_tmp += 1
            continue

        '''
        if word:
            word.show_meaning()
            if db_word:
                print("times: {}, familiar: {}".format(db_word[0], db_word[1]))
        else:
            if db_word:
                print("The word {} is found in db.".format(file_word_list[idx_tmp]))
                print("times: {}, familiar: {}".format(db_word[0], db_word[1]))
            else:
                uncheck_word_list.extend(file_word_list[idx_tmp])
                file_word_list.remove(file_word_list[idx_tmp])
                continue
        '''
        # operations
        while True:
            x_tmp = getch()
            time.sleep(0.05) 
            if x_tmp in ("q", "Q", "x", "X"):
                print(psettings.get('msg_exit'))
                return
            elif x_tmp in ("s", "S"):
                wordbank.commit()
                continue
            elif x_tmp in ("n", "N"):
                idx_tmp += 1
                break
            elif x_tmp in ("p", "P"):
                idx_tmp -= 1
                break
            elif x_tmp in ("1", "2", "3", "4", "5"):
                if not wordbank.update_familiar(dict_word.word, int(x_tmp)):
                    wordbank.insert(dict_word.word, int(x_tmp))
                idx_tmp += 1
                break
            elif x_tmp in ("b", "B"):
                break
            else:
                print("Unknown key>" + x_tmp)
                continue
        print(uncheck_word_list)
        wordbank.commit()

def main():
    parser = OptionParser(usage='Usage: pydict [options] ......')
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
                      
    (options, args) = parser.parse_args()

    # set up settings.py!
    # mode settings
    if options.word is not None:
        psettings.set('mode', 'word')
        psettings.set('word', options.word)
    if options.file_name is not None:
        psettings.set('mode', 'file')
        psettings.set('file_name', options.file_name)
    if options.test is not None:
        psettings.set('mode', 'test')
        psettings.set('file_name', options.file_name)
    if options.list is not None:
        psettings.set('mode', 'list')
    if options.debug:
        psettings.set('debug', True)
        psettings.set('database', 'debug.db')

    # init

    psettings.set('config_path', os.environ['HOME']+'/'+'.list_config'+'/')
    os.makedirs(psettings.get('config_path'), exist_ok=True)

    my_dict = LocalDict()
    wordbank = WordBank()
    wordbank.db__init()
    wordbank.connect()

    # open file
    try:
        if psettings.get('mode') == 'interactive':
            try:
                interactive(wordbank, my_dict)
            except EOFError:
                print(psettings.get('msg_exit'))
            except:
                raise
        elif psettings.get('mode') == 'word':
            # print("search single word!")
            query_word = options.word
            word = my_dict.search(query_word)
            if word:
                word.show_meaning()
                if not wordbank.update(word.word):
                    wordbank.insert(word.word)
                wordbank.commit()
            else:
                print("can't find %s" % query_word)
        elif psettings.get('mode') == 'file':
            fileCheck(wordbank, my_dict)

        elif psettings.get('mode') == 'list':
            # print("search single word!")
            print('word'.ljust(20) + '\ttimes\tfamiliar')
            for word in wordbank.quer_for_all_word():
                print(word[0].ljust(20),'\t',word[1],'\t',word[2])
        elif psettings.get('mode') == 'test':
            f = open(psettings.get('file_name'))
            text = f.read()
            f.close()
            data = Data(text)
            data.do_word_list()
            data.word_report()
    except (OSError, KeyboardInterrupt):
        print(psettings.get('msg_exit'))
    except:
        raise
if __name__ == '__main__':
    main()
