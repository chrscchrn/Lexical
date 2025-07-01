import sys
import os
import logging
import argparse

from .server import start_io_server

logging.basicConfig(
    filename="log.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def add_arguments(parser) -> None:
    parser.description = "Lexical: An offline dictionary server and cli"
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose definitions and examples",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--stdin",
        action="store_true",
        help="Run as an IO server",
    )


def _binary_stdio():
    stdin, stdout = sys.stdin.buffer, sys.stdout.buffer
    return stdin, stdout


def main() -> None:
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()

    if args.stdin:
        stdin, stdout = _binary_stdio()
        start_io_server(stdin, stdout, ROOT_DIR, args.verbose)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
