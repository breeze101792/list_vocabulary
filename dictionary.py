
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
    def show_meaning(self):
        print(self.word)
        if len(self.pronunciation)!= 0:
            print(self.pronunciation)
        if len(self.noun) != 0:
            print("Noun:")
            for n in self.noun:
                print(n[0])
                if len(n[1]) > 0:
                    for sen in n[1]:
                        if len(sen[0]) > 3:
                            print(sen[0] + "\n" + sen[1])
        if len(self.verb) != 0:
            print("Verb:")
            for n in self.verb:
                print(n[0])
                if len(n[1]) > 0:
                    for sen in n[1]:
                        if len(sen[0]) > 3:
                            print(sen[0] + "\n" + sen[1])
        if len(self.adjective) != 0:
            print("adjective:")
            for n in self.adjective:
                print(n[0])
                if len(n[1]) > 0:
                    for sen in n[1]:
                        if len(sen[0]) > 3:
                            print(sen[0] + "\n" + sen[1])
        if len(self.adverb) != 0:
            print("adverb:")
            for n in self.adverb:
                print(n[0])
                if len(n[1]) > 0:
                    for sen in n[1]:
                        if len(sen[0]) > 3:
                            print(sen[0] + "\n" + sen[1])


        if len(self.preposition) != 0:
            print("preposition:")
            for n in self.preposition:
                print(n[0])
                if len(n[1]) > 0:
                    for sen in n[1]:
                        if len(sen[0]) > 3:
                            print(sen[0] + "\n" + sen[1])
        if len(self.abbr) != 0:
            print("abbreviation:")
            for n in self.abbr:
                print(n[0])
                if len(n[1]) > 0:
                    for sen in n[1]:
                        if len(sen[0]) > 3:
                            print(sen[0] + "\n" + sen[1])

# return word

class Dictionary:
    pass

class DictionaryManager:
    pass
