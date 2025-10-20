from language.english.a1 import vocabulary as english_a1
from language.english.basic import vocabulary as english_basic
# TODO, currently hard-coded to english-a1
class Language:
    @classmethod
    def get_word_list(cls, level = 'a1', ):
        return english_basic + english_a1


