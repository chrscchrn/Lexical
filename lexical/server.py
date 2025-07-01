import os
import sys
import logging
from typing import Dict

from .wordnet.wordnet import WordNetHandler

from ._version import __version__

log = logging.getLogger(__name__)


"""
use verbosity to limit the number or definitions and examples.
i.e.
    1 few definitions,
    2 some definitions with max 1 example,
    3 all definitions and examples
"""


def start_io_server(stdin, stdout, root_dir, verbose):
    """Start the IO server
    Args:
        stdin (file): stdin
        stdout (file): stdout
        root_dir (str): root directory
        verbose (bool): verbose
    """
    log.info("starting io server")
    log.info(f"root dir: {root_dir}")
    server = Server(stdin, stdout, root_dir, verbose)
    server.listen()


class Server:
    def __init__(self, stdin, stdout, root_dir, verbose):
        self.stdin = stdin
        self.stdout = stdout
        self.wordnet_path = os.path.join(root_dir, "data")
        self.verbose = verbose
        self.startup_message = False
        self.wordnet = WordNetHandler(self.wordnet_path)
        # TODO: morph explanations
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
        """Listens to stdin and writes to stdout"""
        while not self.stdin.closed:
            if not self.stdout.closed and not self.startup_message:
                msg = "Lexical\n"
                msg += f"version {__version__}\n"
                msg += f"verbose: {self.verbose}\n\n"
                self.write(msg.encode("utf-8"))
                self.startup_message = True
            byte_string = None

            try:
                byte_string = self.stdin.readline().strip()
            except KeyboardInterrupt:
                self.write(b"\n")
                sys.exit(0)
            except Exception as e:
                log.exception(f"Failed to read from stdin {e}")
                continue

            if byte_string is None:
                break

            if len(byte_string) == 0:
                continue

            try:
                request = byte_string.decode("utf-8")
                response = self.handle_request(request)
                self.write(response.encode("utf-8"))
            except Exception as e:
                log.exception(f"Failed to read from stdin: {e}")
                continue
        log.info("Shutting down")

    def handle_request(self, word: str) -> str:
        """Handles a request from stdin and returns a formatted response"""
        log.info(f"Received {word}")
        try:
            response = self.wordnet.call(word.lower())
        except Exception as e:
            return f"An error occured while looking up {word}: {e}\n"

        if not response["synset_count"]:
            return f"No definition(s) found for {word}\n"

        try:
            return self.format_response(response)
        except Exception as e:
            return f"Wordnet Response Protocol Error:\n{e}\n"

    def format_response(self, response: Dict) -> str:
        """Recieves a response in wordnet response
        protocol, formats it, then returns it
        Args:
            response (dict): response from wordnet
        Returns:
            msg (str): formatted response
        """
        if not self.verbose:
            for ss_type in response["body"]:
                response["body"][ss_type] = response["body"][ss_type][:2]
                for i in range(len(response["body"][ss_type])):
                    egs = response["body"][ss_type][i]["examples"][:1]
                    response["body"][ss_type][i]["examples"] = egs

        cur_word_class = ""
        msg = ""
        counter = 1
        for ss_type, type_list in response["body"].items():
            word_class = self._ss_type_to_class[ss_type]
            if cur_word_class != word_class and len(type_list):
                msg += f"({word_class})\n"
            for content in type_list:
                defenition: str = content["definition"]
                msg += f"{counter}. "
                msg += f"{defenition[0].capitalize()}"
                msg += f"{defenition[1:]}\n"
                for ex in content["examples"]:
                    msg += f"  - {ex}\n"
                counter += 1
        return msg

    def write(self, data: bytes):
        """Write bytes to stdout"""
        try:
            self.stdout.write(data)
            self.stdout.flush()
        except Exception as e:
            log.exception(f"Failed to write to stdout: {e}")
