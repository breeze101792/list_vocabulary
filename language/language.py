from language.english.a1 import vocabulary as english_a1
from language.english.basic import vocabulary as english_basic
from language.spanish.basic import vocabulary as spanish_basic
# TODO, currently hard-coded to english-a1
class Language:
    @classmethod
    def get_word_list(cls, level = 'a1', language = 'english'):
        if language == 'english' and level == 'a1':
            return english_basic + english_a1
        elif language == 'spanish' and level == 'a1':
            return spanish_basic
        else:
            dbg_warning(f'language {language} and level {level} is not supported')
            return []


