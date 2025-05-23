from dataclasses import asdict, dataclass
from enum import Enum
from json import JSONEncoder
from typing import Any


# Lexer
class TokenType(Enum):
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    LEFT_PARENTHESIS = "("
    RIGHT_PARENTHESIS = ")"
    SINGLE_QUOTE = "'"
    DOUBLE_QUOTE = '"'
    EQUAL = "="
    COLON = ":"
    POINT = "."
    COMMA = ","
    SPACE = " "
    TAB = "\t"
    CR = "\r"
    LF = "\n"

    BOOL = "bool"
    IDENTIFIER = "identifier"
    STRING = "string"
    NUMBER = r"^\d+(?:\.\d+|)$"
    ACTOR_TEXT = "actor_text"

    UNKNOWN = "unknown"


@dataclass
class Token:
    type: TokenType = TokenType.UNKNOWN
    value: str = ""


# Parser
@dataclass
class ActionBase:
    pass


@dataclass
class Property(ActionBase):
    key: str
    value: Any


@dataclass
class Call(ActionBase):
    name: str
    parameters: list[Property] | None = None


@dataclass
class ScriptLine:
    actions: list[ActionBase] | None
    actor_text: str | None


# Convert
@dataclass
class ActorLine:
    name: str
    text: str


@dataclass
class Passage:
    title: str
    content: list[ActorLine]


@dataclass
class Chapter:
    title: str
    passages: list[Passage]


class ScriptJsonEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, ActorLine) or isinstance(o, Passage) or isinstance(o, Chapter):
            return asdict(o)
        return super().default(o)
