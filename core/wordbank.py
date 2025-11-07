import sqlite3
import os
from datetime import datetime

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

        # Familiarity settings:
        # 0: Not relevant or not yet memorized.
        # 1: New word; try to remember its meaning. Criteria: Recognize the word when seen (can read it).
        # 2: When presented with a Chinese word, you can recall this word. Criteria: Can translate it.
        # 3: You can use it in your own sentence.
        self.familiar_time_threshold = 5
        self.familiar_level_list = [1, 2]
    def setup_tables(self):
        # TODO, consider those in the future.
        # Add more columns:
        # 1. column for remember those forgeting words today. bool, could use with timestamp?
        # 2. column for remember those beautiful words. bool?
        self.execute('''CREATE TABLE WORD
                        (word text, times real, familiar real, create_time text, timestamp real)''')

        # Insert a row of data with current time and timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_timestamp = datetime.now().timestamp()
        self.execute("INSERT INTO Word VALUES ('a',0,0,'%s',%f)" % (current_time, current_timestamp))
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

    def alter_table_add_columns(self):
        # Check if 'create_time' column exists
        cursor = self.execute("PRAGMA table_info(WORD)")
        columns = [col[1] for col in cursor]

        if 'create_time' not in columns:
            self.execute("ALTER TABLE WORD ADD COLUMN create_time text")
            # Populate existing rows with a default value (current time)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.execute("UPDATE WORD SET create_time = '%s' WHERE create_time IS NULL" % current_time)
            dbg_info("Added 'create_time' column to WORD table.")

        if 'timestamp' not in columns:
            self.execute("ALTER TABLE WORD ADD COLUMN timestamp real")
            # Populate existing rows with a default value (current Unix timestamp)
            current_timestamp = datetime.now().timestamp()
            self.execute("UPDATE WORD SET timestamp = %f WHERE timestamp IS NULL" % current_timestamp)
            dbg_info("Added 'timestamp' column to WORD table.")

        self.commit()
        return True

    def quer_for_all_word(self, times = None, familiar = None):
        query_str = """SELECT word, times, familiar FROM WORD"""
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
        query_str = "SELECT times, familiar, timestamp FROM WORD WHERE word == '%s'" % word
        result = self.execute(query_str)
        ret_data = result#.fetchall()
        if len(ret_data) != 0:
            return ret_data[0]
        else:
            return False
    # def update(self, word, times = 1, familiar = 0):
    #     # dbg_info(word)
    #     query_str = "SELECT times, familiar FROM WORD WHERE word == '%s'" % word
    #
    #     result = self.execute(query_str, fetchone=True)#.fetchone()
    #     dbg_debug(query_str, result)
    #     if result is None:
    #         # dbg_info(word, 'Not in ')
    #         return self.insert(word, times, familiar)
    #     else:
    #         query_str = "UPDATE WORD SET times = %i, familiar = %i WHERE word == '%s'" % (result[0] + times, result[1] + familiar, word)
    #         dbg_debug(query_str)
    #         result = self.execute(query_str, fetchone=True)#.fetchone()
    #     return result ##.fetchone()
    def insert(self, word, times = 1, familiar = 0):
        query_str = "SELECT word FROM WORD WHERE word == '%s'" % word
        # print(query_str)

        result = self.execute(query_str, fetchone=True)#.fetchone()
        # print(result)
        if result is not None:
            # word is already in the wordbank
            return False
        else:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_timestamp = datetime.now().timestamp()
            query_str = "INSERT INTO WORD (word, times, familiar, create_time, timestamp) VALUES ('%s', %i, %i, '%s', %f)" % (word, times, familiar, current_time, current_timestamp)
            # print(query_str)
            result = self.execute(query_str, fetchone=True)#.fetchone()
        return result ##.fetchone()
    def update_familiar(self, word, familiar):
        query_str = "SELECT times, familiar FROM WORD WHERE word == '%s'" % word
        result = self.execute(query_str, fetchone=True)#.fetchone()
        if result is None:
            return False
        else:
            # query_str = "UPDATE WORD SET familiar = %i WHERE word == '%s'" % (familiar, word)
            # reset times to 1
            current_timestamp = datetime.now().timestamp()
            query_str = "UPDATE WORD SET times = %i, familiar = %i, timestamp = %f WHERE word == '%s'" % (1, familiar, current_timestamp, word)
            result = self.execute(query_str, fetchone=True)#.fetchone()
        return True
    def update_and_mark_familiar(self, word, isFamiliar = True):
        default_times = 1
        default_familiar = 1
        # dbg_info(word)
        query_str = "SELECT times, familiar, timestamp FROM WORD WHERE word == '%s'" % word

        result = self.execute(query_str, fetchone=True)#.fetchone()
        dbg_debug(query_str, result)
        current_timestamp = datetime.now().timestamp()

        if result is None:
            # dbg_info(word, 'Not in ')
            return self.insert(word, default_times, default_familiar)
        elif datetime.fromtimestamp(result[2]).date() != datetime.now().date():
            # print(datetime.fromtimestamp(result[2]).date(),  datetime.now().date())
            if result[1] in self.familiar_level_list and result[0] + 1  >= self.familiar_time_threshold:
                # to next level.
                query_str = "UPDATE WORD SET times = %i, familiar = %i, timestamp = %f WHERE word == '%s'" % (default_times, result[1] + 1, current_timestamp, word)
                dbg_debug("Enter to next familar" + query_str)
                result = self.execute(query_str, fetchone=True)#.fetchone()
            # elif result[0] + 1  == self.familiar_time_threshold:
            #     # only add times in else
            #     query_str = "UPDATE WORD SET times = %i, familiar = %i WHERE word == '%s'" % (result[0] + 1, result[1], word)
            #     dbg_debug("Enter to next familar" + query_str)
            #     result = self.execute(query_str, fetchone=True)#.fetchone()
            else:
                if isFamiliar is False:
                    decreased_times = result[0] - 1 if result[0] > 0 else 0
                    # only add times in else
                    query_str = "UPDATE WORD SET times = %i, timestamp = %f WHERE word == '%s'" % (decreased_times, current_timestamp, word)
                    dbg_debug("Enter to next familar" + query_str)
                    result = self.execute(query_str, fetchone=True)#.fetchone()
                else:
                    # only add times in else
                    query_str = "UPDATE WORD SET times = %i, timestamp = %f WHERE word == '%s'" % (result[0] + 1, current_timestamp, word)
                    dbg_debug("Enter to next familar" + query_str)
                    result = self.execute(query_str, fetchone=True)#.fetchone()

        return result ##.fetchone()

