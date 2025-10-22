import datetime
import os
import sys
import re
import html
from bs4 import BeautifulSoup

from pystardict import Dictionary as startdict

from dictionary.dictionary import Dictionary
from dictionary.word import JWord,PureWord

class StartDict(Dictionary):
    def __init__(self, dict_name = "json dict", dict_file="./local.json"):
        self.dict_name = dict_name
        self.dict_file=dict_file
        # if not os.path.exists(self.dict_file):
        #     raise FileNotFoundError(f"Dictionary file not found: {self.dict_file}")

        self.dict = startdict(self.dict_file)

    def strip_tags(self, text: str) -> str:
        """Remove both HTML/XML tags and decode entities."""

        # Remove HTML comments <!-- ... -->
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

        # Remove XML processing instructions <? ... ?>
        text = re.sub(r'<\?.*?\?>', '', text, flags=re.DOTALL)

        # Remove DOCTYPE declarations <!DOCTYPE ... >
        text = re.sub(r'<!DOCTYPE.*?>', '', text, flags=re.DOTALL | re.IGNORECASE)

        # Replace <br> / <br/> with newlines
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)

        # Replace CDATA sections with their contents
        text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', text, flags=re.DOTALL)

        # Remove all other HTML/XML tags like <tag> ... </tag>
        text = re.sub(r'<[^>]+>', '', text)

        # Decode HTML entities like &nbsp; &amp; &quot;
        text = html.unescape(text)

        # Clean up spaces and newlines
        text = re.sub(r'\s+\n', '\n', text)
        text = re.sub(r'\n\s+', '\n', text)
        return text.strip()
    def __search(self, query_word):
        dict_word = self.dict[query_word] # This is now a list of definition dictionaries
        # plain_text = dict_word
        plain_text = self.strip_tags(dict_word)

        # print("==================")
        # print(plain_text)
        # print("==================")

        word_obj = PureWord()
        word_obj.word = query_word
        word_obj.dict_name = self.dict_name
        word_obj.meaning = plain_text

        # word_obj.definitions = definitions
        # word_obj.definitions = [[1,2,3]]
        return word_obj

    def search(self, query_word):
        try:
            return self.__search(query_word)
        except KeyError:
            return None
        return None

# def demo():
#     
#     milestone1 = datetime.datetime.today()
#     
#     dicts_dir = os.path.join(os.path.dirname(__file__))
#     dict1 = startdict(os.path.join(dicts_dir, 'stardict-quick_eng-rus-2.4.2','quick_english-russian'))
#     dict2 = startdict(os.path.join(dicts_dir, 'stardict-quick_rus-eng-2.4.2',
#         'quick_russian-english'))
#     
#     milestone2 = datetime.datetime.today()
#     print '2 dicts load:', milestone2-milestone1
#     
#     print dict1.idx['test']
#     print dict2.idx['проверка']
#     
#     milestone3 = datetime.datetime.today()
#     print '2 cords getters:', milestone3-milestone2
#     
#     print dict1.dict['test']
#     print dict2.dict['проверка']
#     
#     milestone4 = datetime.datetime.today()
#     print '2 direct data getters (w\'out cache):', milestone4-milestone3
#     
#     print dict1['test']
#     print dict2['проверка']
#
#     milestone5 = datetime.datetime.today()
#     print '2 high level data getters (not cached):', milestone5-milestone4
#     
#     print dict1['test']
#     print dict2['проверка']
#     
#     milestone6 = datetime.datetime.today()
#     print '2 high level data getters (cached):', milestone6-milestone5
#
#     # list dictionary keys and dictionary content according to the key
#     for key in dict1.ids.keys():
# 	print dict1.dict[key]
#
#
# if __name__ == '__main__':
#     demo()
