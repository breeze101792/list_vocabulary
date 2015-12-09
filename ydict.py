import urllib.request
from html.parser import HTMLParser

class DictParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.content = False
        # self.query_string = None
        self.li_counter = 0
        self.ignore_flag = False
    def handle_starttag(self, tag, attrs):
        if self.content and tag == "li" and len(attrs) == 0:
            self.li_counter += 1
        elif len(attrs) == 0:
            pass
        elif tag == "li" and attrs[0][1] == "first":
            print("first" + self.li_counter.__str__())
            self.li_counter = 0
            self.content = True
        elif tag == "li" and attrs[0][1] == "last":
            print("last" + self.li_counter.__str__())
            self.content = False
        elif tag == "span" and len(attrs) > 2:
            if attrs[1][1] == "iconStyle":
                self.ignore_flag = True
            pass
        # if self.content and (tag == "a" or tag == "span" or tag == "b"):
        #     print("Start tag: " + tag)
            # for a in attrs:
            #     print(", " + str(a))
        # print("Encountered a start tag:", tag)
    def handle_endtag(self, tag):
        pass
        # if self.content and tag == "li" and len(attrs) == 0:
        #     self.li_counter -= 1
        # print("Encountered an end tag :", tag)
    def handle_data(self, data):
        if self.content == False or self.ignore_flag:
            if self.ignore_flag:
                self.ignore_flag = False
        elif self.li_counter == 0:
            print("query word:" + data)
        elif self.li_counter == 1:
            print("content:" + data)
        elif self.li_counter == 2:
            print("forms:" + data)
        elif self.li_counter == 3:
            print("sym:" + data)
        # if data == self.query_string:
        #     self.content = True
        # if self.content and (self.lasttag == "a" or self.lasttag == "span" or self.lasttag == "b"):
        #     print("data  :", data)
    # def set_query_str(self, query_str):
    #     self.query_string = query_str

class ydict:
    def __init__(self):
        self.url = "http://tw.dictionary.search.yahoo.com/search?p="
    def search(self, word):
        opener = urllib.request.FancyURLopener({})
        f = opener.open(self.url+word)
        content = f.read()
        dp = DictParser()
        # dp.set_query_str("test")
        dp.feed(content.decode('UTF-8'))
        # print(content.decode('UTF-8'))
