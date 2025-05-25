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
class Story:
    name: str
    secondary_name: str
    code: str
    avg_tag: str
    description: str
    texts: list[ActorLine]


@dataclass
class Entry:
    name: str
    secondary_name: str
    entry_type: EntryType
    activity_type: ActivityType
    stories: list[Story]


class ScriptJsonEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, ActorLine) or isinstance(o, Story) or isinstance(o, Entry):
            return asdict(o)
        if isinstance(o, Enum):
            return o.value
        return super().default(o)
