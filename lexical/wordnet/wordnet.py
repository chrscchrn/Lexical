import os
import logging
from typing import List
log = logging.getLogger(__name__)

class WordNetHandler:
    def __init__(self, wordnet_path):
        self.wordnet_path = wordnet_path
        '''
        If not in exceptions, apply standard morphological rules (like dropping “-s”, “-ing”).
        exceptions might have overwrites
        '''
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
        self._load_files()

    def _load_files(self):
        '''Loads exc, index, and data wordnet files into memory
        '''
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
            word: string
        returns:
            list of tuples containing the base word and definition
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
            for _type, synset_lookup in self._index.items():
                if base_word not in synset_lookup:
                    continue
                log.info(f"Found synset(s): {synset_lookup[base_word]}")
                synsets_and_pos.append((synset_lookup[base_word], _type, base_word))
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

            

       

