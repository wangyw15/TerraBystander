import json
from pathlib import Path
from typing import Any

from .lexer import Tokenizer
from .model import (
    ActivityType,
    ActorLine,
    Entry,
    EntryType,
    Property,
    Story,
)
from .parser import ArknightsStoryParser


class GameDataReader:
    def __init__(self, gamedata_path: str | Path, nickname: str = "Doctor"):
        self.path = Path(gamedata_path)
        self.nickname = nickname

    def _apply_template(self, template: str) -> str:
        result = template

        result = result.replace("{@nickname}", self.nickname)

        return result

    def _convert_story_text(self, raw_text: str) -> list[ActorLine]:
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
                    if line.actor_text is not None:
                        text = self._apply_template(line.actor_text)
                    else:
                        text = ""
                    lines.append(
                        ActorLine(
                            action.value,
                            text,
                        )
                    )
                    break
        return lines

    def read_entries(self) -> list[Entry]:
        entries: list[Entry] = []

        with (self.path / "excel" / "story_review_table.json").open(
            "r", encoding="utf-8"
        ) as f:
            story_review_table: dict[str, Any] = json.load(f)

        # for description
        with (self.path / "excel" / "retro_table.json").open(
            "r", encoding="utf-8"
        ) as f:
            retro_table: dict[str, Any] = json.load(f)

        for _, entry in story_review_table.items():
            stories: list[Story] = []

            for story in entry["infoUnlockDatas"]:
                story_path = self.path / f"story/{story['storyTxt']}.txt"
                with story_path.open("r", encoding="utf-8") as f:
                    texts = self._convert_story_text(f.read())

                descriptions: list[str] = []
                if "requiredStages" in story and story["requiredStages"] is not None:
                    for stage in story["requiredStages"]:
                        if (
                            stage["stageId"] in retro_table["stageList"]
                            and "description"
                            in retro_table["stageList"][stage["stageId"]]
                        ):
                            desc: str = retro_table["stageList"][stage["stageId"]][
                                "description"
                            ]
                            desc = desc.split("\\n")[0]
                            descriptions.append(desc)

                stories.append(
                    Story(
                        name=story["storyName"],
                        code=story["storyCode"],
                        avg_tag=story["avgTag"],
                        description="\n".join(descriptions),
                        texts=texts,
                    )
                )

            entries.append(
                Entry(
                    name=entry["name"],
                    entry_type=EntryType(entry["entryType"]),
                    activity_type=ActivityType(entry["actType"]),
                    stories=stories,
                )
            )

        return entries
