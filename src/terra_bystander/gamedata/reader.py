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
    Profession,
)


class Reader:
    """
    Read gamedata
    """

    def __init__(
        self,
        gamedata_path: str | Path,
        secondary_gamedata_path: str | Path | None = None,
    ):
        self.path = Path(gamedata_path)
        self.story_review_table: dict[str, Any] = self._read_excel_data(
            "story_review_table"
        )

        if secondary_gamedata_path is not None and secondary_gamedata_path != "":
            self.secondary_path = Path(secondary_gamedata_path)
            self.secondary_story_review_table: dict[str, Any] = (
                self._read_secondary_excel_data("story_review_table")
            )
        else:
            self.secondary_path = None
            self.secondary_story_review_table = {}

    def read_data(self) -> GameDataForBook:
        """
        Read all data from `gamedata` path

        :return: `GameDataForBook`
        """
        return GameDataForBook(
            activities=self._read_activities(),
            operators=self._read_operators(),
        )

    def _convert_story_text(self, raw_text: str) -> list[ActorLine]:
        """
        Convert story text to structured data

        :params raw_text: story text

        :return: `list[ActorLine]`
        """
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
        """
        Read data from `excel/{filename}.json`

        :params filename: File name without `.json`

        :return: `Any`
        """
        with (self.path / "excel" / (filename + ".json")).open(
            "r", encoding="utf-8"
        ) as f:
            return json.load(f)

    def _read_secondary_excel_data(self, filename: str) -> Any:
        """
        Read data from secondary `excel/{filename}.json`

        :params filename: File name without `.json`

        :return: `Any`
        """
        if self.secondary_path is None:
            return None

        with (self.secondary_path / "excel" / (filename + ".json")).open(
            "r", encoding="utf-8"
        ) as f:
            return json.load(f)

    def _get_secondary_activity_name(self, activity_id: str) -> str:
        """
        Get secondary name for the activity

        :params activity_id: Id of activity

        :return: Secondary name, empty if not found
        """
        if activity_id in self.secondary_story_review_table:
            return self.secondary_story_review_table[activity_id]["name"]
        return ""

    def _get_secondary_story_name(self, activity_id: str, story_id: str) -> str:
        """
        Get secondary name for the story

        :params activity_id: Id of activity
        :params story_id: Id of story

        :return: Secondary name, empty if not found
        """
        if activity_id in self.secondary_story_review_table:
            for story in self.secondary_story_review_table[activity_id][
                "infoUnlockDatas"
            ]:
                if story["storyId"] == story_id:
                    return story["storyName"]
        return ""

    def _read_activities(self) -> list[Activity]:
        """
        Read all activities except which of operators

        :return: `list[Activity]`
        """
        activities: list[Activity] = []

        # for description
        stage_table: dict[str, Any] = self._read_excel_data("stage_table")

        for _, activity_data in self.story_review_table.items():
            stories: list[AvgStory] = []

            if (
                activity_data["entryType"] == EntryType.NONE.value
                and activity_data["actType"] == ActivityType.NONE.value
            ):
                continue

            for story in activity_data["infoUnlockDatas"]:
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

                stories.append(
                    AvgStory(
                        id=story["storyId"],
                        name=story["storyName"],
                        secondary_name=self._get_secondary_story_name(
                            activity_data["id"], story["storyId"]
                        ),
                        code=story["storyCode"],
                        avg_tag=story["avgTag"],
                        description="\n".join(descriptions),
                        texts=texts,
                    )
                )

            activities.append(
                Activity(
                    id=activity_data["id"],
                    name=activity_data["name"],
                    secondary_name=self._get_secondary_activity_name(
                        activity_data["id"]
                    ),
                    entry_type=EntryType(activity_data["entryType"]),
                    activity_type=ActivityType(activity_data["actType"]),
                    stories=stories,
                )
            )

        return activities

    def _read_story_dict(
        self, activity_id: str, story_id: str
    ) -> dict[str, Any] | None:
        """
        Get story dict

        :params activity_id: Id of activity
        :params story_id: Id of story

        :return: `dict[str, Any]`, empty if not found
        """
        activity_data = self.story_review_table[activity_id]
        for story in activity_data["infoUnlockDatas"]:
            if story["storyId"] == story_id:
                return story
        return None

    def _read_operators(self) -> list[Operator]:
        """
        Read all operator info and their stories

        :return: `list[Operator]`
        """
        operators: list[Operator] = []

        character_table: dict[str, Any] = self._read_excel_data("character_table")
        handbook_info_table: dict[str, Any] = self._read_excel_data(
            "handbook_info_table"
        )
        handbook_team_table: dict[str, Any] = self._read_excel_data(
            "handbook_team_table"
        )
        uniequip_table = self._read_excel_data("uniequip_table")

        for operator_id, operator_data in character_table.items():
            if operator_data["profession"] not in Profession:
                continue

            sub_profession: str = operator_data["subProfessionId"]
            sub_profession = uniequip_table["subProfDict"][sub_profession][
                "subProfessionName"
            ]

            main_nation_id: str | None = operator_data["mainPower"]["nationId"]
            main_group_id: str | None = operator_data["mainPower"]["groupId"]
            main_team_id: str | None = operator_data["mainPower"]["teamId"]
            main_power = Power(
                nation=handbook_team_table[main_nation_id]["powerName"]
                if main_nation_id is not None
                else None,
                group=handbook_team_table[main_group_id]["powerName"]
                if main_group_id is not None
                else None,
                team=handbook_team_table[main_team_id]["powerName"]
                if main_team_id is not None
                else None,
            )

            sub_powers: list[Power] | None = None
            if operator_data["subPower"] is not None:
                sub_powers = []
                for p in operator_data["subPower"]:
                    sub_nation_id: str | None = p["nationId"]
                    sub_group_id: str | None = p["groupId"]
                    sub_team_id: str | None = p["teamId"]

                    sub_powers.append(
                        Power(
                            nation=handbook_team_table[sub_nation_id]["powerName"]
                            if sub_nation_id is not None
                            else None,
                            group=handbook_team_table[sub_group_id]["powerName"]
                            if sub_group_id is not None
                            else None,
                            team=handbook_team_table[sub_team_id]["powerName"]
                            if sub_team_id is not None
                            else None,
                        )
                    )

            operator_stories: list[OperatorStory] = []
            avgs: list[Activity] = []
            if operator_id in handbook_info_table["handbookDict"]:
                operator_handbook_info = handbook_info_table["handbookDict"][
                    operator_id
                ]
                for story in operator_handbook_info["storyTextAudio"]:
                    text: str = "\n".join(
                        [line["storyText"] for line in story["stories"]]
                    )
                    operator_stories.append(
                        OperatorStory(
                            title=story["storyTitle"],
                            text=text,
                        )
                    )

                for operator_activity in operator_handbook_info["handbookAvgList"]:
                    stories: list[AvgStory] = []
                    for story in operator_activity["avgList"]:
                        story_path = self.path / f"story/{story['storyTxt']}.txt"
                        with story_path.open("r", encoding="utf-8") as f:
                            texts = self._convert_story_text(f.read())

                        story_dict = self._read_story_dict(
                            story["storySetId"], story["storyId"]
                        )
                        stories.append(
                            AvgStory(
                                id=story["storyId"],
                                name=story_dict["storyName"]
                                if story_dict is not None
                                else "",
                                secondary_name=self._get_secondary_story_name(
                                    story["storySetId"], story["storyId"]
                                ),
                                code=story_dict["storyCode"]
                                if story_dict is not None
                                else "",
                                avg_tag=story_dict["avgTag"]
                                if story_dict is not None
                                else "",
                                description=story["storyIntro"],
                                texts=texts,
                            )
                        )

                    avgs.append(
                        Activity(
                            id=operator_activity["storySetId"],
                            name=operator_activity["storySetName"],
                            secondary_name=self._get_secondary_activity_name(
                                operator_activity["storySetId"]
                            ),
                            entry_type=EntryType.NONE,
                            activity_type=ActivityType.NONE,
                            stories=stories,
                        )
                    )

            operators.append(
                Operator(
                    id=operator_id,
                    name=operator_data["name"],
                    appellation=operator_data["appellation"],
                    usage=operator_data["itemUsage"],
                    description=operator_data["itemDesc"],
                    profession=Profession(operator_data["profession"]),
                    sub_profession=sub_profession,
                    operator_stories=operator_stories,
                    avgs=avgs,
                    main_power=main_power,
                    sub_powers=sub_powers,
                )
            )

        return operators
