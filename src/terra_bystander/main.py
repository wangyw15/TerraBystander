import argparse
import json
from pathlib import Path

from tqdm import tqdm, trange

from .comic import Comic
from .epub import EpubGenerator
from .gamedata import Reader, ScriptJsonEncoder
from .txt import generate_txt


def download_comic(comic_downloader: Comic, output_path: str):
    comics = comic_downloader.list_comics()
    if comics is None:
        raise ValueError("Error when fetch comic list")

    comic_output_path: Path = Path(output_path)
    comic_output_path.mkdir(parents=True, exist_ok=True)
    for c in tqdm(comics, position=0, leave=True):
        comic_path = comic_output_path / c["title"]
        comic_path.mkdir()
        comic_data = comic_downloader.comic_data(c["cid"])
        if comic_data is None:
            print(f"Error when fetch data for comic {c['title']}")
            continue

        episode_count = len(comic_data["episodes"])
        for episode in tqdm(comic_data["episodes"], position=1, leave=True):
            episode_path = comic_path / (str(episode_count).zfill(3) + " " + episode["title"])
            episode_count -= 1
            episode_path.mkdir()
            episode_data = comic_downloader.episode_data(
                comic_data["cid"], episode["cid"]
            )
            if episode_data is None:
                print(
                    f"Error when fetch data for episode {episode['title']} comic {c['title']}"
                )
                continue

            for page_num in trange(
                len(episode_data["pageInfos"]), position=2, leave=True
            ):
                page_data = comic_downloader.page_data(
                    comic_data["cid"], episode["cid"], page_num + 1
                )
                if page_data is None:
                    print(
                        f"Error when fetch data for page {page_num} episode {episode['title']} comic {c['title']}"
                    )
                    continue

                img_data = comic_downloader.download(page_data["url"])
                if img_data is None:
                    print(
                        f"Error when download page {page_num} episode {episode['title']} comic {c['title']}"
                    )
                    continue

                page_path = episode_path / (
                    str(page_num + 1).zfill(3) + "." + page_data["url"].split(".")[-1]
                )
                with page_path.open("wb") as f:
                    f.write(img_data)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    book_parser = subparsers.add_parser(
        "book", help="Tools for gamedata extraction and book generation"
    )
    book_parser.add_argument(
        "main_gamedata", type=str, help="Path to main gamedata folder"
    )
    book_parser.add_argument(
        "-s",
        "--secondary",
        type=str,
        help="Path to secondary gamedata folder",
        required=False,
        default=None,
    )
    book_parser.add_argument(
        "-t",
        "--type",
        type=str,
        help="Output file type",
        required=False,
        default="json",
        choices=["json", "epub", "txt"],
    )
    book_parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to save the result file",
        required=False,
        default="./out",
    )

    comic_parser = subparsers.add_parser("comic", help="Tools for downloading comics")
    comic_parser.add_argument(
        "action", type=str, help="Action", choices=["list", "download_all"]
    )
    comic_parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to save the comics",
        required=False,
        default="./comics",
    )

    args = parser.parse_args()

    if args.subcommand == "book":
        print("Reading data...")
        reader = Reader(args.main_gamedata, args.secondary)
        data = reader.read_data()

        if args.type == "json":
            book_output_path: str = (
                args.output if args.output.endswith(".json") else args.output + ".json"
            )
            with open(book_output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, cls=ScriptJsonEncoder)
        elif args.type == "epub":
            print("Generating epub...")
            book_output_path: str = (
                args.output if args.output.endswith(".epub") else args.output + ".epub"
            )
            generator = EpubGenerator(data, book_output_path)
            generator.generate()
        elif args.type == "txt":
            print("Generating txt...")
            book_output_path: str = (
                args.output if args.output.endswith(".txt") else args.output + ".txt"
            )
            with open(book_output_path, "w", encoding="utf-8") as f:
                f.write(generate_txt(data))

    elif args.subcommand == "comic":
        comic_downloader = Comic()

        if args.action == "list":
            comics = comic_downloader.list_comics()
            if comics is not None:
                for c in comics:
                    print_line = c["title"]
                    if c["subtitle"] != "":
                        print_line += " " + c["subtitle"]
                    print_line += " by " + "/".join(c["authors"])
                    print(print_line)
            else:
                print("Error when fetch comic list")

        elif args.action == "download_all":
            download_comic(comic_downloader, args.output)


if __name__ == "__main__":
    main()
