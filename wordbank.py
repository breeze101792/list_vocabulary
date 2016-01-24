import sqlite3
import os
from settings import Settings


class WordBank:
    __db_lock = False
    __db_connection = None
    __cursor = None
    psettings = Settings()
    def db__init(self):
        if not os.path.isfile(self.psettings.get('database')):
            conn = sqlite3.connect(self.psettings.get('database'))
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
            print('successful init')
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
        return self.__db_lock
    def connect(self):
        if self.__is_locked():
            print("Database is locked!")
            return False
        elif self.__db_connection is None:
            self.__lock()
            self.__db_connection = sqlite3.connect(self.psettings.get('database'))
            self.__cursor = self.__db_connection.cursor()
            self.__unlock()
            return True
        else:
            print("Database is already connected!")
            return True
    def close(self):
        if self.__db_lock:
            print('database is locked!\n please unlocked first!')
            return False
        elif self.__db_connection is None:
            print('there is nothing to do!')
        else:
            self.commit()
            self.__db_connection.close()
    def commit(self):
        if self.__is_locked():
            print('db is locked')
            return False
        else:
            self.__db_connection.commit()
            return True
    def quer_for_all_word(self):
        if self.__is_locked():
            print('db is locked')
            return False
        else:
            self.__lock()
            query_str = """SELECT * FROM WORD;"""
            result = self.__cursor.execute(query_str)
            self.__unlock()
            return result.fetchone()
    def update(self, word):
        query_str = "SELECT times FROM WORD WHERE word == '%s'" % word

        if self.__is_locked():
            print('db is locked')
            return False
        else:
            self.__lock()
            result = self.__cursor.execute(query_str).fetchone()[0]

            if result is None:
                self.__unlock()
                return False
            else:
                query_str = "UPDATE WORD SET times = %d WHERE word == '%s'" % (result + 1, word)
                result = self.__cursor.execute(query_str).fetchone()
            self.__unlock()
            return result #.fetchone()

test = WordBank()
test.db__init()
test.connect()
print(test.update('a'))
print(test.quer_for_all_word())
test.close()
