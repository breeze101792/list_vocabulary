import collections
from language.language import Language

from core.config import AppConfigManager

class FileData:
    def __init__(self, file = None):
        self.file = file
        self.sentence_list = file
        # self.words = None
        self.word_list = []
        self.word_counter = []

        appcgm = AppConfigManager()
        self.language = appcgm.get('variable.language')
        # TODO, Make it configable by language. For now, we ignore the basic english words.
        # A list of common English words that beginners typically know (A1 level approximation).
        self.ignore_list = Language.get_word_list('a1', language = self.language)
    def do_sentence_list(self):
        tmp_list = self.file.replace('\n', ' ').replace('  ', ' ').splitlines()
        tmp = []
        mark_list = ['.','!', '?', ':', '\"', "-", "*"]
        for mark in mark_list:
            tmp = []
            for idx, line in enumerate(tmp_list):
                if mark in line:
                    tmp_sen = line.split(mark)
                    if len(tmp_sen) > 1:
                        tmp.extend(tmp_sen)
                    else:
                        tmp.append(tmp_sen)
                else:
                    tmp.append(line)
            tmp_list = tmp
        self.sentence_list = tmp_list

    @staticmethod
    def word_extractor(word):
        tmp = []
        if word.isalpha() is True:
            return [word]
        # for idx, word in enumerate(sen):2015-12-06t12:45:50+00:00
        while len(word) >= 1 and (word[0].isalpha() is False or word[-1].isalpha() is False):
            # if len(word) == 1 and word.isalpha() is False:
            #     return []
            if word[0].isalpha() is False:
                word = word[1:]
            elif word[-1].isalpha() is False:
                word = word[:-1]
        if len(word) < 1:
            return []
        elif word.count('\'') <= 1 and word.replace('\'', 'z').replace('-', 'z').isalpha() and word != '\'' and word != '-':
            return [word]
        else:
            idx = 0
            wbuf = ''
            #have a bug when "a',"" appear
            while word[idx].isalpha() or word[idx] == '\'' or (word[idx] == '-' and word[idx].isalpha()):
                    idx += 1
            tmp.append(word[0:idx - 1])
            tmp.extend(FileData.word_extractor(word[idx:]))
        return tmp

    def _to_base_form(self, word):
        """
        A simple function to convert a word to its base form based on language.
        This is a basic implementation and focuses on common suffixes.
        It is not a comprehensive stemmer/lemmatizer.
        TODO. add to language class in the future.
        """
        if self.language == 'english':
            # A short list of common irregular verbs.
            # This is not exhaustive but covers many frequent cases.
            irregular_verbs = {
                'got': 'get', 'gotten': 'get',
                'was': 'be', 'were': 'be', 'been': 'be',
                'had': 'have',
                'did': 'do', 'done': 'do',
                'went': 'go', 'gone': 'go',
                'said': 'say',
                'saw': 'see', 'seen': 'see',
                'made': 'make',
                'knew': 'know', 'known': 'know',
                'took': 'take', 'taken': 'take',
                'came': 'come',
                'gave': 'give', 'given': 'give',
                'ate': 'eat', 'eaten': 'eat',
                'ran': 'run',
                'told': 'tell',
                'thought': 'think',
            }
            if word in irregular_verbs:
                return irregular_verbs[word]

            if len(word) < 4:
                return word

            # Verb forms
            if word.endswith('ing'):
                base = word[:-3]
                # # Handles doubled consonants (e.g., running -> run).
                # # NOTE: This can fail on non-verbs like 'wedding' -> 'wedd'.
                # if len(base) > 1 and base[-1] == base[-2] and base[-1] not in 'lsz':
                #     return base[:-1]
                # # Handles silent 'e' (e.g., making -> make).
                # # NOTE: This can fail on non-verbs like 'during' -> 'dure'.
                # vowels = 'aeiou'
                # if len(base) > 2 and base[-1] not in vowels and base[-2] in vowels and base[-3] not in vowels:
                #     return base + 'e'
                return base
            if word.endswith('ed'):
                base = word[:-2]
                # # Handles doubled consonants (e.g., stopped -> stop).
                # # NOTE: This can fail on words like 'shredded' -> 'shredd'.
                # if len(base) > 1 and base[-1] == base[-2] and base[-1] not in 'lsz':
                #     return base[:-1]
                # # Handles silent 'e' (e.g., hoped -> hope).
                # # NOTE: This can fail on adjectives like 'jaded' -> 'jade'.
                # vowels = 'aeiou'
                # if len(base) > 2 and base[-1] not in vowels and base[-2] in vowels and base[-3] not in vowels:
                #     return base + 'e'
                return base

            # Plurals
            if word.endswith('ies'):
                return word[:-3] + 'y'  # e.g., stories -> story

            if word.endswith('es'):
                # Handle plurals for words ending in s, x, z, ch, sh (e.g., buses, boxes, witches)
                if word[:-2].endswith(('s', 'x', 'z')) or word[:-2].endswith(('ch', 'sh')):
                    return word[:-2]

            # Handle most common plural, also handles 3rd person singular verbs (e.g., cats, runs)
            if word.endswith('s') and not word.endswith('ss'):
                # Avoid stripping 's' from short words like 'is', 'as', 'bus'
                if len(word[:-1]) > 2:
                    return word[:-1]

        elif self.language == 'spanish':
            # A short list of common irregular verbs.
            # This is not exhaustive but covers many frequent cases.
            irregular_verbs = {
                'dijo': 'decir', 'dicho': 'decir',
                'hizo': 'hacer', 'hecho': 'hacer',
                'tuvo': 'tener',
                'estuvo': 'estar',
                'pudo': 'poder',
                'puso': 'poner',
                'quiso': 'querer',
                'vino': 'venir',
                'vio': 'ver', 'visto': 'ver',
                'dio': 'dar',
                # 'fue': 'ser',  # Can also be from 'ir'
                'era': 'ser',
            }
            if word in irregular_verbs:
                return irregular_verbs[word]

            # This is a very basic approach for regular Spanish verbs and plurals.
            # It is not a comprehensive lemmatizer and may mis-classify words.
            # It handles some common verb endings and plural nouns, with longer suffixes checked first.

            # --- Verb Conjugations (simple, regular) ---

            # Gerunds (-ando, -iendo)
            if word.endswith('ando'):
                return word[:-4] + 'ar'  # e.g., hablando -> hablar
            if word.endswith('iendo'):
                return word[:-5] + 'er'  # A guess, could also be from an -ir verb

            # Past participles (-ado, -ido)
            if word.endswith('ado'):
                return word[:-3] + 'ar'  # e.g., hablado -> hablar
            if word.endswith('ido'):
                return word[:-3] + 'er'  # A guess, could also be from an -ir verb

            # Present tense endings (plural and tú form)
            # These are less ambiguous than singular forms.
            if word.endswith('an'):
                return word[:-2] + 'ar' # e.g., hablan -> hablar
            if word.endswith('en'):
                return word[:-2] + 'er' # e.g., comen -> comer (could be -ir)
            if word.endswith('as'):
                return word[:-2] + 'ar' # e.g., hablas -> hablar
            if word.endswith('es') and not word.endswith('ces'):
                # This is ambiguous with plural nouns (e.g., 'meses' would become 'meser').
                # A blacklist can help avoid wrong conversions for common nouns.
                noun_blacklist = ['meses', 'reyes', 'leyes', 'interes', 'autobuses']
                if word in noun_blacklist:
                    pass  # Let it be handled by noun plural rules later
                else:
                    # Prioritizing the verb form.
                    return word[:-2] + 'er'  # e.g., comes -> comer (could be -ir)

            # --- Noun Plurals ---
            if len(word) < 3:
                return word

            if word.endswith('ces'):  # e.g., luces -> luz
                return word[:-3] + 'z'
            if word.endswith('es'):
                # e.g., colores -> color. This might catch some verbs incorrectly if not caught above.
                if len(word) > 3 and word[-3] not in 'aeiou':
                    return word[:-2]
            if word.endswith('s'):
                # e.g., casas -> casa. Avoids verbs like 'das'.
                if len(word) > 2 and word[-2] in 'aeiou':
                    return word[:-1]

        return word

    def merge_to_base_form(self, word_counts_map):
        """
        Merges words to their base form using simple suffix-stripping rules.
        For example, 'words' and 'word' will be merged into 'word'.
        The counts of the different forms are summed up.
        """
        if self.language not in ['english', 'spanish']:
            return

        new_word_counts_map = collections.defaultdict(int)
        for word, count in word_counts_map.items():
            base_word = self._to_base_form(word)
            new_word_counts_map[base_word] += count

        # If the base form and the original form are different, and both existed
        # in the original map, their counts will be correctly summed under the base_word key.
        # e.g., if map has {'walk': 2, 'walked': 3}, new map will have {'walk': 5}.

        word_counts_map.clear()
        word_counts_map.update(new_word_counts_map)

    def do_word_list(self, sorting = True):
        # TODO need to find another way to remvoe those symbol except '
        # Note: The initial aggressive replacement of characters like apostrophes
        # might interfere with word_extractor's intended handling of contractions.
        # This part is kept as per original code, but could be a source of issues.
        tmp_words_raw = self.file.replace('>', ' ').replace('<', ' ').replace('.', ' ').replace('?', ' ').replace('!', ' ').replace('.', ' ').replace(',', ' ').replace('\"', ' ').replace('n\'', ' ').replace('\'', ' ').lower().split()

        processed_word_list = []
        for each_word_raw in tmp_words_raw:
            # word_extractor returns a list of words
            processed_word_list.extend(self.word_extractor(each_word_raw))

        # Use a dictionary for efficient word counting
        word_counts_map = collections.defaultdict(int)
        # Use a list to store unique words in their order of first appearance
        unique_words_ordered = []
        # Use a set for efficient checking if a word has already been added to unique_words_ordered
        seen_words_for_order = set()

        for word in processed_word_list:
            # Validate word: must be alphabetic and longer than 2 characters
            if word.isalpha() and len(word) > 2:
                word_counts_map[word] += 1

                # If sorting is False, track the order of first appearance
                if not sorting and word not in seen_words_for_order:
                    unique_words_ordered.append(word)
                    seen_words_for_order.add(word)

        self.merge_to_base_form(word_counts_map)

        # Clear existing lists
        self.word_list = []
        self.word_counter = []

        if sorting:
            # Populate word_list and word_counter with alphabetically sorted words
            sorted_words = sorted(word_counts_map.keys())
            for word in sorted_words:
                if word in self.ignore_list:
                    continue
                self.word_list.append(word)
                self.word_counter.append(word_counts_map[word])
        else:
            # Populate word_list and word_counter with words in their order of first appearance
            for word in unique_words_ordered:
                if word in self.ignore_list:
                    continue
                self.word_list.append(word)
                self.word_counter.append(word_counts_map[word])
    def do_list(self):
        self.sentence_list = self.file.splitlines()
        for line in self.sentence_list:
            print(line + "\n")
        pass
    def word_report(self):
        for voc, times in zip(self.word_list, self.word_counter):
            print(times.__str__().zfill(4), "\t: " + voc)
    def get_word_list(self):
        #return tuple(self.word_list)
        return list(self.word_list)
    def get_freq_list(self):
        return { w:f for w, f in zip(self.word_list, self.word_counter) }
        #return tuple(self.word_list)
        # return list(self.word_counter)
    def get_word_freq(self, word):
        if word in self.word_list:
            return self.word_counter[self.word_list.index(word)]
        return False
