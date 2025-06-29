import logging
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
        
    def listen(self):
        while not self.stdin.closed:
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
                self.consumer(req_str.strip().decode('utf-8'))
            except ValueError:
                log.exception("Failed to read from stdin")
                continue
        log.info("Shutting down")
    
    def consumer(self, word: str):
        log.info(f"Received {word}")
        clean_words = ' '.join(word.strip().split())

        for cw in clean_words.split(' '):
            response = self.wordnet.lookup_v2(cw.lower())
        
            current_base_word = ""
            log.info(response)
            log.info(f"WORD: {word}")
            counter = 0
            current_base_word = ""
            header_written = False
            msg = '\nDefinition:\n'

            for definition, base_word, pos, tid in response:
                if not header_written:
                    if tid is not None:
                        morph = self._morph_explanations[tid]
                        msg += self._header(word, morph)
                    else:
                        msg += self._header(word)
                    header_written = True

                if current_base_word != base_word:
                    if tid is not None:
                        morph = self._morph_explanations[tid]
                        msg += f'{word} is the {morph[1]} of "{base_word}"\n{self.speech_class[pos]}\n'
                    else:
                        msg += f'{word} coming from the word "{base_word}"\n{self.speech_class[pos]}\n'
                    current_base_word = base_word

                msg += f'{counter}. '
                msg += self._format_defenition_and_examples(definition)
                counter += 1
            self.write(msg.encode('utf-8'))


    def _format_defenition_and_examples(self, body: str):
        parts = body.split(";")
        msg = f"{parts[0].strip()}\n"
        for i in range(1, len(parts)):
            msg += f'- {parts[i].strip()}\n'
        return msg

    def _header(self, word: str, morph: Any = None):
        msg = f"{word[0].capitalize()}{word[1:]}\n"
        if morph is not None:
            msg += f'{morph[0]}\n'
        return msg
        

    def _new_base_word(self, base_word: str, pos: str, tid: str):
        msg = f"{base_word}\n"
        return msg

    # def _get_speech_class(self, tense = None):
    #     return self.speech_class[pos]

        
    def write(self, data):
        self.stdout.write(data)
        self.stdout.flush()

