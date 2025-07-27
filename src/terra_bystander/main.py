import json
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer
from tqdm import tqdm, trange

from .comic import Comic
from .epub import EpubGenerator
from .gamedata import Reader, ScriptJsonEncoder
from .txt import generate_txt

typer_app = typer.Typer()


class BookType(str, Enum):
    json = "json"
    epub = "epub"
    txt = "txt"


@typer_app.command()
def book(
    main_gamedata_path: Path,
    output_file: Path,
    book_type: Annotated[BookType, typer.Option("--type", "-t")] = BookType.json,
    secondary_gamedata_path: Annotated[
        Path | None, typer.Option("--secondary-gamedata-path", "-s")
    ] = None,
) -> None:
    print("Reading data...")
    reader = Reader(main_gamedata_path, secondary_gamedata_path)
    data = reader.read_data()

    if book_type == BookType.json:
        print("Writing json...")
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, cls=ScriptJsonEncoder)
    elif book_type == BookType.epub:
        print("Generating epub...")
        generator = EpubGenerator(data, output_file)
        generator.generate()
    elif book_type == BookType.txt:
        print("Generating txt...")
        with output_file.open("w", encoding="utf-8") as f:
            f.write(generate_txt(data))


class ComicAction(str, Enum):
    list = "list"
    download_all = "download_all"


@typer_app.command()
def comic(
    action: ComicAction,
    output_path: Path | None = None,
) -> None:
    comic_downloader = Comic()

    if action == ComicAction.list:
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

    elif action == ComicAction.download_all:
        if output_path is None:
            print("Please specify comic download path")
            return
        download_comic(comic_downloader, output_path)


def download_comic(comic_downloader: Comic, comic_output_path: Path):
    comics = comic_downloader.list_comics()
    if comics is None:
        raise ValueError("Error when fetch comic list")

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
            episode_path = comic_path / (
                str(episode_count).zfill(3) + " " + episode["title"]
            )
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
    typer_app()


if __name__ == "__main__":
    main()
