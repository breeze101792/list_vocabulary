from third_party.ecdict.stardict import *
from utility.debug import *

from dictionary.word import Word, SWord
from dictionary.dictionary import Dictionary

def ischinese(test_str):
    for ch in test_str:
        if ord(ch) < 0x4e00 or ord(ch) > 0x9fff:
            return False
    return True

class SECDict(Dictionary):
    def __init__(self, dict_name = "SECDict", dict_file="dict.db"):
        self.dict_name = dict_name
        self.dict_file = os.path.join(os.path.dirname(__file__), dict_file)
        dbg_debug('Open dictionary: ', self.dict_file)
        self.start_dict = StarDict(self.dict_file, False)
    def __fuzzy_search(self, query_word):
        result = self.start_dict.match(query_word)
        candidate_list = list()
        # dbg_debug('fuzzy search: ', result)
        if result == None:
            return False
        for each_candidate in result:
            candidate_list.append(each_candidate[1])
        return candidate_list

        # word = SWord()
        # word.word = query_word
        # word.phonetic = result['phonetic']
        # word.form = result['exchange'].replace('/', ' ').replace(':', '/')
        # for each_meaning in result['definition'].split('\n'): 
        #     if len(each_meaning) == 0:
        #         continue
        #     word.definition.append(each_meaning)
        # for each_meaning in result['translation'].split('\n'): 
        #     if len(each_meaning) == 0:
        #         continue
        #     word.translation.append(each_meaning)
        # return word
    def __search(self, query_word):
        result = self.start_dict.query(query_word)
        if result == None:
            return False
        word = SWord()
        word.word = query_word
        word.dict_name = self.dict_name
        word.phonetic = result['phonetic']
        word.form = result['exchange'].replace('/', ' ').replace(':', '/')
        for each_meaning in result['definition'].split('\n'): 
            if len(each_meaning) == 0:
                continue
            word.definition.append(each_meaning)
        for each_meaning in result['translation'].split('\n'): 
            if len(each_meaning) == 0:
                continue
            word.translation.append(each_meaning)
        return word
        
    def search(self, query_word):
        try:
            return self.__search(query_word)
        except KeyError:
            return None
    def suggest(self, query_word):
        try:
            return self.__fuzzy_search(query_word)
        except KeyError:
            return []

class ECDict(Dictionary):
    def __init__(self, dict_file="dict.db"):
        self.dict_file = os.path.join(os.path.dirname(__file__), dict_file)
        self.start_dict = StarDict(self.dict_file, False)
    def __search(self, query_word):
        result = self.start_dict.query(query_word)
        if result == None:
            return False
        word = Word()

        word.word = query_word
        word.pronunciation = result['phonetic']
        for each_meaning in result['definition'].split('\n'): 
            word.other.append([each_meaning, [["", ""]]])
        for each_meaning in result['translation'].split('\n'): 
            word.other.append([each_meaning, [["", ""]]])
        return word
        
        if result[0] == 'n':
            part = word.noun
        elif result[0] == 'v':
            part = word.verb
        elif result[0] == 'a':
            part = word.adverb
        elif result[0] == 'a':
            part = word.adjective
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

if __name__ == '__main__':
    if len(sys.argv) == 3:
        print("ecdict init: convert " + sys.argv[1] + " to " +  sys.argv[2] + '\n')
        # convert_dict("dict.db", "stardict.csv")
        convert_dict(sys.argv[1], sys.argv[2])
    else:
        print("Usage: ./ecdict.py filename.dict startdict.csv\n")

