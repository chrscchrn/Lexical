import logging
import os
from typing import List
from .wordnet.wordnet import WordNetHandler

log = logging.getLogger(__name__)


"""
use verbosity to limit the number or definitions and examples.
i.e.
    1 few definitions,
    2 some definitions with max 1 example,
    3 all definitions and examples
"""


def start_io_server(stdin, stdout, root_dir, _):
    log.info("starting io server")
    log.info(f"root dir: {root_dir}")
    server = Server(stdin, stdout, root_dir)
    server.listen()


class Server:
    def __init__(self, stdin, stdout, root_dir):
        self.stdin = stdin
        self.stdout = stdout
        self.wordnet_path = os.path.join(root_dir, "data")
        self.startup_message = False
        self.wordnet = WordNetHandler(self.wordnet_path)
        # TODO: morph explanations --base-word, --tense, etc.
        self._morph_explanations = {
            "n": ("noun", "regular plural"),
            "vtp": ("verb", "third person singular present"),
            "vpt": ("verb", "past tense / past participle"),
            "vpp": ("verb", "present tense / present participle"),
            "a": ("adjective", "comparative & superlative"),
        }
        self._ss_type_to_class = {
            "a": "adjective",
            "n": "noun",
            "v": "verb",
            "r": "adverb",
            "s": "adjective",
        }

    def listen(self):
        while not self.stdin.closed:
            if not self.stdout.closed and not self.startup_message:
                self.write("Lexical\nversion 1.0\n\n")
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
                self.handle_request([req_str.strip().decode("utf-8")])
            except ValueError:
                log.exception("Failed to read from stdin")
                continue
        log.info("Shutting down")

    def handle_request(self, words: List[str]):
        log.info(f"Received {words}")

        for word in words:
            try:
                response = self.wordnet.lookup_v2(word.lower())
            except Exception as e:
                self.write(f"An error occured when looking up {word}: {e}\n")
                return

            if not response["synset_count"]:
                self.write(f"No definition(s) found for {word}\n")
                return

            try:
                self.handle_response(response)
            except Exception as e:
                self.write(f"Wordnet Response Protocol Error:\n{e}\n")
                return

    def handle_response(self, response):
        cur_word_class = ""
        msg = ""
        counter = 1
        for ss_type, type_obj in response["body"].items():
            word_class = self._ss_type_to_class[ss_type]
            if cur_word_class != word_class and len(type_obj):
                msg += f"({word_class})\n"

            for content in type_obj:
                defenition: str = content["definition"]
                msg += f"{counter}. "
                msg += f"{defenition[0].capitalize()}"
                msg += f"{defenition[1:]}\n"
                for ex in content["examples"]:
                    msg += f"  - {ex}\n"
                counter += 1
        self.write(msg)

    def write(self, data):
        data = data.encode("utf-8")
        try:
            self.stdout.write(data)
            self.stdout.flush()
        except ValueError:
            log.exception("Failed to write to stdout")
