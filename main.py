#!/bin/env python
from optparse import OptionParser
from data import Data
from dictionary import Word
from ydict import ydict


import settings
def printfun(it, s = '', e = '\n'):
    for i in it:
        print(s + i + e)


def main():
    parser = OptionParser(usage = 'Usage: login ......')
    parser.add_option("-f", "--file", dest="file_name", help="file that you would like to parse", action="store")
    parser.add_option("-w", "--word", dest="word", help="word that you would like to get its meaning", action="store")
    parser.add_option("-t", "--test", dest="test", help="testing function", action="store")


    # parser.add_option("-p", "--password", dest="user_password", help="User password for log in", action="store")
    # parser.add_option("-s", "--serial-number", dest="serial_number", help="Project's serial number", action="store")
    # parser.add_option("-a", dest="job_type_long", help="Job for logn term",default=False, action="store_true")
    # parser.add_option("-w", dest="job_type_short", help="Job for short term",default=False, action="store_true")
    # parser.add_option("-q", dest="quiet", help="Make script more quiet",default=False, action="store_true")
    # parser.add_option("-i", "--sign-in", dest="sign_in", help="Sign in",default=False, action="store_true")
    # parser.add_option("-o", "--sign-out", dest="sign_out", help="Sign out",default=False, action="store_true")
    (options, args) = parser.parse_args()

    #set up settings.py!
    if options.file_name is not None:
        settings.file_name = options.file_name
    else:
        settings.file_name = "data/i have a dream.txt"

    # print("list all vocabulary")
    # print("file name\t", settings.file_name)

    # open file
    if options.file_name is not None:
        f = open(settings.file_name)
        text = f.read()
        f.close()
        data = Data(text)
        data.do_word_list()
        data.word_report()
    if options.word is not None:
        # print("search single word!")
        test = ydict()
        test.search(options.word)
    if options.test is not None:
        word = Word()
        word.show_meaning()
if __name__ == '__main__':
    main()
