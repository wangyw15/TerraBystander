from dataclasses import asdict, dataclass
from enum import Enum
from json import JSONEncoder
from typing import Any


# Game data
class EntryType(Enum):
    ACTIVITY = "ACTIVITY"
    MAINLINE = "MAINLINE"
    MINI_ACTIVITY = "MINI_ACTIVITY"
    NONE = "NONE"


class ActivityType(Enum):
    ACTIVITY_STORY = "ACTIVITY_STORY"
    MAIN_STORY = "MAIN_STORY"
    MINI_STORY = "MINI_STORY"
    NONE = "NONE"


@dataclass
class ActorLine:
    name: str
    text: str


@dataclass
class AvgStory:
    id: str
    name: str
    secondary_name: str
    code: str
    avg_tag: str
    description: str
    texts: list[ActorLine]


@dataclass
class Activity:
    id: str
    name: str
    secondary_name: str
    entry_type: EntryType
    activity_type: ActivityType
    stories: list[AvgStory]


@dataclass
class Power:
    nation: str | None = None
    group: str | None = None
    team: str | None = None


@dataclass
class OperatorStory:
    title: str
    text: str


class Profession(Enum):
    PIONEER = "PIONEER"
    WARRIOR = "WARRIOR"
    SNIPER = "SNIPER"
    CASTER = "CASTER"
    SUPPORT = "SUPPORT"
    MEDIC = "MEDIC"
    SPECIAL = "SPECIAL"
    TANK = "TANK"


@dataclass
class Operator:
    id: str
    name: str
    appellation: str
    usage: str
    description: str
    profession: Profession
    sub_profession: str
    operator_stories: list[OperatorStory]
    avgs: list[Activity]
    main_power: Power
    sub_powers: list[Power] | None = None


@dataclass
class GameDataMetadata:
    version: str
    date: str


@dataclass
class GameDataForBook:
    metadata: GameDataMetadata
    activities: list[Activity]
    operators: list[Operator]


class ScriptJsonEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if (
            isinstance(o, ActorLine)
            or isinstance(o, AvgStory)
            or isinstance(o, Activity)
            or isinstance(o, Power)
            or isinstance(o, OperatorStory)
            or isinstance(o, Operator)
            or isinstance(o, GameDataMetadata)
            or isinstance(o, GameDataForBook)
        ):
            return asdict(o)
        if isinstance(o, Enum):
            return o.value
        return super().default(o)
