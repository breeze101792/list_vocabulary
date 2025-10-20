import collections
from language.language import Language

class FileData:
    def __init__(self, file = None):
        self.file = file
        self.sentence_list = file
        # self.words = None
        self.word_list = []
        self.word_counter = []

        # TODO, Make it configable by language. For now, we ignore the basic english words.
        # A list of common English words that beginners typically know (A1 level approximation).
        self.ignore_list = Language.get_word_list('a1')
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
        if word.isalpha() is True:
            return [word]
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

    def do_word_list(self, sorting = True):
        # TODO need to find another way to remvoe those symbol except '
        # Note: The initial aggressive replacement of characters like apostrophes
        # might interfere with word_extractor's intended handling of contractions.
        # This part is kept as per original code, but could be a source of issues.
        tmp_words_raw = self.file.replace('>', ' ').replace('<', ' ').replace('.', ' ').replace('?', ' ').replace('!', ' ').replace('.', ' ').replace(',', ' ').replace('\"', ' ').replace('n\'', ' ').replace('\'', ' ').lower().split()

        processed_word_list = []
        for each_word_raw in tmp_words_raw:
            # word_extractor returns a list of words
            processed_word_list.extend(self.word_extractor(each_word_raw))

        # Use a dictionary for efficient word counting
        word_counts_map = collections.defaultdict(int)
        # Use a list to store unique words in their order of first appearance
        unique_words_ordered = []
        # Use a set for efficient checking if a word has already been added to unique_words_ordered
        seen_words_for_order = set()

        for word in processed_word_list:
            # Validate word: must be alphabetic and longer than 2 characters
            if word.isalpha() and len(word) > 2:
                word_counts_map[word] += 1

                # If sorting is False, track the order of first appearance
                if not sorting and word not in seen_words_for_order:
                    unique_words_ordered.append(word)
                    seen_words_for_order.add(word)

        # Clear existing lists
        self.word_list = []
        self.word_counter = []

        if sorting:
            # Populate word_list and word_counter with alphabetically sorted words
            sorted_words = sorted(word_counts_map.keys())
            for word in sorted_words:
                if word in self.ignore_list:
                    continue
                self.word_list.append(word)
                self.word_counter.append(word_counts_map[word])
        else:
            # Populate word_list and word_counter with words in their order of first appearance
            for word in unique_words_ordered:
                if word in self.ignore_list:
                    continue
                self.word_list.append(word)
                self.word_counter.append(word_counts_map[word])
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
        if word in self.word_list:
            return self.word_counter[self.word_list.index(word)]
        return False
