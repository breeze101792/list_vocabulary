#!/bin/env python
from optparse import OptionParser

import settings
class Data:
    def __init__(self, file):
        self.file = file
    def make_sentence_list(self):
        pass

class ydict:
    pass

class Word:
    pass
class Dictionary:
    pass

def main():
    parser = OptionParser(usage = 'Usage: login ......')
    parser.add_option("-f", "--file", dest="file_name", help="file that you would like to parse", action="store")

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

    # open file
    with open(settings.file_name) as f:
        for line in f:
            print(line)

    print("list all vocabulary")
    print("file name\t", settings.file_name)

if __name__ == '__main__':
    main()
