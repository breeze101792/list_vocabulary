#!/bin/env python
from optparse import OptionParser

import settings
def printfun(it, s = '', e = '\n'):
    for i in it:
        print(s + i + e)

class Data:
    def __init__(self, file = None):
        self.file = file
        self.sentence_list = file
        # self.words = None
        self.word_list = []
        self.word_counter = []
    def do_sentence_list(self):
        tmp_list = self.file.replace('\n', ' ').replace('  ', ' ').splitlines()
        tmp = []
        mark_list = ['.','!', '?', ':', '\"', "-", "*"]
        for mark in mark_list:
            tmp = []
            for idx, line in enumerate(tmp_list):
                if mark in line:
                    tmp_sen = line.split(mark)
                    if len(tmp_sen) > 1:
                        tmp.extend(tmp_sen)
                    else:
                        tmp.append(tmp_sen)
                else:
                    tmp.append(line)
            tmp_list = tmp
        self.sentence_list = tmp_list

        # for i in tmp:
        #     print(i.lstrip())
    @staticmethod
    def word_extractora(word):
        tmp = []
        # for idx, word in enumerate(sen):2015-12-06t12:45:50+00:00
        while len(word) >= 1 and (word[0].isalpha() is False or word[-1].isalpha() is False):
            # if len(word) == 1 and word.isalpha() is False:
            #     return []
            if word[0].isalpha() is not True:
                word = word[1:]
            elif word[-1].isalpha() is not True:
                word = word[:-2]
        print("in while\t" + word)
        if len(word) >= 1 and word[0].isalpha() and word[-1].isalpha() and word.replace('\'', 'z').replace('-', 'z').isalpha() :
            return [word]
        else:
            wbuf = ''
            for char in word:
                if char.isalpha() or char == '\'' or char == '-':
                    wbuf += char
                else:
                    tmp.append(wbuf)
                    wbuf = ''
            if wbuf != '':
                tmp.append(wbuf)
        return tmp
    @staticmethod
    def word_extractor(word):
        tmp = []
        # for idx, word in enumerate(sen):2015-12-06t12:45:50+00:00
        while len(word) >= 1 and (word[0].isalpha() is False or word[-1].isalpha() is False):
            # if len(word) == 1 and word.isalpha() is False:
            #     return []
            if word[0].isalpha() is False:
                word = word[1:]
            elif word[-1].isalpha() is False:
                word = word[:-2]
        if len(word) < 1:
            return []
        elif word.count('\'') <= 1 and word.replace('\'', 'z').replace('-', 'z').isalpha() :
            return [word]
        else:
            idx = 0
            wbuf = ''
            #have a bug when "a',"" appear
            while word[idx].isalpha() or word[idx] == '\'' or (word[idx] == '-' and word[idx].isalpha()):
                    idx += 1
            tmp.append(word[0:idx - 1])
            tmp.extend(Data.word_extractor(word[idx:]))
        return tmp

    def do_word_list(self):
        tmp_words = self.file.replace('.', ' ').replace('?', ' ').replace('!', ' ').replace('.', ' ').replace(',', ' ').lower().split()
        tmp_words = sorted(tmp_words)
        self.word_list = []
        self.word_counter =  []
        cidx = 0
        cbuf = 0
        while cidx < len(tmp_words):
            if tmp_words[cidx].isalpha():
                self.word_list.append(tmp_words[cidx])
                cbuf = tmp_words.count(tmp_words[cidx])
                self.word_counter.append(cbuf)
                cidx += cbuf;
            else:
                cbuf = tmp_words.count(tmp_words[cidx])
                for each_word in self.word_extractor(tmp_words[cidx]):
                    if each_word in self.word_list:
                        self.word_counter[self.word_list.index(each_word)] += cbuf
                    else:
                        self.word_list.append(each_word)
                        self.word_counter.append(cbuf)
                cidx += cbuf;

        # self.words = dict({key: val for key, val in zip(self.word_list, self.word_counter)})
        # printfun(sorted(self.words))
        # for voc, times in zip(self.word_list, self.word_counter):
        #     print(voc + " : " + times.__str__())

    def do_list(self):
        self.sentence_list = self.file.splitlines()
        for line in self.sentence_list:
            print(line + "\n")
        pass
    def word_report(self):
        for times, voc in sorted(zip(self.word_counter, self.word_list), reverse=True):
            print(voc + ' ' * (15 - len(voc)) + ":\t" + times.__str__())
            # self.word_counter[self.word_list.index(voc)].__str__())
class Word:
    pass

# return word
class ydict:
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
    else:
        settings.file_name = "data/i have a dream.txt"

    print("list all vocabulary")
    print("file name\t", settings.file_name)

    # open file
    # with open(settings.file_name) as f:
    #     for line in f:
    #         print(line)
    f = open(settings.file_name)
    text = f.read()
    f.close()
    data = Data(text)
    # print(data.word_extractorb('--app\'ss,dd!!'))
    data.do_word_list()
    data.word_report()

if __name__ == '__main__':
    main()
