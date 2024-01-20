import sqlite3
import os
from core.settings import Settings
from utility.debug import *
from utility.udb import *

class WordBank(uDatabase):
    psettings = Settings()
    def __init__(self):
        self.db_path=self.psettings.get('config_path') + self.psettings.get('database')
        super().__init__(self.db_path)
    def setup(self):
        if not os.path.isfile(self.db_path):
            # dbg_info('Database Init')
            dbg_info("Initiialize database")
            self.connect()
            # conn = sqlite3.connect(self.psettings.get('config_path') + self.psettings.get('database'))
            # c = conn.cursor()
            # Create table
            self.execute('''CREATE TABLE WORD
                         (word text, times real, familiar real)''')

            # Insert a row of data
            self.execute("INSERT INTO Word VALUES ('a',1,1)")

            # Save (commit) the changes
            self.commit()

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
    def update_familiar(self, word, familiar = 0):
        query_str = "SELECT times, familiar FROM WORD WHERE word == '%s'" % word
        result = self.execute(query_str, fetchone=True)#.fetchone()
        if result is None:
            return False
        else:
            query_str = "UPDATE WORD SET familiar = %i WHERE word == '%s'" % (familiar, word)
            result = self.execute(query_str, fetchone=True)#.fetchone()
        return True

class WordBank_bak:
    __db_lock = False
    __db_connection = None
    __cursor = None
    psettings = Settings()
    def db__init(self):
        if not os.path.isfile(self.psettings.get('config_path') + self.psettings.get('database')):
            conn = sqlite3.connect(self.psettings.get('config_path') + self.psettings.get('database'))
            c = conn.cursor()
            # Create table
            c.execute('''CREATE TABLE WORD
                         (word text, times real, familiar real)''')

            # Insert a row of data
            c.execute("INSERT INTO Word VALUES ('a',1,1)")

            # Save (commit) the changes
            conn.commit()

            # We can also close the connection if we are done with it.
            # Just be sure any changes have been committed or they will be lost.
            conn.close()
            # print('successful init')
    def __lock(self):
        if self.__db_lock == False:
            self.__db_lock = True
            return True
        else:
            return False
    def __unlock(self):
        if self.__db_lock == True:
            self.__db_lock = False
            return True
        else:
            return False
    def __is_locked(self):
        dbg_trace("DB Lock:", self.__db_lock)
        return self.__db_lock
    def connect(self):
        if self.__is_locked():
            # print("Database is locked!")
            return False
        elif self.__db_connection is None:
            self.__lock()
            self.__db_connection = sqlite3.connect(self.psettings.get('config_path') + self.psettings.get('database'))
            self.__cursor = self.__db_connection.cursor()
            self.__unlock()
            return True
        else:
            # print("Database is already connected!")
            return True
    def close(self):
        if self.__db_lock:
            # print('database is locked!\n please unlocked first!')
            return False
        elif self.__db_connection is None:
            # print('there is nothing to do!')
            return True
        else:
            self.commit()
            self.__db_connection.close()
            return True
    def commit(self):
        if self.__is_locked():
            # print('db is locked')
            return False
        else:
            # print('sent commit')
            self.__db_connection.commit()
            return True
    def quer_for_all_word(self, times = None, familiar = None):
        if self.__is_locked():
            # print('db is locked')
            return False
        else:
            self.__lock()
            query_str = """SELECT * FROM WORD"""
            if times is not None and familiar is not None:
                query_str = "%s WHERE times == %i AND familiar == %i" % (query_str, times, familiar)
            elif familiar is not None:
                query_str = "%s WHERE familiar == %i" % (query_str, familiar)
            elif familiar is not None:
                query_str = "%s WHERE times == %i" % (query_str, times)

            dbg_debug(query_str)
            result = self.__cursor.execute(query_str)
            self.__unlock()
            return result.fetchall()
    def get_word(self, word):
        if self.__is_locked():
            # print('db is locked')
            return False
        else:
            self.__lock()
            query_str = "SELECT times, familiar FROM WORD WHERE word == '%s'" % word
            result = self.__cursor.execute(query_str)
            self.__unlock()
            ret_data = result.fetchall()
            if len(ret_data) != 0:
                return ret_data[0]
            else:
                return False
    def update(self, word, times = 1, familiar = 0):
        dbg_info(word)
        query_str = "SELECT times, familiar FROM WORD WHERE word == '%s'" % word
        if self.__is_locked():
            # print('db is locked')
            return False
        else:
            self.__lock()
            result = self.__cursor.execute(query_str).fetchone()
            dbg_debug(query_str, result)
            if result is None:
                self.__unlock()
                return False
            else:
                query_str = "UPDATE WORD SET times = %i, familiar = %i WHERE word == '%s'" % (result[0] + times, result[1] + familiar, word)
                dbg_debug(query_str)
                result = self.__cursor.execute(query_str).fetchone()
            self.__unlock()
            return result #.fetchone()
    def insert(self, word, familiar = 0):
        query_str = "SELECT word FROM WORD WHERE word == '%s'" % word
        # print(query_str)
        if self.__is_locked():
            # print('db is locked')
            return False
        else:
            self.__lock()
            result = self.__cursor.execute(query_str).fetchone()
            # print(result)
            if result is not None:
                # word is already in the wordbank
                self.__unlock()
                return False
            else:
                query_str = "INSERT INTO WORD (word, times, familiar) VALUES ('%s', %i, %i)" % (word, 1, familiar)
                # print(query_str)
                result = self.__cursor.execute(query_str).fetchone()
            self.__unlock()
            return result #.fetchone()
    def update_familiar(self, word, familiar = 0):
        query_str = "SELECT times, familiar FROM WORD WHERE word == '%s'" % word
        if self.__is_locked():
            # print('db is locked')
            return False
        else:
            self.__lock()
            result = self.__cursor.execute(query_str).fetchone()
            if result is None:
                self.__unlock()
                return False
            else:
                query_str = "UPDATE WORD SET familiar = %i WHERE word == '%s'" % (familiar, word)
                result = self.__cursor.execute(query_str).fetchone()
            self.__unlock()
            return True
# test = WordBank()
# test.db__init()
# test.connect()
# test.insert('test')
# print(test.update('test', 1))
# print(test.quer_for_all_word())
# test.close()
