import urllib.request
from html.parser import HTMLParser

from dictionary.dictionary import Word, SWord

def ischinese(test_str):
    for ch in test_str:
        if ord(ch) < 0x4e00 or ord(ch) > 0x9fff:
            return False
    return True


class DictParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.content = False
        # self.query_string = None
        self.li_counter = 0
        self.ignore_flag = False
        self.sentenc_buf = ""
        self.senbuf_flag = False
        self.word = Word()
        self.current = 0
        self.example_flag = 0
    def handle_starttag(self, tag, attrs):
        if self.content and tag == "li" and len(attrs) == 0:
            self.li_counter += 1
        elif len(attrs) == 0:
            if tag == "b":
                self.senbuf_flag = True
                self.sentenc_buf = ""
        elif tag == "li" and attrs[0][1] == "first":
            # print("first" + self.li_counter.__str__())
            self.li_counter = 0
            self.content = True
        elif tag == "li" and attrs[0][1] == "last":
            # print("last" + self.li_counter.__str__())
            self.content = False
        elif tag == "span" and len(attrs) > 2:
            if attrs[1][1] == "iconStyle":
                self.ignore_flag = True
    # def handle_endtag(self, tag):
    #     pass

    def handle_data(self, data):
        if len(data) == 1:
            pass
        elif self.content == False or self.ignore_flag:
            if self.ignore_flag:
                self.ignore_flag = False
        elif self.li_counter == 0:
            if self.word.word == "":
                self.word.word = data
            elif data[0][0] == 'K':
                self.word.pronunciation = data
                # print("query word:" + data)
        # main content
        elif self.li_counter == 1:
            # print("content:" + len(data).__str__() + data)
            if data[0] == 'n' and data[1] == '.' or data[0:3] == "n [":
                # print("Noun in")
                self.current = 1
            elif data[0:2] == 'v.' or data[0:2] == 'vi' or data[0:2] == 'vt':
                # print("Verb in")
                self.current = 2
            elif data[0:2] == 'a.':# and data[1] == '.':
                # print("adj in")
                self.current = 3
            elif data[0:3] == 'ad.':
                # print("adv in")
                self.current = 4
            elif data[0:5] == 'prep.':
                # print("prep in")
                self.current = 5
            elif data[0:5] == 'abbr.':
                # print("abbr in")
                self.current = 6
            elif self.current == 1:
                if data[0][0] in ["1","2", "3", "4", "5", "6", "7", "8", "9", "0"]:
                    self.word.noun.append([data, [["   ", "   "]]])
                    self.example_flag = 0
                #  or len(data[0]) == 1 is for . ? !
                elif data[0:1].isalpha() or data[1:2].isalpha() or len(data[0]) == 1:
                    if ischinese(data[0]):
                        self.word.noun[-1][1][self.example_flag][1] += data
                    else:
                        self.word.noun[-1][1][self.example_flag][0] += data
                    # self.word.noun[-1][1][self.example_flag][0] += data
                else:
                    self.word.noun[-1][1][self.example_flag][1] += data
                    self.word.noun[-1][1].append(["   ", "   "])
                    self.example_flag += 1
            elif self.current == 2:
                if data[0][0] in ["1","2", "3", "4", "5", "6", "7", "8", "9", "0"]:
                    self.word.verb.append([data, [["   ", "   "]]])
                    self.example_flag = 0
                elif data[0:1].isalpha() or data[1:2].isalpha() or len(data[0]) == 1:
                    if ischinese(data[0]):
                        self.word.verb[-1][1][self.example_flag][1] += data
                    else:
                        self.word.verb[-1][1][self.example_flag][0] += data
                else:
                    self.word.verb[-1][1][self.example_flag][1] += data
                    self.word.verb[-1][1].append(["   ", "   "])
                    self.example_flag += 1
            elif self.current == 3:
                # print(data)
                if data[0][0] in ["1","2", "3", "4", "5", "6", "7", "8", "9", "0"]:
                    self.word.adjective.append([data, [["   ", "   "]]])
                    self.example_flag = 0
                elif data[0:1].isalpha() or data[1:2].isalpha() or len(data[0]) == 1:
                    if ischinese(data[0]):
                        self.word.adjective[-1][1][self.example_flag][1] += data
                    else:
                        self.word.adjective[-1][1][self.example_flag][0] += data
                else:
                    self.word.adjective[-1][1][self.example_flag][1] += data
                    self.word.adjective[-1][1].append(["   ", "   "])
                    self.example_flag += 1
            elif self.current == 4:
                # print(data)
                if data[0][0] in ["1","2", "3", "4", "5", "6", "7", "8", "9", "0"]:
                    self.word.adverb.append([data, [["   ", "   "]]])
                    self.example_flag = 0
                elif data[0:1].isalpha() or data[1:2].isalpha() or len(data[0]) == 1:
                    if ischinese(data[0]):
                        self.word.adverb[-1][1][self.example_flag][1] += data
                    else:
                        self.word.adverb[-1][1][self.example_flag][0] += data
                else:
                    self.word.adverb[-1][1][self.example_flag][1] += data
                    self.word.adverb[-1][1].append(["   ", "   "])
                    self.example_flag += 1
            elif self.current == 5:
                # print(data)
                if data[0][0] in ["1","2", "3", "4", "5", "6", "7", "8", "9", "0"]:
                    self.word.preposition.append([data, [["   ", "   "]]])
                    self.example_flag = 0
                elif data[0:1].isalpha() or data[1:2].isalpha() or len(data[0]) == 1:
                    if ischinese(data[0]):
                        self.word.preposition[-1][1][self.example_flag][1] += data
                    else:
                        self.word.preposition[-1][1][self.example_flag][0] += data
                else:
                    self.word.preposition[-1][1][self.example_flag][1] += data
                    self.word.preposition[-1][1].append(["   ", "   "])
                    self.example_flag += 1
            elif self.current == 6:
                if data[0][0] in ["1","2", "3", "4", "5", "6", "7", "8", "9", "0"]:
                    self.word.abbr.append([data, [["   ", "   "]]])
                    self.example_flag = 0
                elif data[0:1].isalpha() or data[1:2].isalpha() or len(data[0]) == 1:
                    if ischinese(data[0]):
                        self.word.abbr[-1][1][self.example_flag][1] += data
                    else:
                        self.word.abbr[-1][1][self.example_flag][0] += data
                else:
                    self.word.abbr[-1][1][self.example_flag][1] += data
                    self.word.abbr[-1][1].append(["   ", "   "])
                    self.example_flag += 1


                pass
        # other sections
        # elif self.li_counter == 2:
        #     print("forms:" + data)
        # elif self.li_counter == 3:
        #     print("sym:" + data)
        # elif self.sentenc_buf:
        #     self.sentenc_buf += data
    def get_word(self):
        return self.word


class ydict:
    def __init__(self):
        self.url = "http://tw.dictionary.search.yahoo.com/search?p="
    def search(self, word):
        opener = urllib.request.FancyURLopener({})
        f = opener.open(self.url+word)
        # print("searching address:" + self.url + word)
        content = f.read()
        dp = DictParser()
        # dp.set_query_str("test")
        dp.feed(content.decode('UTF-8'))
        # print(content.decode('UTF-8'))
        word = dp.get_word()
        # print(word.word, "word ")
        if word.word == '無法找到符合 ':
            return False
        else:
            return word
