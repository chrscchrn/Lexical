import logging
import os
from typing import List, Tuple
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
    
    def consumer(self, word):
        log.info(f"Received {word}")
        clean_words = ' '.join(word.strip().split())
        responses: List[List[Tuple[str, str]]] = [self.wordnet.lookup(cw) for cw in clean_words.split(' ')]

        out = f"Definition(s) for word: {word}\n"

        for res in responses:
            log.info(f"res: {res}")
            for base, _def in res:
                log.info(base)
                out += f"base word: {base} - {_def}\n"

        self.write(out.encode("utf-8"))

    def write(self, data):
        self.stdout.write(data)
        self.stdout.flush()

