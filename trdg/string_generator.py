import random as rnd
import re
import string
import requests

from bs4 import BeautifulSoup

import copy

def create_strings_from_file(filename, count):
    """
        Create all strings by reading lines in specified files
    """

    strings = []

    with open(filename, "r", encoding="utf8") as f:
        lines = [l[0:200] for l in f.read().splitlines() if len(l) > 0]
        if len(lines) == 0:
            raise Exception("No lines could be read in file")
        while len(strings) < count:
            if len(lines) >= count - len(strings):
                strings.extend(lines[0 : count - len(strings)])
            else:
                strings.extend(lines)

    return strings


def create_strings_from_dict(length, allow_variable, count, lang_dict):
    """
        Create all strings by picking X random word in the dictionnary
    """

    dict_len = len(lang_dict)
    strings = []
    for _ in range(0, count):
        current_string = ""
        for _ in range(0, rnd.randint(1, length) if allow_variable else length):
            current_string += lang_dict[rnd.randrange(dict_len)]
            current_string += " "
        strings.append(current_string[:-1])
    return strings


def create_strings_from_wikipedia(minimum_length, count, lang):
    """
        Create all string by randomly picking Wikipedia articles and taking sentences from them.
    """
    sentences = []

    while len(sentences) < count:
        # We fetch a random page
        page = requests.get("https://{}.wikipedia.org/wiki/Special:Random".format(lang))

        soup = BeautifulSoup(page.text, "html.parser")

        for script in soup(["script", "style"]):
            script.extract()

        # Only take a certain length
        lines = list(
            filter(
                lambda s: len(s.split(" ")) > minimum_length
                and not "Wikipedia" in s
                and not "wikipedia" in s,
                [
                    " ".join(re.findall(r"[\w']+", s.strip()))[0:200]
                    for s in soup.get_text().splitlines()
                ],
            )
        )

        # Remove the last lines that talks about contributing
        sentences.extend(lines[0 : max([1, len(lines) - 5])])

    return sentences[0:count]


def create_strings_randomly(length, allow_variable, count, let, num, sym, lang):
    """
        Create all strings by randomly sampling from a pool of characters.
    """

    # If none specified, use all three
    if True not in (let, num, sym):
        let, num, sym = True, True, True

    pool = ""
    if let:
        if lang == "cn":
            pool += "".join(
                [chr(i) for i in range(19968, 40908)]
            )  # Unicode range of CHK characters
        else:
            pool += string.ascii_letters
    if num:
        pool += "0123456789"
    if sym:
        pool += "!\"#$%&'()*+,-./:;?@[\\]^_`{|}~"

    if lang == "cn":
        min_seq_len = 1
        max_seq_len = 2
    else:
        min_seq_len = 2
        max_seq_len = 10

    strings = []
    for _ in range(0, count):
        current_string = ""
        for _ in range(0, rnd.randint(1, length) if allow_variable else length):
            seq_len = rnd.randint(min_seq_len, max_seq_len)
            current_string += "".join([rnd.choice(pool) for _ in range(seq_len)])
            current_string += " "
        strings.append(current_string[:-1])
    return strings

def _num_generator():
    while True:
        rand = rnd.random()
        if rand < 0.1:
            number = '{:,.2f}'.format(rnd.randint(0, 1e3) / 100)
        elif 0.1 <= rand <0.4:
            if rand < 0.7:
                number = '{:,}'.format(rnd.randint(0,1e3))
            else:
                number = '{:,.2f}'.format(rnd.randint(0, 1e5) / 100)
        elif 0.4 <= rand < 0.7:
            if rand < 0.7:    
                number = '{:,}'.format(rnd.randint(0,1e6))
            else:
                number = '{:,}'.format(rnd.randint(0,1e8) / 100)
        elif 0.7 <= rand <= 0.95:
            if rand < 0.7:
                number = '{:,}'.format(rnd.randint(0,1e9))
            else:
                number = '{:,}'.format(rnd.randint(0,1e11) / 100)
        else:
            if rand < 0.7:
                number = '{:,}'.format(rnd.randint(0,1e12))
            else:
                number = '{:,}'.format(rnd.randint(0,1e11) / 100)
        if rand < 0.1:
            number = '-' + number
        elif 0.1 <= rand < 0.4:
            number = '(' + number + ')'
        yield number


class CH_GENERATOR():

    
    def __init__(self, file=None):
        self.file = file
        if self.file is not None:
            with open(file, 'r') as f:
                self.data = list(f.read().split('\n'))

    def __iter__(self):
        return self

    def __next__(self):
        if self.file is not None:
            return self.data[rnd.randint(0, len(self.data) - 1)]
        else:
            text = ''
            for _ in range(rnd.randint(1,4)):
                text += chr(rnd.randint(19968, 40908))
            return text

class EN_GENERATOR():


    def __init__(self, file=None):
        self.file = file
        if self.file is not None:
            with open(file, 'r') as f:
                self.data = list(f.read().split('\n'))

    def __iter__(self):
        return self

    def __next__(self):
        if self.file is not None:
            return self.data[rnd.randint(0, len(self.data) - 1)]
        else:
            text = ''
            for _ in range(rnd.randint(2,12)):
                text += string.ascii_letters[rnd.randint(0, 51)]
            return text

def _sym_generator():
    while True:
        yield string.punctuation[rnd.randint(0, 3)]



class ControlledRandomStringsGenerator:


    def __init__(self, length, allow_variable, count, lang_mix, next_lang_stickness, ch_file=None, en_file=None):
        self.length = length
        self.allow_variable = allow_variable
        self.count = count
        self.lang_mix = lang_mix
        self.next_lang_stickness = next_lang_stickness
        self.ch_gen = CH_GENERATOR(ch_file)
        self.en_gen = EN_GENERATOR(en_file)
        self.num_gen = _num_generator()
        self.sym_gen = _sym_generator()
    
    @staticmethod
    def _sample_from_dict(pool_input, length, next_lang_stickness):
        pool = copy.deepcopy(pool_input)
        state_history = []
        text_list = []
        while len(state_history) < length or sum([len(i) for i in pool.values()]) != 0:
            if len(state_history) == 0:
                current_state = rnd.choice(['cn', 'en', 'num', 'sym'])
                state_history.append(current_state)
                text_list.append(pool[current_state].pop(0))
            else:
                if (rnd.random() < next_lang_stickness and len(pool[state_history[-1]]) > 0):
                    current_state = state_history[-1]
                else:
                    #only include non-empty list
                    next_action_set = list([k for k,v in pool.items() if len(v)>0 and k != state_history[-1]]) 
                    if len(next_action_set) == 0:
                        break
                    current_state = rnd.choice(next_action_set)
                state_history.append(current_state)
                text_list.append(pool[current_state].pop(0))
        return ' '.join(text_list)
    
    def pool_setup(self):
        assert 'cn' in self.lang_mix and 'en' in self.lang_mix and 'num' in self.lang_mix and 'sym' in self.lang_mix
        cn_length = self.length * self.lang_mix['cn']
        en_length = self.length * self.lang_mix['en']
        num_length = self.length * self.lang_mix['num']
        sym_length = self.length * self.lang_mix['sym']
        cn_pool = []
        while len(cn_pool) < cn_length:
            cn_pool.append(next(self.ch_gen))
        en_pool = []
        while len(en_pool) < en_length:
            en_pool.append(next(self.en_gen))
        num_pool = []
        while len(num_pool) < num_length:
            num_pool.append(next(self.num_gen))
        sym_pool = []
        while len(sym_pool) < sym_length:
            sym_pool.append(next(self.sym_gen))
        return {'cn': cn_pool, 'en': en_pool, 'num': num_pool, 'sym': sym_pool}

    def generate(self):
        """
            Create all strings by randomly sampling from a pool of characters.
            lang_mix = {'cn': 0.5,
                        'en': 0.1,
                        'num': 0.2,
                        'sym': 0.2}
        """
        strings = []
        for _ in range(0, self.count):
            pool = self.pool_setup()
            if self.allow_variable:
                current_string = self._sample_from_dict(pool, rnd.randint(1, self.length), self.next_lang_stickness)
            else:
                current_string = self._sample_from_dict(pool, self.length, self.next_lang_stickness)
            strings.append(current_string)
        return strings

