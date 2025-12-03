from enum import Enum, auto
import datetime
import random
import threading
import traceback
import json
import time
import subprocess as sp
import sqlite3
from tabulate import tabulate
from core.config import AppConfigManager

from utility.utils import getch
from utility.debug import *

# from dictionary.hal.ecdict import *
from dictionary.manager import Manager as DictMgr

from core.wordbank import WordBank
from core.data import FileData

from plugins.page.dictpage import DictPage 
from plugins.page.listpage import MemorizeListPage

class Operation:
    def __init__(self, wordbank = None):
        self.wordbank = wordbank
        self.dict_mgr = DictMgr()

    def __ui_print(self, *args):
        print("".join(map(str,args)), end="")
    def __ui_print_line(self, *args):
        print("".join(map(str,args)))

    def __suggest(self, query_word, filter_flag = True):
        # searching in dictionary
        word_list = self.dict_mgr.suggest(query_word)
        if word_list == False:
            dbg_warning("The word haven't been found in dictionary")
            return False
        # self.__ui_print("{} ".format(query_word))
        if word_list:
            return word_list
        else:
            return False
    def __search_word(self, query_word, filter_flag = True):
        # searching in dictionary
        dict_word = self.dict_mgr.search(query_word)
        if dict_word == []:
            dbg_warning("The word haven't been found in dictionary")
            return []
        # searching in databas
        db_word = self.wordbank.get_word(query_word)

        if dict_word:
            # dict_word.show_meaning()
            return dict_word
        else:
            return []

    def op_list_statistic(self, word_list):
        word_set = set()
        level_dict = {}
        for each_level in range(1, 6):
            level_word_list = [ word[0] for word in self.wordbank.quer_for_all_word(familiar = each_level) ]
            level_dict[each_level] = set(level_word_list)
            # tmp_set = set(level_word_list)
            # word_set = word_set | tmp_set

        level_cnt_dict = {1:0, 2:0, 3:0, 4:0, 5:0}
        new_cnt = 0

        for each_word in word_list:
            if each_word in level_dict[1]:
                level_cnt_dict[1] += 1
            elif each_word in level_dict[2]:
                level_cnt_dict[2] += 1
            elif each_word in level_dict[3]:
                level_cnt_dict[3] += 1
            elif each_word in level_dict[4]:
                level_cnt_dict[4] += 1
            elif each_word in level_dict[5]:
                level_cnt_dict[5] += 1
            else:
                new_cnt += 1

        data = []
        data.append([f"All", len(word_list)])
        data.append([f"New", new_cnt])
        data.append([f"Learned", len(word_list) - new_cnt])
        for each_level in range(1, 6):
            if level_cnt_dict[each_level] == 0:
                continue
            data.append([f"Level {each_level}", level_cnt_dict[each_level]])

        headers = ['Statistic', 'Count']
        self.__ui_print_line(tabulate(data, headers=headers, tablefmt="grid"))

    def def_search(self, args):

        dict_word=None
        # dbg_trace(args)
        # arg_dict = ArgParser.args_parser(args)
        arg_dict = args
        arg_key = list(arg_dict.keys())

        # print(arg_dict[arg_key[0]])
        dict_word = self.__search_word(arg_dict[arg_key[0]])
        if dict_word is []:
            word_list = self.__suggest(arg_dict[arg_key[0]])
            if word_list is False:
                return False
            else:
                self.__ui_print_line(word_list)
            # self.__ui_print_line('No such word.')
        else:
            dict_word.show_meaning()
            if self.wordbank.insert(dict_word.word):
                self.wordbank.commit()
            return True
    def search(self, args):

        dict_word_list=None
        # dbg_trace(args)
        # arg_dict = ArgParser.args_parser(args)
        arg_dict = args
        arg_key = list(arg_dict.keys())

        # print(arg_dict[arg_key[0]])
        dict_word_list = self.__search_word(arg_dict[arg_key[1]])
        if len(dict_word_list) > 0:
            dict_word_list[0].show_meaning()
            if self.wordbank.insert(dict_word_list[0].word):
                self.wordbank.commit()
            return True
        else:
            word_list = self.__suggest(arg_dict[arg_key[1]])
            if word_list is False:
                return False
            else:
                self.__ui_print_line(word_list)
            # self.__ui_print_line('No such word.')
    def fuzzy(self, args):
        # dbg_trace(args)
        # arg_dict = ArgParser.args_parser(args)
        arg_dict = args
        arg_key = list(arg_dict.keys())

        # print(arg_dict[arg_key[0]])
        word_list = self.__suggest(arg_dict[arg_key[1]])
        dbg_debug('word list: ', word_list)
        if word_list is False:
            self.__ui_print_line('No such word.')
            return False
        else:
            self.__ui_print_line(word_list)
            return True
    def dump_vocabulary(self, args):

        file_name = ""
        if args['#'] == 1:
            file_name = os.path.abspath(args['1'])

        word_list = self.wordbank.quer_for_all_word()
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    for each_word in word_list:
                        f.write(",".join([each_item.__str__() for each_item in each_word]) + '\n')
                self.__ui_print_line(f"Vocabulary dumped to '{file_name}' successfully.")
            except IOError as e:
                self.__ui_print_line(f"Error writing to file '{file_name}': {e}")
                return False
        else:
            for each_word in word_list:
                self.__ui_print_line(each_word)

        return True
    def cmd_list(self, args):
        appcgm = AppConfigManager()
        list_config = os.path.join(appcgm.get_path('language'),"list.cfg")
        
        # ['do', 'set', 'get']
        flag_action = 'do'
        var_file = ""
        var_type = ""

        for each_idx in range(1, args['#'] + 1):
            if args[str(each_idx)] == 'do':
                flag_action = 'do'
            if args[str(each_idx)] == 'set':
                flag_action = 'set'
            if args[str(each_idx)] == 'stats':
                flag_action = 'stats'

        if 'file' in args:
            var_file = args['file']
        else:
            with open(list_config, 'r') as f:
                var_file = f.readline().strip()

        # if 'type' in args:
        #     ['json', 'sqlite3', 'txt']
        #     var_type = args['type']

        if var_file != "" and var_type == "":
            if var_file.endswith('json'):
                var_type = "json"
            elif var_file.endswith('sqlite3'):
                var_type = "sqlite3"
            else:
                var_type = "text"

        if flag_action == 'set':
            with open(list_config, 'w') as f:
                f.write(var_file + '\n')
        elif flag_action == 'stats':
            self.__ui_print_line(f"type: {var_type}, file: {var_file}")

            new_args = {'#': 0}
            new_args['stats'] = args.get('stats', 'on')

            if var_type == 'text':
                self.cmd_file_input(file = var_file, args = file)
            elif var_type == 'json':
                self.cmd_json_input(file = var_file)
            elif var_type == 'sqlite3':
                self.cmd_vocabs_builder_input(file = var_file, args = new_args)
        elif flag_action == 'do':
            self.__ui_print_line(f"type: {var_type}, file: {var_file}")

            new_args = {'#': 0}
            new_args['stats'] = args.get('stats', 'off')

            if var_type == 'text':
                self.cmd_file_input(file = var_file, args = file)
            elif var_type == 'json':
                self.cmd_json_input(file = var_file)
            elif var_type == 'sqlite3':
                self.cmd_vocabs_builder_input(file = var_file, args = new_args)

        return True

    def cmd_statistic(self, args):
        # {1: 75, 2: 153, 3: 0, 4: 0, 5: 0}
        stats = self.wordbank.query_for_statistic()

        other_new_count = len(self.wordbank.quer_for_all_word(familiar = 0, today_new_words = True))
        new_count = len(self.wordbank.quer_for_all_word(today_new_words = True)) - other_new_count

        other_forgotten_count = len(self.wordbank.quer_for_all_word(familiar = 0, forgotten = True))
        forgotten_count = len(self.wordbank.quer_for_all_word(forgotten = True)) - other_forgotten_count

        other_reviewed_count = len(self.wordbank.quer_for_all_word(familiar = 0, reviewed = True))
        reviewed_count = len(self.wordbank.quer_for_all_word(reviewed = True)) - other_reviewed_count

        data = list()
        for key in stats.keys():
            if stats[key] == 0:
                continue
            data.append([f'Level {key}', stats[key]])

        data.append([f"Reviewed", reviewed_count])
        data.append([f"New", new_count])
        data.append([f"Forgotten", forgotten_count])
        headers = ['Title', 'Count']

        # tabulate creates a nice table
        print(tabulate(data, headers=headers, tablefmt="grid"))

        # print(stats)
        # print(new_count)
        # print(forgotten_count)
        return True
    def cmd_search_dictionary(self, args = None):
        page_dict = DictPage(self.wordbank)

        page_dict.run()

        return True
    def cmd_memorize_words(self, args = None):
        title = "Vocabulary Builder"
        word_idx = 0
        times_idx = 1
        familiar_idx = 2
        timestamp_idx = 3

        familiar_target = 1
        times_target = -1
        list_number = 0
        flag_reverse = False
        flag_meaning = False
        # default not show reviewed words.
        flag_reviewed_word = False
        flag_forgotten_word = None
        flag_new_word = None
        review_interval = 0

        for each_idx in range(1, args['#'] + 1):
            if args[str(each_idx)] == 'reverse':
                flag_reverse = True

            if args[str(each_idx)] == 'new':
                flag_new_word = True
                flag_reviewed_word = True
                flag_meaning = True
                title = "New Words"

            if args[str(each_idx)] == 'forgotten':
                flag_forgotten_word = True
                flag_reviewed_word = True
                flag_meaning = True
                title = "Forgotten Words"

            if args[str(each_idx)] == 'review':
                list_number = 50
                familiar_target = 2
                flag_forgotten_word = None
                flag_reviewed_word = None
                flag_meaning = False
                title = "Review Words"
                review_interval = 7

        if 'familiar' in args:
            familiar_target = int(args['familiar'])

        if 'times' in args:
            times_target = int(args['times'])

        if 'number' in args:
            list_number = int(args['number'])

        if 'interval' in args:
            review_interval = int(args['interval'])

        # dbg_info("Change familiar level to {}.".format(familiar_target))

        word_list = []
        for each_word in self.wordbank.quer_for_all_word(familiar = familiar_target, forgotten = flag_forgotten_word, today_new_words = flag_new_word):
            if len(each_word) < 3:
                continue
            if times_target != -1 and each_word[times_idx] > times_target:
                continue

            if review_interval > 0:
                today_date = datetime.now().date()
                word_date = datetime.fromtimestamp(each_word[timestamp_idx]).date()
                if (today_date - word_date).days < review_interval:
                    continue

            if each_word[familiar_idx] == familiar_target:
                word_list.append(each_word[word_idx])

        if flag_reverse is True:
            word_list.reverse()

        if list_number != 0 and list_number < len(word_list):
            word_list = word_list[-list_number:]

        list_page = MemorizeListPage(wordlist = word_list, wordbank = self.wordbank, title = title, reviewed = flag_reviewed_word, meaning = flag_meaning, announce = True, shuffle = True)
        list_page.run()

        return True
    def cmd_forgotten_words(self, args = None):
        word_idx = 0
        times_idx = 1
        familiar_idx = 2
        forgotten_idx = 3

        familiar_target = 1
        list_number = 0

        if 'familiar' in args:
            familiar_target = int(args['familiar'])

        if 'number' in args:
            list_number = int(args['number'])

        word_list = []
        for each_word in self.wordbank.quer_for_all_word(familiar = familiar_target, forgotten = True):
            if len(each_word) < 3:
                continue
            if each_word[familiar_idx] == familiar_target:
                word_list.append(each_word[word_idx])

        if list_number != 0 and list_number < len(word_list):
            word_list = word_list[-list_number:]

        list_page = MemorizeListPage(wordlist = word_list, wordbank = self.wordbank, title = 'Forgotten Words.', meaning = True, announce = True, shuffle = True)
        list_page.run()

        return True
    def cmd_new_words(self, args = None):
        word_idx = 0
        times_idx = 1
        familiar_idx = 2
        forgotten_idx = 3

        familiar_target = 1

        if 'familiar' in args:
            familiar_target = int(args['familiar'])

        word_list = []
        for each_word in self.wordbank.quer_for_all_word(familiar = familiar_target, today_new_words = True):
            if len(each_word) < 3:
                continue
            if each_word[familiar_idx] == familiar_target:
                word_list.append(each_word[word_idx])

        list_page = MemorizeListPage(wordlist = word_list, wordbank = self.wordbank, title = 'New Words.', meaning = True, announce = True, shuffle = True)
        list_page.run()

        return True
    def cmd_text_input(self, args = None):
        input_lines = []
        self.__ui_print_line("Enter word list (press Enter on an empty line to finish):")
        while True:
            line = input()
            if not line:
                break
            input_lines.append(line)
        text = "\n".join(input_lines)

        # self.__ui_print_line(text)
        file_data = FileData(text)
        file_data.do_word_list(sorting = False)

        # self.__listing_word(file_data.word_list, file_data.word_counter)

        # dbg_info(f"Len of list: {len(file_data.word_list)}", file_data.word_list)
        list_page = MemorizeListPage(wordlist = file_data.word_list, wordbank = self.wordbank, title = "Text vocabs.")

        list_page.run()

        return True
    def cmd_file_input(self, args = None, file = None):
        file_name = ""
        flag_stats = False
        if file is not None:
            file_name = file

        if args is not None:
            if args['#'] == 1:
                file_name = args['1']
                if file_name == "sample":
                    file_name = "./data/i_have_a_dream.txt"
            # else:
            #     self.__ui_print_line(f"Error: No file specified.")
            #     return False

            if 'stats' in args:
                switch = args['stats']
                if switch == 'on':
                    flag_stats = True
                else:
                    flag_stats = False
            else:
                flag_stats = False

        # read file
        if not os.path.exists(file_name):
            self.__ui_print_line(f"Error: File '{file_name}' not found.")
            return False
        # file_name = "/mnt/data/workspace/code/list_vocabulary/data/i_have_a_dream.txt"
        # self.__ui_print_line(file_name)
        file_raw = open(file_name)
        text = file_raw.read()
        file_raw.close()

        # self.__ui_print_line(text)
        file_data = FileData(text)
        file_data.do_word_list()

        if flag_stats:
            self.op_list_statistic(word_list)
        else:
            list_page = MemorizeListPage(wordlist = file_data.word_list, wordbank = self.wordbank, title = "File vocabs.")
            list_page.run()

        return True
    def cmd_vocabs_builder_input(self, args = None, file = None):
        file_name = ""
        flag_stats = False
        if file is not None:
            file_name = file

        if args is not None:
            if args['#'] == 1:
                file_name = args['1']
            # else:
            #     self.__ui_print_line(f"Error: No file specified.")
            #     return False

            if 'stats' in args:
                switch = args['stats']
                if switch == 'on':
                    flag_stats = True
                else:
                    flag_stats = False
            else:
                flag_stats = False


        # for koreader.
        con = sqlite3.connect(file_name)
        cur = con.cursor()
        word_list = []
        for word, prev_context, next_context in cur.execute("SELECT word, prev_context, next_context FROM vocabulary;"):
            word_list.append(word)
        con.close()

        if flag_stats:
            self.op_list_statistic(word_list)
        else:
            list_page = MemorizeListPage(wordlist = word_list, wordbank = self.wordbank, title = "Vocabs Builder.")
            list_page.run()

        return True
    def cmd_json_input(self, args = None, file = None):
        file_name = ""
        if file is not None:
            file_name = file

        if args is not None:
            if args['#'] == 1:
                file_name = args['1']
            # else:
            #     self.__ui_print_line(f"Error: No file specified.")
            #     return False

        # read file
        if not os.path.exists(file_name):
            self.__ui_print_line(f"Error: File '{file_name}' not found.")
            return False

        try:
            # setup customize dictionary
            self.dict_mgr.word_list_dict.cleanAll()
            self.dict_mgr.word_list_dict.buildDict(file_name)

            # # read word list.
            # file_raw = open(file_name)
            # text = file_raw.read()
            # file_raw.close()
            json_word_list = []
            with open(file_name, "r", encoding="utf-8") as jfile:
                # Load the entire JSON file as a list of entries
                data = json.load(jfile)
                for entry in data:
                    word = entry["word"]
                    json_word_list.append(word)

            list_page = MemorizeListPage(wordlist = json_word_list, wordbank = self.wordbank, title = 'Json Words.', meaning = True)
            list_page.run()

        except Exception as e:
            dbg_error(e)

            traceback_output = traceback.format_exc()
            dbg_error(traceback_output)
        finally:
            self.dict_mgr.word_list_dict.cleanAll()
        return True

