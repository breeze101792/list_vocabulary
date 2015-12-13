
class Word:
    def __init__(self):
        self.word = "test"
        self.pronunciation = ""
        # [["meaning", [["english sentence", "thranslated sentence"], [] ...] ] ... ]
        self.noun = [["meaning", [["english sentence", "thranslated sentence"]]]]
        self.verb = []
        self.adjective = []
        self.adverb = []
        self.interjection = []

        self.synonyms = []
        self.antonyms = []

        # use dictionary type to impoement
        self.forms = []
    def show_meaning(self):
        print("search word:" + self.word)
        print(self.pronunciation)
        if len(self.noun) != 0:
            print("Noun:")
            for n in self.noun:
                print(n[0])
                if len(n[1]) > 0:
                    for sen in n[1]:
                        print(sen[0] + " " + sen[1])
        if len(self.verb) != 0:
            print("Verb:")
            for n in self.verb:
                print(n[0])
                if len(n[1]) > 0:
                    for sen in n[1]:
                        print(sen[0] + " " + sen[1])

# return word

class Dictionary:
    pass

class DictionaryManager:
    pass
