from dictionary.word import Word
from dictionary.dictionary import Dictionary

def ischinese(test_str):
    for ch in test_str:
        if ord(ch) < 0x4e00 or ord(ch) > 0x9fff:
            return False
    return True

class LocalDict(Dictionary):
    def __init__(self, dict_name = "local dict", dict_file="./local.csv"):
        self.dict_name = dict_name
        self.dict_file=dict_file
        self.dict = None
        self.__buildDict()
    def __buildDict(self):
        self.dict = dict()
        with open(self.dict_file) as fdict:
            for each_line in fdict:
                try:
                    part = "other"

                    # test = v.meaning
                    (word, tmp) = each_line.split(" = ", 1)
                    (part, tmp) = tmp.split(".")
                    meanings = tmp.split(";")
                    each_word = (word, part, meanings)
                    self.dict[word] = list([part, meanings])
                    #print(each_word, self.dict[word])
                except ValueError:
                    print("[Err]", each_line)
    def __search(self, query_word):
        result = self.dict[query_word]
        word = Word()
        part = None
        # print(result)

        word.word = query_word
        word.dict_name = self.dict_name
        if result[0] == 'n':
            part = word.noun
        elif result[0] == 'v':
            part = word.verb
        elif result[0] == 'adv':
            part = word.adverb
        elif result[0] == 'adj':
            part = word.adjective
        elif result[0] == 'other':
            part = word.other
        else:
            print("Unknown part")
            return 

        for each_meaning in result[1]:
            part.append([each_meaning, [["", ""]]])
        return word
    def search(self, query_word):
        try:
            return self.__search(query_word)
        except KeyError:
            return None
        return None
