from dictionary import Word

def ischinese(test_str):
    for ch in test_str:
        if ord(ch) < 0x4e00 or ord(ch) > 0x9fff:
            return False
    return True

class LocalDict:
    def __init__(self, dict_file="./default.dict"):
        self.dict_file=dict_file
        self.dict = None
        self.__buildDict()
    def __buildDict(self):
        self.dict = dict()
        with open(self.dict_file) as fdict:
            for each_line in fdict:
                try:
                    (word, tmp) = each_line.split(" = ", 1)
                    (part, tmp) = tmp.split(".", 1)
                    meanings = tmp.split(";")
                    each_word = (word, part, meanings)
                    self.dict[word] = list([part, meanings])
                except ValueError:
                    print("[Err]", each_line)
    def __search(self, query_word):
        result = self.dict[query_word]
        word = Word()
        part = None
        # print(result)

        word.word = query_word
        if result[0] == 'n':
            part = word.noun
        elif result[0] == 'v':
            part = word.verb
        elif result[0] == 'adv':
            part = word.adverb
        elif result[0] == 'adj':
            part = word.adjective
        else:
            print("Unknown part!!!")
            return 

        for each_meaning in result[1]:
            part.append([each_meaning, [["", ""]]])
        return word
    def search(self, query_word):
        try:
            return self.__search(query_word)
        except KeyError:
            return False
