from pathlib import Path

from .lexer import Tokenizer
from .model import (
    ActorLine,
    Call,
    Chapter,
    Passage,
    Property,
)
from .parser import ArknightsStoryParser


def convert_passage(raw_text: str) -> Passage:
    raw_lines = Tokenizer.split_code_lines(raw_text)
    ast_lines = [
        ArknightsStoryParser(Tokenizer.tokenize(line)).parse() for line in raw_lines
    ]
    lines: list[ActorLine] = []
    title: str = ""
    for line in ast_lines:
        if line.actions is None:
            if line.actor_text is not None:
                lines.append(ActorLine("", line.actor_text))
            continue

        for action in line.actions:
            if isinstance(action, Call) and action.name == "HEADER":
                title = line.actor_text if line.actor_text is not None else ""
            if isinstance(action, Property) and action.key == "name":
                lines.append(
                    ActorLine(
                        action.value,
                        line.actor_text if line.actor_text is not None else "",
                    )
                )
                break
    return Passage(title, lines)


def convert_chapter(chapter_path: str | Path) -> Chapter:
    if isinstance(chapter_path, str):
        chapter_path = Path(chapter_path)

    title: str = chapter_path.name
    passages: list[Passage] = []
    for i in chapter_path.glob("*.txt"):
        with i.open("r", encoding="utf-8") as f:
            passages.append(convert_passage(f.read()))

    return Chapter(title, passages)
