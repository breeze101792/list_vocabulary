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
        self.freq_dict = {}

        # post init
        self.cmd_freq(enable=True)

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
        for each_level in range(0, 6):
            level_word_list = [ word[0] for word in self.wordbank.quer_for_all_word(familiar = each_level) ]
            level_dict[each_level] = set(level_word_list)
            # tmp_set = set(level_word_list)
            # word_set = word_set | tmp_set

        level_cnt_dict = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0}
        new_cnt = 0

        for each_word in word_list:
            if each_word in level_dict[0]:
                level_cnt_dict[0] += 1
            elif each_word in level_dict[1]:
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
        data.append([f"Others", level_cnt_dict[0]])

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
        elif os.path.exists(list_config):
            with open(list_config, 'r') as f:
                var_file = f.readline().strip()
        else:
            self.__ui_print_line("Please specify file first")
            return False

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
                self.cmd_file_input(file = var_file, args = new_args)
            elif var_type == 'json':
                self.cmd_json_input(file = var_file, args = new_args)
            elif var_type == 'sqlite3':
                self.cmd_vocabs_builder_input(file = var_file, args = new_args)
        elif flag_action == 'do':
            self.__ui_print_line(f"type: {var_type}, file: {var_file}")

            new_args = {'#': 0}
            new_args['stats'] = args.get('stats', 'off')
            new_args['freq'] = "on"
            new_args['reviewed'] = "off"
            new_args['known'] = "off"

            if var_type == 'text':
                self.cmd_file_input(file = var_file, args = new_args)
            elif var_type == 'json':
                self.cmd_json_input(file = var_file, args = new_args)
            elif var_type == 'sqlite3':
                self.cmd_vocabs_builder_input(file = var_file, args = new_args)

        return True

    def cmd_statistic(self, args):
        flag_action = 'all'
        target_familiar = 1

        for each_idx in range(1, args['#'] + 1):
            if args[str(each_idx)] == 'times':
                flag_action = 'times'
        if 'familiar' in args:
            target_familiar = int(args['familiar'])

        data = list()
        if flag_action == 'all':

            # {1: 75, 2: 153, 3: 0, 4: 0, 5: 0}
            stats = self.wordbank.query_for_statistic()

            other_new_count = len(self.wordbank.quer_for_all_word(familiar = 0, today_new_words = True))
            new_count = len(self.wordbank.quer_for_all_word(today_new_words = True)) - other_new_count

            other_forgotten_count = len(self.wordbank.quer_for_all_word(familiar = 0, forgotten = True))
            forgotten_count = len(self.wordbank.quer_for_all_word(forgotten = True)) - other_forgotten_count

            other_reviewed_count = len(self.wordbank.quer_for_all_word(familiar = 0, reviewed = True))
            reviewed_count = len(self.wordbank.quer_for_all_word(reviewed = True)) - other_reviewed_count

            other_count = len(self.wordbank.quer_for_all_word(familiar = 0))

            for key in stats.keys():
                if stats[key] == 0:
                    continue
                data.append([f'Level {key}', stats[key]])

            data.append([f'Others', other_count])

            data.append([f"Reviewed", reviewed_count])
            data.append([f"New", new_count])
            data.append([f"Forgotten", forgotten_count])
        else:
            times_idx = 1

            stats = self.wordbank.query_for_statistic()
            data.append([f'Level {target_familiar}', stats[target_familiar]])

            for idx in range(6):
                times_count = len(self.wordbank.quer_for_all_word(familiar = target_familiar, times = idx))

                data.append([f'Times {idx}', times_count])

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

    ## Vocabulary
    def cmd_vocabulary(self, args = None):
        # TODO, move it out to be a class.
        title = "Vocabulary Builder"
        word_idx = 0
        times_idx = 1
        familiar_idx = 2
        timestamp_idx = 3

        familiar_target = 1
        times_target = -1
        list_number = 0

        ## flags
        flag_reverse = False
        flag_meaning = False
        flag_llm_search = False

        # default not show reviewed words.
        flag_reviewed_word = False
        flag_reinforce_memorize = False
        flag_forgotten_word = None
        flag_new_word = None

        review_interval = 0
        reinforce_interval = [{}, {0:1, 1:1, 2:1, 3:1, 4:2, 5:3}, {0:7, 1:7, 2:15, 3:30}]

        for each_idx in range(1, args['#'] + 1):
            if args[str(each_idx)] == 'llm':
                flag_llm_search = True

            if args[str(each_idx)] == 'meaning':
                flag_meaning = True

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

            if args[str(each_idx)] == 'reinforce':
                familiar_target = 1
                title = "Reinforce Memorize"
                flag_reinforce_memorize = True

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
            word_familiar = int(each_word[familiar_idx])
            word_times = int(each_word[times_idx])
            if times_target != -1 and word_times > times_target:
                continue

            if review_interval > 0:
                today_date = datetime.now().date()
                word_date = datetime.fromtimestamp(each_word[timestamp_idx]).date()
                if (today_date - word_date).days < review_interval:
                    continue

            if flag_reinforce_memorize is True and familiar_target in {1, 2}:
                today_date = datetime.now().date()
                word_date = datetime.fromtimestamp(each_word[timestamp_idx]).date()
                if (today_date - word_date).days < reinforce_interval[word_familiar][word_times]:
                    continue

            if word_familiar == familiar_target:
                word_list.append(each_word[word_idx])

        if flag_reverse is True:
            word_list.reverse()

        if list_number != 0 and list_number < len(word_list):
            word_list = word_list[-list_number:]

        list_page = MemorizeListPage(wordlist = word_list, wordbank = self.wordbank, title = title, reviewed = flag_reviewed_word, meaning = flag_meaning, announce = True, shuffle = True, llm_search = flag_llm_search)
        list_page.run()

        return True

    def cmd_reinforce_words(self, args = None):

        arg_idx = args['#'] + 1
        args[str(arg_idx)] = 'reinforce'
        args['#'] = arg_idx
        self.cmd_vocabulary(args)
        return True
    def cmd_review_words(self, args = None):

        arg_idx = args['#'] + 1
        args[str(arg_idx)] = 'review'
        args['#'] = arg_idx
        self.cmd_vocabulary(args)
        return True
    def cmd_forgotten_words(self, args = None):

        arg_idx = args['#'] + 1
        args[str(arg_idx)] = 'forgotten'
        args['#'] = arg_idx
        self.cmd_vocabulary(args)
        return True
    def cmd_new_words(self, args = None):
        arg_idx = args['#'] + 1
        args[str(arg_idx)] = 'new'
        args['#'] = arg_idx

        # current disable it.
        # arg_idx += 1
        # args[str(arg_idx)] = 'llm'
        # args['#'] = arg_idx
        self.cmd_vocabulary(args)
        return True

    ## Frequency
    def cmd_freq(self, args = None, enable = None):
        flag_action = ""
        file_name = ""
        freq_list_name = 'freq.list'
        if enable is not None:
            if enable is True:
                flag_action = 'enable'
            else:
                flag_action = 'disable'

        if args is not None:
            if args['#'] == 1:
                optons = args['1']
                if optons == "show":
                    flag_action = optons
                elif optons == "enable":
                    flag_action = optons
                elif optons == "disable":
                    flag_action = optons
                # elif optons == "set":
                #     flag_action = optons
                #     self.__ui_print_line("Use default freq list.")
                #     file_name = "./data/i_have_a_dream.txt"
            elif args['#'] == 2:
                optons = args['1']
                if optons == "set":
                    file_name = args['2']
                    flag_action = 'set'

        if flag_action == 'set':
            # read file
            if not os.path.exists(file_name):
                self.__ui_print_line(f"Error: File '{file_name}' not found.")
                return False

            # self.__ui_print_line(file_name)
            file_raw = open(file_name)
            text = file_raw.read()
            file_raw.close()

            # self.__ui_print_line(text)
            file_data = FileData(text)
            file_data.do_word_list()

            appcgm = AppConfigManager()
            output_file = os.path.join(appcgm.get_path('language'),freq_list_name)
            self.freq_dict = file_data.get_freq_list()
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    # sort by it's value before write it out.
                    sorted_freq_items = sorted(self.freq_dict.items(), key=lambda item: item[1], reverse=True)
                    for word, freq in sorted_freq_items:
                        f.write(f"{word},{freq}\n")
                self.__ui_print_line(f"Frequency list updated to '{output_file}' successfully.")
            except IOError as e:
                self.__ui_print_line(f"Error writing to file '{output_file}': {e}")
                return False
        elif flag_action == 'enable':
            self.freq_dict = {}
            appcgm = AppConfigManager()
            input_file = os.path.join(appcgm.get_path('language'),freq_list_name)
            if os.path.exists(input_file):
                try:
                    with open(input_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            parts = line.strip().split(',')
                            if len(parts) == 2:
                                word, freq = parts[0], int(parts[1])
                                self.freq_dict[word] = freq
                    self.__ui_print_line(f"Frequency list loaded from '{input_file}' successfully.")
                except IOError as e:
                    dbg_error(f"Error reading from file '{input_file}': {e}")
                    return False
                except ValueError:
                    dbg_error(f"Error parsing frequency in '{input_file}'. Ensure frequency is an integer.")
                    return False
            # else:
            #     dbg_error(f"Frequency list file '{input_file}' not found. Frequency feature disabled.")
        elif flag_action == 'disable':
            self.freq_dict = {}
            self.__ui_print_line(f"Reset freq list.")
        elif flag_action == 'show':
            if self.freq_dict:
                word_list = [ word for word,freq in self.freq_dict.items() ]
                self.__list_word(wordlist = word_list, title = "Freq words.", args = args)
            else:
                self.__ui_print_line("Freq list is empty.")
        else:
            self.__ui_print_line(f"No options specify.")

        return True
    def cmd_freq_cmp(self, args = None, enable = None):

        # flags
        flag_action = "list"

        # variables
        target_file_name = ""

        db_file = ""
        db_freq_threshold = 10
        freq_list_name = 'freq.list'

        ## Args
        for each_idx in range(1, args['#'] + 1):
            each_args = args[str(each_idx)]

            if each_args in ['list', 'save']:
                flag_action = each_args
            else:
                target_file_name=each_args


        if 'freq' in args:
            db_freq_threshold = int(args['freq'])

        ## Proccess
        if not os.path.exists(target_file_name):
            self.__ui_print_line(f"Error: File '{target_file_name}' not found.")
            return False

        # db file
        db_freq_dict = dict()
        if db_file != "":
            if not os.path.exists(target_file_name):
                self.__ui_print_line(f"Error: File '{target_file_name}' not found.")
                return False
            file_raw = open(target_file_name)
            text = file_raw.read()
            file_raw.close()


            db_file_data = FileData(text)
            db_file_data.do_word_list()

        elif self.freq_dict:
            db_freq_dict = self.freq_dict
        else:
            print("Please sepcify freq list/file.")
            return False

        # target file
        file_raw = open(target_file_name)
        text = file_raw.read()
        file_raw.close()

        file_data = FileData(text)
        file_data.do_word_list()
        target_freq_dict = file_data.get_freq_list()

        # sorting dict.
        # sorted_db_freq_items = sorted(db_freq_dict.items(), key=lambda item: item[1], reverse=True)
        sorted_tgt_freq_items = sorted(target_freq_dict.items(), key=lambda item: item[1], reverse=True)

        # debug
        # print(sorted_db_freq_items[:5])
        # print(sorted_tgt_freq_items[:5])
        

        if flag_action == 'list':
            word_list = []
            for each_item in sorted_tgt_freq_items:
                word = each_item[0]

                word_db_freq = db_freq_dict.get(word, 0)
                # use smaller then , so we filter out the word with freq more then target.
                # and the target we already knows/memorized.
                if word_db_freq < db_freq_threshold:
                    word_list.append(word)

            self.__list_word(wordlist = word_list, title = f"Freq Compare List (threshold: {db_freq_threshold})", args = args)
        elif flag_action == 'save':
            output_file = target_file_name + ".list"

            with open(output_file, 'w', encoding='utf-8') as f:
                for word, freq in sorted_tgt_freq_items:
                    word_db_freq = db_freq_dict.get(word, 0)
                    if word_db_freq < db_freq_threshold:
                        f.write(f"{word},{freq}\n")
            print(f"File save to : {output_file}")
        else:
            print(f"Unkonwn options.{flag_action}")
            return False

        return True

    ## Input
    def __list_word(self, wordlist, title = "Word List", customize_freq_dict = None, args = None):
        flag_stats = False
        flag_freq_sort = False
        flag_reviewed = True
        flag_known = True
        sort_freq_dict = {}

        if args is not None:
            if 'stats' in args:
                switch = args['stats']
                if switch == 'on':
                    flag_stats = True
                else:
                    flag_stats = False

            if 'freq' in args:
                switch = args['freq']
                if switch == 'on':
                    flag_freq_sort = True
                    print("Using system freq dict list")
                    sort_freq_dict = self.freq_dict
                elif switch == 'file':
                    print("Using file freq dict list")
                    flag_freq_sort = True
                    sort_freq_dict = customize_freq_dict
                else:
                    flag_freq_sort = False

            if 'reviewed' in args:
                switch = args['reviewed']
                if switch == 'on':
                    flag_reviewed = True
                else:
                    flag_reviewed = False
            if 'known' in args:
                switch = args['known']
                if switch == 'on':
                    flag_known = True
                else:
                    flag_known = False

        # Sort wordlist by frequency if sort_freq_dict is available
        if sort_freq_dict and flag_freq_sort:
            # Assign a default frequency of 0 to words not founfreq_dict
            wordlist.sort(key=lambda word: sort_freq_dict.get(word, 0), reverse=True)

        if flag_stats:
            self.op_list_statistic(wordlist)
        else:
            list_page = MemorizeListPage(wordlist = wordlist, wordbank = self.wordbank, title = title, reviewed = flag_reviewed, known = flag_known, freq_dict = sort_freq_dict)
            list_page.run()

    def cmd_text_input(self, args = None):
        input_lines = [""]
        self.__ui_print_line("Enter word list (press Enter on an empty line to finish):")
        while True:
            line = input()
            if not line:
                break
            input_lines.append(line)
        text = "\n".join(input_lines)

        self.__ui_print_line(text)
        file_data = FileData(text)
        file_data.do_word_list(sorting = False)

        self.__list_word(wordlist = file_data.word_list, title = "Text vocabs.", args = args)

        return True
    def cmd_file_input(self, args = None, file = None):
        file_name = ""

        if file is not None:
            file_name = file

        if args is not None:
            if args['#'] == 1:
                file_name = args['1']
                if file_name == "sample":
                    file_name = "./data/i_have_a_dream.txt"

        # read file
        if not os.path.exists(file_name):
            self.__ui_print_line(f"Error: File '{file_name}' not found.")
            return False

        # self.__ui_print_line(file_name)
        file_raw = open(file_name)
        text = file_raw.read()
        file_raw.close()

        # self.__ui_print_line(text)
        file_data = FileData(text)
        file_data.do_word_list()

        self.__list_word(wordlist = file_data.word_list, title = "File vocabs.", customize_freq_dict = file_data.get_freq_list(), args = args)

        return True
    def cmd_vocabs_builder_input(self, args = None, file = None):
        file_name = ""
        if file is not None:
            file_name = file

        if args is not None:
            if args['#'] == 1:
                file_name = args['1']

        # for koreader.
        con = sqlite3.connect(file_name)
        cur = con.cursor()
        word_list = []
        for word, prev_context, next_context in cur.execute("SELECT word, prev_context, next_context FROM vocabulary;"):
            word_list.append(word)
        con.close()

        self.__list_word(wordlist = word_list, title = "Vocabs builder.", args = args)

        return True
    def cmd_json_input(self, args = None, file = None):
        file_name = ""
        if file is not None:
            file_name = file

        if args is not None:
            if args['#'] == 1:
                file_name = args['1']

        # read file
        if not os.path.exists(file_name):
            self.__ui_print_line(f"Error: File '{file_name}' not found.")
            return False

        try:
            # setup customize dictionary
            self.dict_mgr.word_list_dict.cleanAll()
            self.dict_mgr.word_list_dict.buildDict(file_name)

            # # read word list.
            json_word_list = []
            with open(file_name, "r", encoding="utf-8") as jfile:
                # Load the entire JSON file as a list of entries
                data = json.load(jfile)
                for entry in data:
                    word = entry["word"]
                    json_word_list.append(word)

            self.__list_word(wordlist = json_word_list, title = "Json Words", args = args)

        except Exception as e:
            dbg_error(e)

            traceback_output = traceback.format_exc()
            dbg_error(traceback_output)
        finally:
            self.dict_mgr.word_list_dict.cleanAll()
        return True

