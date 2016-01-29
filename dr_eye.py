import urllib.request
from html.parser import HTMLParser

from dictionary import Word,Dictionary

class DictParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_dict = False
        self.content = False
        # self.query_string = None
        self.current_tags = None
        self.word = Word()
        # mark_list = ['display_word','phonetic']
        # self.mark_dict = dict(zip(mark_list,range(len(mark_list))))
        # print(self.mark_dict)
    def handle_starttag(self, tag, attrs):
        # print(attrs)
        if len(attrs) != 0 and (tag == 'div' or tag == 'span'):
            if len(attrs) >= 2 and attrs[1][1] == 'display_word':
                self.in_dict = True
                self.current_tags = attrs[1][1]
                # print(attrs[1][1])
            elif attrs[0][1] == 'phonetic':
                self.current_tags = attrs[0][1]
            # elif attrs[]

        pass
    def handle_data(self, data):
        if not self.in_dict or len(data.strip()) == 0:
            return
        elif self.current_tags == 'display_word':
            self.word.word = data.strip()
            self.current_tags = None
        elif self.current_tags == 'phonetic':
            self.word.pronunciation = data.strip()
            self.current_tags = None
        else:
            print(len(data.strip()),">",data.strip())
        pass
    def get_word(self):
        return self.word


class dr_eye(Dictionary):
    def __init__(self):
        self.__url = "http://yun.dreye.com/dict_new/dict_min.php?w="
    def search(self, word):
        opener = urllib.request.FancyURLopener({})
        f = opener.open(self.__url+word)
        # print("searching address:" + self.url + word)
        content = f.read()
        dp = DictParser()
        # dp.set_query_str("test")
        dp.feed(content.decode('UTF-8'))
        # print(content.decode('UTF-8'))
        word = dp.get_word()
        if word.word == '無法找到符合 ':
            return False
        else:
            return word

my_dict = dr_eye()
# word = input('input word: >')
word = 'apple'
w = my_dict.search(word)
print('\nprint meaning')
w.show_meaning()



#
