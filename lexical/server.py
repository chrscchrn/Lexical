import logging
import sys
import os
from typing import Any, List, Tuple
from .wordnet.wordnet import WordNetHandler
log = logging.getLogger(__name__)


def start_io_server(stdin, stdout, root_dir):
    log.info("starting io server")
    log.info(f"root dir: {root_dir}")
    server = Server(stdin, stdout, root_dir)
    server.listen()

class Server:
    def __init__(self, stdin, stdout, root_dir):
        self.stdin = stdin
        self.stdout = stdout
        self.root_dir = root_dir
        self.wordnet_path = os.path.join(self.root_dir, "data")
        self.startup_message = False
        self.wordnet = WordNetHandler(self.wordnet_path)
        self.speech_class = {
            "adj": "adjective",
            "adv": "adverb",
            "noun": "noun",
            "verb": "verb",
            "adj_s": "adjective",
        }
        self._morph_explanations = {
            'n': ("noun", "regular plural"),
            'vtp': ("verb", "third person singular present"),
            'vpt': ("verb", "past tense / past participle"),
            'vpp': ("verb", "present tense / present participle"),
            'a': ("adjective", "comparative & superlative"),
        }
        self._ss_type_to_class = {
            'a': 'adjective',
            'n': 'noun',
            'v': 'verb',
            'r': 'adverb',
            's': 'adjective',
        }
        
    def listen(self):
        while not self.stdin.closed:
            if not self.stdout.closed and not self.startup_message:
                self.write("Lexical\nversion 1.0\n")
                self.startup_message = True
            req_str = None
            try:
                req_str = self.stdin.readline()
            except ValueError:
                if self.stdin.closed:
                    return
                log.exception("Failed to read from stdin")

            if req_str is None:
                break

            if len(req_str) == 0:
                continue

            try:
                self.consumer([req_str.strip().decode('utf-8')])
            except ValueError:
                log.exception("Failed to read from stdin")
                continue
        log.info("Shutting down")
    
    def consumer(self, words: List[str]):
        log.info(f"Received {words}")
        for word in words:
            response = self.wordnet.lookup_v2(word.lower())
            if not response["synset_count"]:
                self.write(f"No definition(s) found for word: {word}.\n")
            cur_word_class = ""
            msg = f"{self._header(word)}"
            counter = 0
            for ss_type, type_obj in response["body"].items():
                word_class = self._ss_type_to_class[ss_type]
                if cur_word_class != word_class and len(type_obj):
                    msg += f"({word_class})\n"
                for content in type_obj:
                    defenition: str = content["definition"]
                    msg += f"{counter}. {defenition[0].capitalize()}{defenition[1:]}\n"
                    for ex in content['examples']:
                        msg += f'  - {ex}\n'
                    counter += 1
            msg += "----------------------------\n"
            self.write(msg)


    def _header(self, word: str):
        return f"----------------------------\n\n{word[0].capitalize()}{word[1:]}\n"
        

    def write(self, data):
        data = data.encode('utf-8')
        self.stdout.write(data)
        self.stdout.flush()

