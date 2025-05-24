import argparse
import json

from .convert import GameDataReader
from .lexer import Tokenizer
from .model import ScriptJsonEncoder
from .parser import ArknightsStoryParser


def test() -> None:
    code = '[name="可露希尔",delay=0.1]你把，温蒂，击飞了？！'
    tokens = Tokenizer.tokenize(code)
    print(tokens)
    parser = ArknightsStoryParser(tokens)
    print(parser.parse())


def main():
    # test()
    # return
    _parser = argparse.ArgumentParser()
    _parser.add_argument("gamedata", type=str, help="Path to gamedata folder")
    _parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to gamedata folder",
        default="./data.json",
        required=False,
    )
    _parser.add_argument(
        "-n",
        "--nickname",
        type=str,
        help="The nickname of Doctor",
        default="博士",
        required=False,
    )
    args = _parser.parse_args()

    reader = GameDataReader(args.gamedata, args.nickname)
    entries = reader.read_entries()
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, cls=ScriptJsonEncoder)


if __name__ == "__main__":
    main()
