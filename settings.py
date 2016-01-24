# list all settings here


class Settings:
    __setting_dict = {\
    'name':'List Words',\
    'version':'0.1',\
    'file_name':'./data/i\ have\ a\ dream.txt',\
    'mode':'interactive',\
    'dictionary':'ydict',\
    'database':'wordbank.db',\
    \
    'word':'test',\
    \
    'msg_exit':'Have a nice day!',\
    'msg_err_connection':'please check out you internet connection!',\
    }
    def set(self, name, value):
        self.__setting_dict[name] = value
    def get(self, name):
        return self.__setting_dict[name]

# test = setting()
# test.set('file_name', 'test')
# print(test.get('file_name'))
