import sys
import os
import logging
import argparse
from .server import start_io_server

logging.basicConfig(filename="log.log", level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def add_arguments(parser) -> None:
    parser.description = "Lexy: A dictionary server run on wordnet"

    group = parser.add_mutually_exclusive_group()
    group.add_argument("word", nargs="?", help="The word to look up")
    group.add_argument("--stdin", action="store_true", help="Run inside an lsp instead of the command line")

def _binary_stdio():
    stdin, stdout = sys.stdin.buffer, sys.stdout.buffer
    return stdin, stdout

def main() -> None:
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()

    if args.stdin:
        stdin, stdout = _binary_stdio()
        start_io_server(stdin, stdout, ROOT_DIR)
    else:
        pass
        # CLI

if __name__ == "__main__":
    main()
