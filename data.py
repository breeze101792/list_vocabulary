
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
        elif word.count('\'') <= 1 and word.replace('\'', 'z').replace('-', 'z').isalpha() and word != '\'' and word != '-':
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
        tmp_words = self.file.replace('>', ' ').replace('<', ' ').replace('.', ' ').replace('?', ' ').replace('!', ' ').replace('.', ' ').replace(',', ' ').replace('\"', ' ').lower().split()
        processed_word_list = []
        self.word_list = []
        self.word_counter =  []
        cidx = 0
        for each_word in tmp_words:
            processed_word_list.extend(self.word_extractor(each_word))
        word_list_sorted = sorted(processed_word_list)
        while cidx < len(word_list_sorted):
            if word_list_sorted[cidx].isalpha():
                if len(word_list_sorted[cidx]) <= 2:
                    # Skip the word if the length less then 2
                    cidx += 1
                    continue
                if word_list_sorted[cidx] not in self.word_list:
                    self.word_list.append(word_list_sorted[cidx])
                    self.word_counter.append(1)
                else:
                    self.word_counter[self.word_list.index(word_list_sorted[cidx])] += 1
            cidx += 1
        # self.word_report()
        # getch()
    def do_list(self):
        self.sentence_list = self.file.splitlines()
        for line in self.sentence_list:
            print(line + "\n")
        pass
    def word_report(self):
        for voc, times in zip(self.word_list, self.word_counter):
            print(times.__str__().zfill(4), "\t: " + voc)
    def get_word_list(self):
        #return tuple(self.word_list)
        return list(self.word_list)
    def get_freq_list(self):
        #return tuple(self.word_list)
        return list(self.word_counter)
    def get_word_freq(self, word):
        return self.word_counter[self.word_list.index(word)]
