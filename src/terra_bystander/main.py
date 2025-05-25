import argparse
import json

from .gamedata import Reader, ScriptJsonEncoder


def main():
    _parser = argparse.ArgumentParser()
    _parser.add_argument("main_gamedata", type=str, help="Path to main gamedata folder")
    _parser.add_argument(
        "-s",
        "--secondary",
        type=str,
        help="Path to secondary gamedata folder",
        required=False,
        default=None,
    )
    _parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to save the result json",
        default="./data.json",
        required=False,
    )
    args = _parser.parse_args()

    reader = Reader(args.main_gamedata, args.secondary)
    entries = reader.read_entries()
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, cls=ScriptJsonEncoder)


if __name__ == "__main__":
    main()
