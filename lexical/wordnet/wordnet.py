import os
import logging
import re
from typing import Any, List, Tuple
log = logging.getLogger(__name__)

class WordNetHandler:
    '''The WordNetHandler class loads wordnet database files into memory and provides methods for looking up words.
    methods:
        lookup
        lookup_v2
    '''

    def __init__(self, wordnet_path):
        self.wordnet_path = wordnet_path
        self._exc = {
            'a': {},
            'n': {},
            'v': {},
            'r': {},
            's': {},
        }
        self._index = {
            'a': {},
            'n': {},
            'v': {},
            'r': {},
            's': {},
        }
        self._data = {
            'a': {},
            'n': {},
            'v': {},
            'r': {},
            's': {},
        }
        self._char_to_pos = {
            'a': 'adj',
            'n': 'noun',
            'v': 'verb',
            'r': 'adv',
            's': 'adj_s'
        }
        self._pos_to_ss_type = {
            'adj': 'a',
            'adv': 'r',
            'noun': 'n',
            'verb': 'v',
            'adj_s': 's',
        }

        self.morph_ruleset = [
            ('n', 'regular plurals', r'(.+?)ies$', r'\1y'),               # babies → baby, flies → fly
            ('n', 'regular plurals', r'(.+?)([sxz]|[cs]h)es$', r'\1\2'),  # boxes → box, wishes → wish
            ('n', 'regular plurals', r'(.+?)s$', r'\1'),                  # cats → cat
            ('v', 'third person', r'(.+?)ies$', r'\1y'),                  # tries → try
            ('v', 'third person', r'(.+?)([sxz]|[cs]h)es$', r'\1\2'),     # passes → pass
            ('v', 'third person', r'(.+?)s$', r'\1'),                     # walks → walk
            ('v', 'past tense', r'(.+?)ied$', r'\1y'),                    # tried → try
            ('v', 'past tense', r'(.+?)ed$', r'\1'),                      # played → play
            ('v', 'past tense', r'(.+?)([b-df-hj-np-tv-z])\2ed$', r'\1\2'),  # stopped → stop
            ('v', 'present participle', r'(.+?)ying$', r'\1ie'),          # lying → lie
            ('v', 'present participle', r'(.+?)ing$', r'\1'),             # running → run
            ('v', 'present participle', r'(.+?)([b-df-hj-np-tv-z])\2ing$', r'\1\2'),  # stopping → stop
            ('a', 'comparative & superlative', r'(.+?)iest$', r'\1y'),    # happiest → happy
            ('a', 'comparative & superlative', r'(.+?)er$', r'\1'),       # bigger → big
            ('a', 'comparative & superlative', r'(.+?)est$', r'\1'),      # biggest → big
            # happier? TODO: need to expand to a complete ruleset
        ]

        # Load wordnet database
        # exceptions[class][word] = basewords
        exc_files = ["adj.exc", "adv.exc", "noun.exc", "verb.exc"]
        path_exc = [os.path.join(wordnet_path, f) for f in exc_files]
        for path in path_exc:
            with open(path, "r") as f:
                log.info(f"Loading {path}")
                while True:
                    line = f.readline()
                    if line == "":
                        break
                    res = line.strip().split()
                    pos = path.split("/")[-1].split(".")[0]
                    self._exc[self._pos_to_ss_type[pos]][res[0]] = res[1:]

        # indexes[class][word] = synsets
        index_files = ["index.adj", "index.adv", "index.noun", "index.verb"]
        path_index = [os.path.join(self.wordnet_path, f) for f in index_files]
        for path in path_index:
            with open(path, "r") as f:
                log.info(f"Loading {path}")
                while True:
                    line = f.readline()
                    if line == "":
                        break
                    elif line[:2] == "  ":
                        continue
                    res = line.strip().split()
                    pos = path.split("/")[-1].split(".")[-1]
                    syn_count = int(res[2])
                    self._index[self._pos_to_ss_type[pos]][res[0]] = res[len(res)-syn_count:]

        # data[class][synset] = definition and examples
        data_files = ["data.adj", "data.adv", "data.noun", "data.verb"]
        path_data = [os.path.join(self.wordnet_path, f) for f in data_files]
        for path in path_data:
            with open(path, "r") as f:
                log.info(f"Loading {path}")
                while True:
                    line = f.readline()
                    if line == "":
                        break
                    elif line[:2] == "  ":
                        continue
                    res_str = line.strip()
                    word = res_str.split()[0]
                    pos = path.split("/")[-1].split(".")[-1]
                    self._data[self._pos_to_ss_type[pos]][word] = res_str.split("|")[1]

    def lookup_v2(self, word: str):
        '''Lookup a word in wordnet and return a response with the word class, definitions and examples.
        args:
        - word: string
        returns:
        - dict
        '''
        response = {
            "word": word,
            "synset_count": 0,
            "body": {
                'n': [],
                'a': [],
                'r': [],
                'v': [],
                's': [],
            }
        }

        # Getting base words then synsets
        synsets_and_ss_types: List[Tuple[str, str]] = []
        if not self._word_exists_in_index(word):
            base_words_and_types: List[Tuple[str, str]] = []
            if not self._word_exists_in_exceptions(word):
                base_words_and_types.extend(self._lemmatize(word))
            else:
                for ss_type, obj in self._exc.items():
                    if word not in obj:
                        continue
                    for base_word in obj[word]:
                        base_words_and_types.append((base_word, ss_type))
            log.info(f"Base Words and SS Types: {base_words_and_types}")
            # go on looking for the synsets
            for base_word, ss_type in base_words_and_types:
                if base_word not in self._index[ss_type]:
                    continue
                for synset in self._index[ss_type][base_word]:
                    synsets_and_ss_types.append((synset, ss_type))
        else:
            # here we will get the ss type from the index
            for ss_type, class_obj in self._index.items():
                if word not in class_obj:
                    log.info(f"{word} not in index class_obj[{ss_type}]")
                    continue
                log.info(f"{word} in class_obj[{ss_type}]")
                for synset in class_obj[word]:
                    log.info(f"Synset: {synset} in index.{ss_type}")
                    synsets_and_ss_types.append((synset, ss_type))

        log.info(f"Synsets and SS Types: {synsets_and_ss_types}")

        response["synset_count"] = len(synsets_and_ss_types)

        for synset, ss_type in synsets_and_ss_types:
            defs_and_egs = self._data[ss_type][synset].split(';')
            data = {
                "definition": defs_and_egs[0].strip(),
                "examples": [defs_and_egs[i].strip() for i in range(1, len(defs_and_egs))],
            }
            response["body"][ss_type].append(data)
        log.info(response)
        return response


    def _word_exists_in_index(self, word: str) -> bool:
        '''Checks if the word exists in the index.
        args:
        - word: string
        returns:
        - bool
        '''
        exists = False
        for _, synset_dict in self._index.items():
            if word in synset_dict:
                exists = True
                break
        return exists

    def _word_exists_in_exceptions(self, word: str) -> bool:
        '''Checks if the word exists in the exceptions.
        args:
        - word: string
        returns:
        - bool
        '''
        return word in self._exc


    def _lemmatize(self, word: str) -> List[Tuple[str, str]]:
        '''Lemmatizes the word using a morphological ruleset.
        args:
        - word: string
        returns:
        - list of tuples containing the base word and tense id
        '''
        log.info(f"Lemmatizing {word}")
        potential_base_words = []
        for ss_type, _, pattern, replacement in self.morph_ruleset:
            if not re.match(pattern, word):
                continue
            potential_base_words.append((re.sub(pattern, replacement, word), ss_type))
            log.info(f"Matched {pattern} with {word}")
        return potential_base_words

