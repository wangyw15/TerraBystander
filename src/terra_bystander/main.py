import argparse

from .lexer import Tokenizer
from .model import (
    ScriptLine,
)
from .parser import ArknightsStoryParser


def parse_ast(code: str) -> ScriptLine:
    parser = ArknightsStoryParser(Tokenizer.tokenize(code))
    try:
        return parser.parse()
    except:
        print(f"Error at: {code}")
        print("Tokens:")
        for t in parser.tokens:
            print(f"{t.type} {t.value}")
        raise


def main():
    _parser = argparse.ArgumentParser()
    _parser.add_argument("gamedata", type=str, help="Path to gamedata folder")
    _parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to gamedata folder",
        default="./Arknights.pdf",
        required=False,
    )
    args = _parser.parse_args()

    print("Work in progress...")


if __name__ == "__main__":
    main()
