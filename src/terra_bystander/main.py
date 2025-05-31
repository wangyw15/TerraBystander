import argparse
import json

from .epub import EpubGenerator
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
        "-t",
        "--type",
        type=str,
        help="Output file type",
        required=False,
        default="json",
        choices=["json", "epub"],
    )
    _parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to save the result file",
        required=False,
        default="./out",
    )
    args = _parser.parse_args()

    print("Reading data...")
    reader = Reader(args.main_gamedata, args.secondary)
    data = reader.read_data()

    if args.type == "json":
        output_path: str = (
            args.output if args.output.endswith(".json") else args.output + ".json"
        )
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, cls=ScriptJsonEncoder)
    elif args.type == "epub":
        print("Generating epub...")
        output_path: str = (
            args.output if args.output.endswith(".epub") else args.output + ".epub"
        )
        generator = EpubGenerator(data, output_path)
        generator.generate()


if __name__ == "__main__":
    main()
