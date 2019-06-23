
class FileData:
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
                word = word[:-1]
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
            tmp.extend(FileData.word_extractor(word[idx:]))
        return tmp

    def do_word_list(self):
        # TODO need to find another way to remvoe those symbol except '
        tmp_words = self.file.replace('>', ' ').replace('<', ' ').replace('.', ' ').replace('?', ' ').replace('!', ' ').replace('.', ' ').replace(',', ' ').replace('\'', ' ').lower().split()
        tmp_words = sorted(tmp_words)
        self.word_list = []
        self.word_counter =  []
        cidx = 0
        cbuf = 0
        while cidx < len(tmp_words):
            # print(tmp_words[cidx])
            # remove the word like "i'm"
            if '\'' in tmp_words[cidx]:
                tmp_words[cidx] = tmp_words[cidx].strip('\'')[0]
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
    def get_word_list(self):
        #return tuple(self.word_list)
        return list(self.word_list)
