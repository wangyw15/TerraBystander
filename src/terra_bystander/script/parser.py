from .model import (
    ActionBase,
    Call,
    Property,
    ScriptLine,
    Token,
    TokenType,
)


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens: list[Token] = tokens
        self._index: int = 0

    def parse(self) -> ScriptLine:
        try:
            return ScriptLine(self._expression(), self._actor_text())
        except:
            print(f"Token index: {self._index}")
            print(f"Current token: {self._current_token}")
            print("Tokens:")
            for t in self.tokens:
                print(f"{t.type} {t.value}")
            raise

    @property
    def _current_token(self) -> Token | None:
        if self._index >= len(self.tokens):
            return None
        return self.tokens[self._index]

    @property
    def _next_token(self) -> Token | None:
        if self._index + 1 >= len(self.tokens):
            return None
        return self.tokens[self._index + 1]

    @property
    def _next2_token(self) -> Token | None:
        if self._index + 2 >= len(self.tokens):
            return None
        return self.tokens[self._index + 2]

    def _left_bracket(self) -> bool:
        if (
            self._current_token is not None
            and self._current_token.type == TokenType.LEFT_BRACKET
        ):
            self._index += 1
            return True
        return False

    def _right_bracket(self) -> bool:
        if (
            self._current_token is not None
            and self._current_token.type == TokenType.RIGHT_BRACKET
        ):
            self._index += 1
            return True
        return False

    def _left_parenthesis(self) -> bool:
        if (
            self._current_token is not None
            and self._current_token.type == TokenType.LEFT_PARENTHESIS
        ):
            self._index += 1
            return True
        return False

    def _right_parenthesis(self) -> bool:
        if (
            self._current_token is not None
            and self._current_token.type == TokenType.RIGHT_PARENTHESIS
        ):
            self._index += 1
            return True
        return False

    def _equal(self) -> bool:
        if (
            self._current_token is not None
            and self._current_token.type == TokenType.EQUAL
        ):
            self._index += 1
            return True
        return False

    def _colon(self) -> bool:
        if (
            self._current_token is not None
            and self._current_token.type == TokenType.COLON
        ):
            self._index += 1
            return True
        return False

    def _assign(self) -> bool:
        if self._current_token is None:
            return False

        if self._equal():
            return True
        if self._colon():
            return True
        return False

    def _comma(self) -> bool:
        if (
            self._current_token is not None
            and self._current_token.type == TokenType.COMMA
        ):
            self._index += 1
            return True
        return False

    def _identifier(self) -> str | None:
        if (
            self._current_token is not None
            and self._current_token.type == TokenType.IDENTIFIER
        ):
            ret = self._current_token.value
            self._index += 1
            return ret
        return None

    def _actor_text(self) -> str | None:
        if (
            self._current_token is not None
            and self._current_token.type == TokenType.ACTOR_TEXT
        ):
            ret = self._current_token.value
            self._index += 1
            return ret
        return None

    def _boundary(self) -> bool:
        if self._comma() or self._right_bracket() or self._right_parenthesis():
            return True
        return False

    def _property(self) -> Property | None:
        key = self._identifier()
        if key is None:
            return None

        if not self._assign():
            self._index -= 1  # reverse index changed by identifier
            return None

        if self._current_token is None:
            raise SyntaxError("Cannot find value for property")

        if self._current_token.type == TokenType.STRING:
            value = self._current_token.value
            self._index += 1
        elif self._current_token.type == TokenType.BOOL:
            value = bool(self._current_token.value)
            self._index += 1
        elif self._current_token.type == TokenType.NUMBER:
            if "." in self._current_token.value:
                value = float(self._current_token.value)
            else:
                value = int(self._current_token.value)
            self._index += 1

        elif self._boundary():
            self._index -= 1
            value = None

        else:
            raise SyntaxError(f"Cannot find value for the property: {key}")

        return Property(key, value)

    def _call(self) -> Call | None:
        name = self._identifier()
        if name is None:
            return None

        with_equal = self._equal()

        if not self._left_parenthesis():
            if self._boundary():
                self._index -= 1
                return Call(name)
            else:
                self._index -= 1 + (1 if with_equal else 0)
                return None

        parameters: list[Property] = []
        while True:
            parameter = self._property()
            if parameter is None:
                break
            parameters.append(parameter)

            if not self._comma():
                break

        if not self._right_parenthesis():
            raise SyntaxError("Left parenthesis is never closed.")

        return Call(name, parameters)

    def _actions(self) -> list[ActionBase] | None:
        actions: list[ActionBase] = []
        if c := self._call():
            actions.append(c)
        else:
            while True:
                p = self._property()
                if p is None:
                    break
                actions.append(p)

                if not self._comma():
                    break

        return actions if len(actions) > 0 else None

    def _expression(self) -> list[ActionBase] | None:
        if not self._left_bracket():
            return self._actions()

        actions = self._expression()

        if not self._right_bracket():
            raise SyntaxError("The left bracket is never closed.")

        return actions
