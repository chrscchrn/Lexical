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
        self.exc = {} 
        self.index = {
            'adj': {},
            'adv':{},
            'noun': {},
            'verb': {},
        } 
        self.data = {
            'adj': {},
            'adv': {},
            'noun': {},
            'verb': {},
            'adj_s': {},
        }
        self.abbreviations = {
            'a': 'adj',
            'n': 'noun',
            'v': 'verb',
            'r': 'adv',
            's': 'adj_s'
        }
        self.load_files()

    def load_files(self):
        '''Loads exc, index, and data files into memory
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
                    self.exc[word] = [base_word for base_word in base_words]

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
                    pos = self.abbreviations[res[1]]
                    synset_cnt = int(res[2])
                    synsets = res[len(res)-synset_cnt:]
                    self.index[pos][word] = synsets

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
                    pos = self.abbreviations[res_str.split()[2]]
                    definition = res_str.split("|")[1]
                    self.data[pos][synset] = definition
                    


    def lookup(self, word):
        # get base form of word
        # lookup in index get synsets
        # for each synset get definitions
        pass
    
    def get_base_form(self, word):
        # check if in exc
        # if not, apply standard morphological rules
        # return base form
        pass

    def get_synsets(self, word) -> List[str]:
        '''Searches the index.pos dicts for synsets
            params:
                word: string
            returns:
                list of synsets
                list with empty string is word not found
        '''
        return [""]

    def get_definitions(self, synset):
        pass

