# from util import *
from utility.debug import *
class SWord:
    def __init__(self, word = "None"):
        self.word = word 
        self.phonetic = ""
        # ["", "", ...]
        self.definition = []
        self.translation = []
        
        self.form = []
        
        self.__cfg_indentation = "  "
        # unuse
        self.pos = []
    def __showDef(self, definition):
        for each_def in definition:
            print(self.__cfg_indentation + each_def)
    def display(self):
        if len(self.phonetic) != 0:
            print("[{}]".format(self.word))
        if len(self.form) != 0:
            print("Forms: " + self.form)
        if len(self.definition) != 0:
            print("Def.:")
            self.__showDef(self.definition)
        if len(self.translation) != 0:
            print("Transl.:")
            self.__showDef(self.translation)
    def show_meaning(self):
        self.display()
        
class Word:
    def __init__(self):
        self.word = ""
        self.pronunciation = ""
        # [["meaning", [["english sentence", "thranslated sentence"], [] ...] ] ... ]
        self.noun = []
        self.verb = []
        self.adjective = []
        self.adverb = []
        self.preposition = []
        self.abbr = []
        self.other = []

        self.synonyms = []
        self.antonyms = []

        # use dictionary type to impoement
        self.forms = []
    def __showPartMeaning(self, meaning, part="Noun"):
        if len(meaning) != 0:
            print(part)
            for idx, n in enumerate(meaning):
                # meaning
                # print("  " + idx.__str__() +  ". " + n[0].lstrip())
                print("  " + n[0].lstrip())
                # for example scentance
                if len(n[1]) > 0:
                    for sen in n[1]:
                        if len(sen[0]) > 3:
                            print(sen[0] + "\n" + sen[1])

    def show_meaning(self):
        if len(self.pronunciation)!= 0:
            print("[" + self.pronunciation + "]")
        if len(self.noun) != 0:
            self.__showPartMeaning(self.noun, "n.")
        if len(self.verb) != 0:
            self.__showPartMeaning(self.verb, "v.")
        if len(self.adjective) != 0:
            self.__showPartMeaning(self.adjective, "adj.")
        if len(self.adverb) != 0:
            self.__showPartMeaning(self.adverb, "adv.")

        if len(self.preposition) != 0:
            self.__showPartMeaning(self.preposition, "prep.")
        if len(self.abbr) != 0:
            self.__showPartMeaning(self.abbr, "abbr.")
        if len(self.other) != 0:
            self.__showPartMeaning(self.other, "other")

# return word

class Dictionary:
    def search(self, query_word):
        w = Word
        w.word = word
        return w
    def fuzzySearch(self, query_word):
        pass

class DictionaryManager:
    pass
