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
        dbg_info(f"Load wordbook from {self.db_path}")

        # Familiarity settings:
        # TODO, still working on defining those levels.
        # 0: Not relevant or not yet memorized; the word will be ignored for now.
        # 1: New word; try to remember its meaning. Criteria: Recognize the word when seen (can read it).
        # 2: Transition new word to long-term memory; try to remember its meaning. Criteria: Recognize the word when seen (can read it).
        # 3: When presented with a Chinese word, you can recall this word. Criteria: Can translate it.
        # 4: You can use it in your own sentence.
        self.familiar_time_threshold = 5
        self.familiar_level_list = [1, 2]
    def setup_tables(self):
        # TODO, consider those in the future.
        # Add more columns:
        # 1. column for remember those forgeting words today. bool, could use with timestamp?
        # 2. column for remember those beautiful words. bool?
        self.execute('''CREATE TABLE WORD
                        (word text, times real, familiar real, create_time text, timestamp real, forgotten real)''')

        # Insert a row of data with current time and timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_timestamp = datetime.now().timestamp()
        self.execute("INSERT INTO Word VALUES ('a',0,0,'%s',%f,0)" % (current_time, current_timestamp))
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

        if 'forgotten' not in columns:
            self.execute("ALTER TABLE WORD ADD COLUMN forgotten real")
            # Populate existing rows with a default value (0 for False)
            self.execute("UPDATE WORD SET forgotten = 0 WHERE forgotten IS NULL")
            dbg_info("Added 'forgotten' column to WORD table.")

        self.commit()
        return True

    def quer_for_all_word(self, times = None, familiar = None, forgotten = None):
        query_str = """SELECT word, times, familiar, forgotten FROM WORD"""
        conditions = []
        if times is not None:
            conditions.append(f"times == {times}")
        if familiar is not None:
            conditions.append(f"familiar == {familiar}")
        if forgotten is not None:
            # SQLite stores booleans as 0 for False and 1 for True
            forgotten_val = 1 if forgotten else 0
            conditions.append(f"forgotten == {forgotten_val}")
            # If forgotten is set, also check if the timestamp is today
            today_date_str = datetime.now().strftime("%Y-%m-%d")
            conditions.append(f"DATE(timestamp, 'unixepoch') == '{today_date_str}'")

        if conditions:
            query_str += " WHERE " + " AND ".join(conditions)

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
    def insert(self, word, times = 1, familiar = 0, forgotten = 0):
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
            query_str = "INSERT INTO WORD (word, times, familiar, create_time, timestamp, forgotten) VALUES ('%s', %i, %i, '%s', %f, %i)" % (word, times, familiar, current_time, current_timestamp, forgotten)
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
    def update_and_mark_familiar(self, word, forgotten = False):
        default_times = 1
        default_familiar = 1
        forgotten_val = 1 if forgotten is True else 0

        # dbg_info(word)
        query_str = "SELECT times, familiar, timestamp FROM WORD WHERE word == '%s'" % word

        result = self.execute(query_str, fetchone=True)#.fetchone()
        dbg_debug(query_str, result)
        current_timestamp = datetime.now().timestamp()

        if result is None:
            # dbg_info(word, 'Not in ')
            return self.insert(word, default_times, default_familiar, forgotten_val)
        elif datetime.fromtimestamp(result[2]).date() != datetime.now().date():
            # print(datetime.fromtimestamp(result[2]).date(),  datetime.now().date())
            if result[1] in self.familiar_level_list and result[0] + 1  > self.familiar_time_threshold:
                # to next level.
                query_str = "UPDATE WORD SET times = %i, familiar = %i, timestamp = %f, forgotten = %i WHERE word == '%s'" % (default_times, result[1] + 1, current_timestamp, forgotten_val, word)
                dbg_debug("Enter to next familar" + query_str)
                result = self.execute(query_str, fetchone=True)#.fetchone()
            else:
                if forgotten is True:
                    decreased_times = result[0] - 1 if result[0] > 0 else 0
                    # only add times in else
                    query_str = "UPDATE WORD SET times = %i, timestamp = %f, forgotten = %i WHERE word == '%s'" % (decreased_times, current_timestamp, forgotten_val, word)
                    dbg_debug("Enter to next familar" + query_str)
                    result = self.execute(query_str, fetchone=True)#.fetchone()
                else:
                    # only add times in else
                    query_str = "UPDATE WORD SET times = %i, timestamp = %f, forgotten = %i WHERE word == '%s'" % (result[0] + 1, current_timestamp, forgotten_val, word)
                    dbg_debug("Enter to next familar" + query_str)
                    result = self.execute(query_str, fetchone=True)#.fetchone()

        return result ##.fetchone()

