import sqlite3
import os

from core.config import AppConfigManager

from utility.debug import *
from utility.udb import *

class WordBank(uDatabase):
    def __init__(self):
        self.appcgm = AppConfigManager()
        language_path = self.appcgm.get_path('language')
        if not os.path.isdir(language_path):
            os.makedirs(language_path)
        self.db_path=os.path.join(language_path, self.appcgm.get('variable.wordbank'))
        super().__init__(self.db_path)
    def setup_tables(self):
        self.execute('''CREATE TABLE WORD
                        (word text, times real, familiar real)''')

        # Insert a row of data
        self.execute("INSERT INTO Word VALUES ('a',0,0)")
        return True

    # def setup(self):
    #     if not os.path.isfile(self.db_path):
    #         # dbg_info('Database Init')
    #         dbg_info("Initiialize database")
    #         self.connect()
    #
    #         self.execute('''CREATE TABLE WORD
    #                      (word text, times real, familiar real)''')
    #
    #         # Insert a row of data
    #         self.execute("INSERT INTO Word VALUES ('a',0,0)")
    #
    #         # Save (commit) the changes
    #         self.commit()
    #
    #         # we close after setup.
    #         self.close()

    def quer_for_all_word(self, times = None, familiar = None):
        query_str = """SELECT * FROM WORD"""
        if times is not None and familiar is not None:
            query_str = "%s WHERE times == %i AND familiar == %i" % (query_str, times, familiar)
        elif familiar is not None:
            query_str = "%s WHERE familiar == %i" % (query_str, familiar)
        elif familiar is not None:
            query_str = "%s WHERE times == %i" % (query_str, times)

        dbg_debug(query_str)
        result = self.execute(query_str)
        dbg_debug('result:', result)

        return result# .fetchall()
    def get_word(self, word):
        query_str = "SELECT times, familiar FROM WORD WHERE word == '%s'" % word
        result = self.execute(query_str)
        ret_data = result#.fetchall()
        if len(ret_data) != 0:
            return ret_data[0]
        else:
            return False
    def update(self, word, times = 1, familiar = 0):
        # dbg_info(word)
        query_str = "SELECT times, familiar FROM WORD WHERE word == '%s'" % word

        result = self.execute(query_str, fetchone=True)#.fetchone()
        dbg_debug(query_str, result)
        if result is None:
            # dbg_info(word, 'Not in ')
            return self.insert(word, times, familiar)
        else:
            query_str = "UPDATE WORD SET times = %i, familiar = %i WHERE word == '%s'" % (result[0] + times, result[1] + familiar, word)
            dbg_debug(query_str)
            result = self.execute(query_str, fetchone=True)#.fetchone()
        return result ##.fetchone()
    def insert(self, word, times = 1, familiar = 0):
        query_str = "SELECT word FROM WORD WHERE word == '%s'" % word
        # print(query_str)

        result = self.execute(query_str, fetchone=True)#.fetchone()
        # print(result)
        if result is not None:
            # word is already in the wordbank
            return False
        else:
            query_str = "INSERT INTO WORD (word, times, familiar) VALUES ('%s', %i, %i)" % (word, times, familiar)
            # print(query_str)
            result = self.execute(query_str, fetchone=True)#.fetchone()
        return result ##.fetchone()
    def update_familiar(self, word, familiar):
        query_str = "SELECT times, familiar FROM WORD WHERE word == '%s'" % word
        result = self.execute(query_str, fetchone=True)#.fetchone()
        if result is None:
            return False
        else:
            query_str = "UPDATE WORD SET familiar = %i WHERE word == '%s'" % (familiar, word)
            result = self.execute(query_str, fetchone=True)#.fetchone()
        return True

