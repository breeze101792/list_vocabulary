import urllib.request
from html.parser import HTMLParser

class DictParser(HTMLParser):
    # def __init__(self):
    #     super.__init__()
    def handle_starttag(self, tag, attrs):
        print("Encountered a start tag:", tag)
    def handle_endtag(self, tag):
        print("Encountered an end tag :", tag)
    def handle_data(self, data):
        print("Encountered some data  :", data)

class ydict:
    def __init__(self):
        self.url = "http://tw.dictionary.search.yahoo.com/search?p="
    def search(self, word):
        opener = urllib.request.FancyURLopener({})
        f = opener.open(self.url+word)
        content = f.read()
        dp = DictParser()
        dp.feed(content.decode('UTF-8'))
        # print(content.decode('UTF-8'))
