import json
from pathlib import Path
from typing import Any

from ..script import (
    Call,
    Parser,
    Property,
    Tokenizer,
)
from .model import (
    ActivityType,
    ActorLine,
    Entry,
    EntryType,
    Story,
)


class Reader:
    def __init__(
        self,
        gamedata_path: str | Path,
        secondary_gamedata_path: str | Path | None = None,
    ):
        self.path = Path(gamedata_path)
        if secondary_gamedata_path is not None and secondary_gamedata_path != "":
            self.secondary_path = Path(secondary_gamedata_path)
        else:
            self.secondary_path = None

    def _convert_story_text(self, raw_text: str) -> list[ActorLine]:
        raw_lines = Tokenizer.split_code_lines(raw_text)
        ast_lines = [Parser(Tokenizer.tokenize(line)).parse() for line in raw_lines]

        lines: list[ActorLine] = []
        for line in ast_lines:
            if line.actions is None:
                if line.actor_text is not None:
                    lines.append(ActorLine("", line.actor_text))
                continue

            for action in line.actions:
                if isinstance(action, Property) and action.key == "name":
                    if line.actor_text is not None:
                        text = line.actor_text
                    else:
                        text = ""
                    lines.append(
                        ActorLine(
                            action.value,
                            text,
                        )
                    )
                    break
                if isinstance(action, Call) and action.name.lower() == "background":
                    lines.append(
                        ActorLine(
                            "",
                            "",
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
        with (self.path / "excel" / "stage_table.json").open(
            "r", encoding="utf-8"
        ) as f:
            stage_table: dict[str, Any] = json.load(f)

        if self.secondary_path is not None:
            with (self.secondary_path / "excel" / "story_review_table.json").open(
                "r", encoding="utf-8"
            ) as f:
                secondary_story_review_table: dict[str, Any] = json.load(f)
        else:
            secondary_story_review_table = {}

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
                            stage["stageId"] in stage_table["stages"]
                            and "description" in stage_table["stages"][stage["stageId"]]
                        ):
                            desc: str = stage_table["stages"][stage["stageId"]][
                                "description"
                            ]
                            if desc is not None:
                                desc = desc.split("\\n")[0]
                                descriptions.append(desc)

                # fetch secondary name
                secondary_story_name: str = ""
                if entry["id"] in secondary_story_review_table:
                    for secondary_story in secondary_story_review_table[entry["id"]][
                        "infoUnlockDatas"
                    ]:
                        if secondary_story["storyId"] == story["storyId"]:
                            secondary_story_name = secondary_story["storyName"]
                            break

                stories.append(
                    Story(
                        name=story["storyName"],
                        secondary_name=secondary_story_name,
                        code=story["storyCode"],
                        avg_tag=story["avgTag"],
                        description="\n".join(descriptions),
                        texts=texts,
                    )
                )

            # fetch secondary name
            secondary_entry_name: str = ""
            if entry["id"] in secondary_story_review_table:
                secondary_entry_name = secondary_story_review_table[entry["id"]]["name"]
            entries.append(
                Entry(
                    name=entry["name"],
                    secondary_name=secondary_entry_name,
                    entry_type=EntryType(entry["entryType"]),
                    activity_type=ActivityType(entry["actType"]),
                    stories=stories,
                )
            )

        return entries
