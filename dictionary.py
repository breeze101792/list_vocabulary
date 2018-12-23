
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

        self.synonyms = []
        self.antonyms = []

        # use dictionary type to impoement
        self.forms = []
    def __showPartMeaning(self, meaning, part="Noun"):
        if len(meaning) != 0:
            print(part)
            for idx, n in enumerate(meaning):
                # meaning
                print("  " + idx.__str__() +  ". " + n[0].lstrip())
                # for example scentance
                if len(n[1]) > 0:
                    for sen in n[1]:
                        if len(sen[0]) > 3:
                            print(sen[0] + "\n" + sen[1])

    def show_meaning(self):
        if len(self.pronunciation)!= 0:
            print(self.pronunciation)
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

# return word

class Dictionary:
    def search(self, word):
        w = Word
        w.word = word
        return w

class DictionaryManager:
    pass
