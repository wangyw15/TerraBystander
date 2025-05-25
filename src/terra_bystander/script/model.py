from dataclasses import dataclass
from enum import Enum
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
