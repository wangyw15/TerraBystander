import json
from pathlib import Path
from typing import Any

from .lexer import Tokenizer
from .model import (
    ActivityType,
    ActorLine,
    Entry,
    EntryType,
    Story,
    Property,
)
from .parser import ArknightsStoryParser


def convert_story_text(raw_text: str) -> list[ActorLine]:
    raw_lines = Tokenizer.split_code_lines(raw_text)
    ast_lines = [
        ArknightsStoryParser(Tokenizer.tokenize(line)).parse() for line in raw_lines
    ]

    lines: list[ActorLine] = []
    for line in ast_lines:
        if line.actions is None:
            if line.actor_text is not None:
                lines.append(ActorLine("", line.actor_text))
            continue

        for action in line.actions:
            if isinstance(action, Property) and action.key == "name":
                lines.append(
                    ActorLine(
                        action.value,
                        line.actor_text if line.actor_text is not None else "",
                    )
                )
                break
    return lines


def read_entries(gamedata_path: str | Path) -> list[Entry]:
    if isinstance(gamedata_path, str):
        gamedata_path = Path(gamedata_path)

    entries: list[Entry] = []

    with (gamedata_path / "excel" / "story_review_table.json").open("r", encoding="utf-8") as f:
        story_review_table: dict[str, Any] = json.load(f)

    for _, entry in story_review_table.items():
        stories: list[Story] = []

        for story in entry["infoUnlockDatas"]:
            story_path = gamedata_path / f"story/{story['storyTxt']}.txt"
            with story_path.open("r", encoding="utf-8") as f:
                texts = convert_story_text(f.read())
            stories.append(Story(
                name=story["storyName"],
                code=story["storyCode"],
                avg_tag=story["avgTag"],
                texts=texts,
            ))

        entries.append(Entry(
            name=entry["name"],
            entry_type=EntryType(entry["entryType"]),
            activity_type=ActivityType(entry["actType"]),
            stories=stories,
        ))

    return entries
