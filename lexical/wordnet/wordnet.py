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
        self._exc = {} 
        self._index = {
            'adj': {},
            'adv':{},
            'noun': {},
            'verb': {},
        } 
        self._data = {
            'adj': {},
            'adv': {},
            'noun': {},
            'verb': {},
            'adj_s': {},
        }
        self._char_to_pos = {
            'a': 'adj',
            'n': 'noun',
            'v': 'verb',
            'r': 'adv',
            's': 'adj_s'
        }
        self._pos_to_char = {
            'adj': 'a',
            'adv': 'r',
            'noun': 'n',
            'verb': 'v',
            'adj_s': 's',
        }
        self._morph_ruleset = [
            # Nouns - regular plurals
            ('n', r'(.+?)ies$', r'\1y'),           # babies → baby, flies → fly
            ('n', r'(.+?)([sxz]|[cs]h)es$', r'\1\2'),  # boxes → box, wishes → wish
            ('n', r'(.+?)s$', r'\1'),              # cats → cat

            # Verbs - third person
            ('vtp', r'(.+?)ies$', r'\1y'),           # tries → try
            ('vtp', r'(.+?)([sxz]|[cs]h)es$', r'\1\2'), # passes → pass
            ('vtp', r'(.+?)s$', r'\1'),              # walks → walk

            # Verbs - past tense
            ('vpt', r'(.+?)ied$', r'\1y'),           # tried → try
            ('vpt', r'(.+?)ed$', r'\1'),             # played → play
            ('vpt', r'(.+?)([b-df-hj-np-tv-z])\2ed$', r'\1\2'),  # stopped → stop

            # Verbs - present participle
            ('vpp', r'(.+?)ying$', r'\1ie'),         # lying → lie
            ('vpp', r'(.+?)ing$', r'\1'),            # running → run
            ('vpp', r'(.+?)([b-df-hj-np-tv-z])\2ing$', r'\1\2'),  # stopping → stop

            # Adjectives
            ('a', r'(.+?)iest$', r'\1y'),          # happiest → happy
            ('a', r'(.+?)er$', r'\1'),             # bigger → big
            ('a', r'(.+?)est$', r'\1'),            # biggest → big
        ]
        exc_files = ["adj.exc", "adv.exc", "noun.exc", "verb.exc"]
        path_exc = [os.path.join(self.wordnet_path, f) for f in exc_files]

        for path in path_exc:
            with open(path, "r") as f:
                log.info(f"Loading {path}")
                while True:
                    line = f.readline()
                    if line == "":
                        break
                    res = line.strip().split()
                    word = res[0]
                    base_words = [res[i] for i in range(1, len(res))]
                    self._exc[word] = [base_word for base_word in base_words]

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
                    word = res[0]
                    pos = self._char_to_pos[res[1]]
                    synset_cnt = int(res[2])
                    synsets = res[len(res)-synset_cnt:]
                    self._index[pos][word] = synsets

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
                    synset = res_str[:8]
                    pos = self._char_to_pos[res_str.split()[2]]
                    definition = res_str.split("|")[1]
                    self._data[pos][synset] = definition


    def lookup(self, word) -> List[tuple[str, str]]:
        '''Queries the wordnet for the definition of the word.
        args:
        - word: string
        returns:
        - list of tuples containing the base word and definition
        '''
        log.info(f"Looking up {word}...")
        # base word
        if word in self._exc:
            base_words = self._exc[word]
            log.info(f"Found base word(s) {base_words}")
        else:
            # should clean using morphological rules
            log.info("no base word(s) found")
            base_words = [word]
        
        # gettings synset(s)
        synsets_and_pos = []
        for base_word in base_words:
            for _type, synset_dict in self._index.items():
                if base_word not in synset_dict:
                    continue
                log.info(f"Found synset(s): {synset_dict[base_word]}")
                synsets_and_pos.append((synset_dict[base_word], _type, base_word))
                break

        log.info(f"Synsets and pos: {synsets_and_pos}")

        if len(synsets_and_pos) == 0:
            log.info("No synset(s) found...")
            return []

        # getting definition(s)
        definitions = []
        for synsets, pos, base_word in synsets_and_pos:
            for synset in synsets:
                definition = self._data[pos][synset]
                definitions.append((base_word, definition))

        return definitions

    def lookup_v2(self, word: str):
        '''Queries the wordnet for the definition of the word.
        args:
        - word: string
        returns:
        - list of tuples containing the base word and definition
        '''
        base_words_and_tid = self._get_base_words_and_tid(word)
        synsets_bw_pos_and_tid = self._get_synsets_pos_and_tid(base_words_and_tid)
        if len(synsets_bw_pos_and_tid) == 0:
            return []
        defs_bw_pos_tid = self._get_defs_bw_pos_tid(synsets_bw_pos_and_tid)
        return defs_bw_pos_tid

    def _get_defs_bw_pos_tid(self, synsets_bw_pos_tid: List[Tuple[str, str, str, Any]]) -> List[Tuple[str, str, str, Any]]:
        '''Returns a list of tuples containing the definition, base word, pos, and tense id.
        args:
        - synsets_bw_pos_tid: list of tuples containing the synset, base word, pos, and tense id
        returns:
        - list of tuples containing the definition, base word, pos, and tense id
        '''
        defs = []
        for synset, base_word, pos, tid in synsets_bw_pos_tid:
            definition = self._data[pos][synset]
            defs.append((definition, base_word, pos, tid))
        return defs

    def _get_base_words_and_tid(self, word: str) -> List[Tuple[str, str]] | List[Tuple[str, None]]:
        '''Returns a list of tuples containing the base word and tense id.
        args:
        - word: string
        returns:
        - list of tuples containing the base word and tense id (or None)
        '''
        if not self._word_exists_in_index(word):
            if not self._word_exists_in_exceptions(word):
                base_words = self._lemmatize(word)
            else:
                base_words = [(bw, None) for bw in self._exc[word]]
        else:
            base_words = [(word, None)]
        return base_words

    def _get_synsets_pos_and_tid(self, base_words_and_tid: List[Tuple[str, str]] | List[Tuple[str, None]]) -> List[Tuple[str, str, str, Any]]:
        '''Returns a list of tuples containing the synset, pos, and tense id.
        args:
        - base_words_and_tid: list of tuples containing the base word and tense id
        returns:
        - list of tuples containing the synset, base word, pos, and tense id
        '''
        syn_pos_tid = []
        for base_word, tid in base_words_and_tid:
            for _type, synset_dict in self._index.items():
                if base_word not in synset_dict:
                    continue
                for synset in synset_dict[base_word]:
                    syn_pos_tid.append((synset, base_word, _type, tid))
                break
        return syn_pos_tid


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
        for _id, pattern, replacement in self._morph_ruleset:
            if not re.match(pattern, word):
                continue
            potential_base_words.append(
                (re.sub(pattern, replacement, word), _id)
            )
            log.info(f"Matched {pattern} with {word}")
            break

        return potential_base_words

