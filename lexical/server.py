import logging
import os
from typing import Dict, List
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
    """Start the IO server
    Args:
        stdin (file): stdin
        stdout (file): stdout
        root_dir (str): root directory
    """
    log.info("starting io server")
    log.info(f"root dir: {root_dir}")
    server = Server(stdin, stdout, root_dir)
    server.listen()


def run_arguements(words, verbosity):
    """Search the wordnet for words from the command line
    Args:
        words (list): list of words to search
        verbosity (int): verbosity
    """
    log.info("running arguements")
    log.info(f"words: {words}")
    log.info(f"verbosity: {verbosity}")


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
        """Listen for requests from stdin and send responses to stdout"""
        while not self.stdin.closed:
            if not self.stdout.closed and not self.startup_message:
                self.write(b"Lexical\nversion 1.0\n\n")
                self.startup_message = True
            byte_string = None

            try:
                byte_string = self.stdin.readline()
            except Exception as e:
                if self.stdin.closed:
                    log.info("Stdin closed, Shutting down")
                    return
                log.exception(f"Failed to read from stdin {e}")

            if byte_string is None:
                break
            if len(byte_string) == 0:
                continue

            try:
                request = [byte_string.strip().decode("utf-8")]
                response = self.handle_request(request)
                self.write(response.encode("utf-8"))
            except Exception as e:
                log.exception(f"Failed to read from stdin: {e}")
                continue
        log.info("Shutting down")

    def handle_request(self, words: List[str]) -> str:
        """Receives a list of words and returns a response"""
        log.info(f"Received {words}")
        for word in words:
            try:
                response = self.wordnet.call(word.lower())
            except Exception as e:
                self.write(
                    f"An error occured while looking up {word}: {e}\n".encode("utf-8")
                )
                return ""

            if not response["synset_count"]:
                self.write(f"No definition(s) found for {word}\n".encode("utf-8"))
                return ""

            try:
                return self.format_response(response)
            except Exception as e:
                return f"Wordnet Response Protocol Error:\n{e}\n"

        return ""

    def format_response(self, response: Dict) -> str:
        """Recieves a response in wordnet response
        protocol (TODO.md), formats it, then returns it
        Args:
            response (dict): response from wordnet
        Returns:
            msg (str): formatted response
        """
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
        return msg

    def write(self, data: bytes):
        """Write bytes to stdout"""
        try:
            self.stdout.write(data)
            self.stdout.flush()
        except Exception as e:
            log.exception(f"Failed to write to stdout: {e}")
