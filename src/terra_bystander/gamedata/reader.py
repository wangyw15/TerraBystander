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
    Activity,
    ActivityType,
    ActorLine,
    AvgStory,
    EntryType,
    GameDataForBook,
    Operator,
    OperatorStory,
    Power,
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

    def _read_excel_data(self, filename: str) -> Any:
        with (self.path / "excel" / (filename + ".json")).open(
            "r", encoding="utf-8"
        ) as f:
            return json.load(f)

    def read_data(self) -> GameDataForBook:
        return GameDataForBook(
            entries=self.read_entries(),
            operators=self.read_operators(),
        )

    def read_entries(self) -> list[Activity]:
        entries: list[Activity] = []

        # activities
        story_review_table: dict[str, Any] = self._read_excel_data("story_review_table")

        # for description
        stage_table: dict[str, Any] = self._read_excel_data("stage_table")

        if self.secondary_path is not None:
            secondary_story_review_table: dict[str, Any] = self._read_excel_data("story_review_table")
        else:
            secondary_story_review_table = {}

        for _, entry in story_review_table.items():
            stories: list[AvgStory] = []

            if entry["entryType"] == EntryType.NONE.value and entry["actType"] == ActivityType.NONE.value:
                continue

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
                    AvgStory(
                        id=story["storyId"],
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
                Activity(
                    id=entry["id"],
                    name=entry["name"],
                    secondary_name=secondary_entry_name,
                    entry_type=EntryType(entry["entryType"]),
                    activity_type=ActivityType(entry["actType"]),
                    stories=stories,
                )
            )

        return entries

    def read_operators(self) -> list[Operator]:
        operators: list[Operator] = []

        character_table: dict[str, Any] = self._read_excel_data("character_table")
        handbook_info_table: dict[str, Any] = self._read_excel_data("handbook_info_table")
        handbook_team_table: dict[str, Any] = self._read_excel_data("handbook_team_table")
        uniequip_table = self._read_excel_data("uniequip_table")

        for operator_id, operator_data in character_table.items():
            if operator_data["profession"].lower() == "trap":
                continue

            sub_profession: str = operator_data["subProfessionId"]
            sub_profession = uniequip_table["subProfDict"][sub_profession]["subProfessionName"]

            main_nation_id: str | None = operator_data["mainPower"]["nationId"]
            main_group_id: str | None = operator_data["mainPower"]["groupId"]
            main_team_id: str | None = operator_data["mainPower"]["teamId"]
            main_power = Power(
                nation=handbook_team_table[main_nation_id]["powerName"] if main_nation_id is not None else None,
                group=handbook_team_table[main_group_id]["powerName"] if main_group_id is not None else None,
                team=handbook_team_table[main_team_id]["powerName"] if main_team_id is not None else None,
            )

            sub_powers: list[Power] | None = None
            if operator_data["subPower"] is not None:
                sub_powers = []
                for p in operator_data["subPower"]:
                    sub_nation_id: str | None = p["nationId"]
                    sub_group_id: str | None = p["groupId"]
                    sub_team_id: str | None = p["teamId"]

                    sub_powers.append(Power(
                        nation=handbook_team_table[sub_nation_id]["powerName"] if sub_nation_id is not None else None,
                        group=handbook_team_table[sub_group_id]["powerName"] if sub_group_id is not None else None,
                        team=handbook_team_table[sub_team_id]["powerName"] if sub_team_id is not None else None,
                    ))

            operator_stories: list[OperatorStory] = []
            avg_entries: list[Activity] = []
            if operator_id in handbook_info_table["handbookDict"]:
                operator_handbook_info = handbook_info_table["handbookDict"][operator_id]
                for story in operator_handbook_info["storyTextAudio"]:
                    text: str = "\n".join([line["storyText"] for line in story["stories"]])
                    operator_stories.append(OperatorStory(
                        title=story["storyTitle"],
                        text=text,
                    ))

                for operator_activity in operator_handbook_info["handbookAvgList"]:
                    stories: list[AvgStory] = []
                    for story in operator_activity["avgList"]:
                        story_path = self.path / f"story/{story['storyTxt']}.txt"
                        with story_path.open("r", encoding="utf-8") as f:
                            texts = self._convert_story_text(f.read())

                        stories.append(
                            AvgStory(
                                id=story["storyId"],
                                name="",
                                secondary_name="",
                                code="",
                                avg_tag="",
                                description=story["storyIntro"],
                                texts=texts,
                            )
                        )

                    avg_entries.append(Activity(
                        id=operator_activity["storySetId"],
                        name=operator_activity["storySetName"],
                        secondary_name="",
                        entry_type=EntryType.NONE,
                        activity_type=ActivityType.NONE,
                        stories=stories,
                    ))

            operators.append(Operator(
                id=operator_id,
                name=operator_data["name"],
                appellation=operator_data["appellation"],
                usage=operator_data["itemUsage"],
                description=operator_data["itemDesc"],
                profession=operator_data["profession"],
                sub_profession=sub_profession,
                operator_stories=operator_stories,
                avg_entries=avg_entries,
                main_power=main_power,
                sub_powers=sub_powers,
            ))

        return operators
