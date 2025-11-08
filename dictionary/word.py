import re
import traceback

class BaseWord:
    def __init__(self, word = "None", dict_name = ""):
        self.word = word
        self.dict_name = dict_name

    def show_meaning(self):
        pass
    @property
    def dict_name(self):
        return self._dict_name
    @dict_name.setter
    def dict_name(self,val):
        self._dict_name = val

class PureWord(BaseWord):
    def __init__(self, word = "None", dict_name = ""):
        self.dict_name = dict_name
        self.word = word
        self.meaning = ""

    def show_meaning(self):
        # Replace any sequence of two or more newlines with exactly two newlines.
        cleaned_meaning = re.sub(r'\n{2,}', '\n\n', self.meaning)
        print(cleaned_meaning)
    @property
    def dict_name(self):
        return self._dict_name
    @dict_name.setter
    def dict_name(self,val):
        self._dict_name = val

class SWord(BaseWord):
    def __init__(self, word = "None", dict_name = ""):
        self.dict_name = dict_name
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
        print("{}".format(self.word), end='')
        if len(self.phonetic) != 0:
            print(" [{}]".format(self.word), end='')
        print(", {}".format(self.dict_name))

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
        
class Word(BaseWord):
    def __init__(self, word = "", dict_name = ""):
        self.word = word
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
        print("{}, {}".format(self.word, self.dict_name))
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

class JWord(BaseWord):
    def __init__(self, word = "", dict_name = ""):
        self.word = word
        self.definitions = []

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
        prefix_space = "  "
        print("{}, {}".format(self.word, self.dict_name))
        for each_def in self.definitions:
            print("")
            try:
                if "part_of_speech" in each_def:
                    if "gender" in each_def:
                        print(f"{each_def['part_of_speech']} ({each_def['gender']})")
                    else:
                        print(each_def["part_of_speech"])
                elif "gender" in each_def:
                    print(each_def["gender"])

                if "meaning" in each_def:
                    print(prefix_space + each_def["meaning"])
                if "phrase" in each_def:
                    print(prefix_space + each_def["phrase"])
                if "example" in each_def:
                    print(prefix_space + " " + each_def["example"])
                if "notes" in each_def:
                    print(prefix_space + " " + each_def["notes"])
            except Exception as e:
                dbg_error(e)
            
                traceback_output = traceback.format_exc()
                dbg_error(traceback_output)
        print()
