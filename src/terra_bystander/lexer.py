from .model import (
    Token,
    TokenType,
)


class Tokenizer:
    @staticmethod
    def split_code_lines(code: str) -> list[str]:
        lines: list[str] = []

        tmp: str = ""
        for line in code.split("\n"):
            line = line.strip("\r")
            if line.endswith("\\"):
                tmp += line[:-1]
            else:
                combined_line = tmp + line
                if combined_line:
                    lines.append(tmp + line)
                tmp = ""

        return lines

    @staticmethod
    def tokenize(code_line: str) -> list[Token]:
        tokens: list[Token] = []

        tmp: str = ""
        status: TokenType | None = None

        def push_token(token_type: TokenType, value: str = "") -> None:
            tokens.append(Token(token_type, value))

        def push_identifier() -> None:
            nonlocal tmp, status
            if tmp != "":
                token_type = TokenType.IDENTIFIER
                if tmp in ["true", "false"]:
                    token_type = TokenType.BOOL
                push_token(token_type, tmp)
                tmp = ""
                status = None

        for i, char in enumerate(code_line):
            # status
            if status == TokenType.NUMBER:
                if char == TokenType.POINT.value:
                    if "." not in tmp:
                        tmp += char
                        continue
                    else:
                        raise SyntaxError(
                            f"Error when parsing number at position {i}:  {char}"
                        )
                elif char.isdigit():
                    tmp += char
                    continue
                else:
                    push_token(TokenType.NUMBER, tmp)
                    tmp = ""
                    status = None

            elif status == TokenType.SINGLE_QUOTE:
                if char == TokenType.SINGLE_QUOTE.value:
                    push_token(TokenType.STRING, tmp)
                    tmp = ""
                    status = None
                else:
                    tmp += char
                continue
            elif status == TokenType.DOUBLE_QUOTE:
                if char == TokenType.DOUBLE_QUOTE.value:
                    push_token(TokenType.STRING, tmp)
                    tmp = ""
                    status = None
                else:
                    tmp += char
                continue

            elif status == TokenType.ACTOR_TEXT:
                tmp += char
                continue

            # char
            if char == TokenType.LEFT_BRACKET.value:
                push_identifier()
                push_token(TokenType.LEFT_BRACKET, char)
            elif char == TokenType.RIGHT_BRACKET.value:
                push_identifier()
                push_token(TokenType.RIGHT_BRACKET, char)
                status = TokenType.ACTOR_TEXT

            elif char == TokenType.LEFT_PARENTHESIS.value:
                push_identifier()
                push_token(TokenType.LEFT_PARENTHESIS, char)
            elif char == TokenType.RIGHT_PARENTHESIS.value:
                push_identifier()
                push_token(TokenType.RIGHT_PARENTHESIS, char)

            elif char == TokenType.COMMA.value:
                push_identifier()
                push_token(TokenType.COMMA, char)

            elif char == TokenType.EQUAL.value:
                push_identifier()
                push_token(TokenType.EQUAL, char)
            elif char == TokenType.COLON.value:
                push_identifier()
                push_token(TokenType.COLON, char)

            elif char == TokenType.SPACE.value:
                push_identifier()
            elif char == TokenType.TAB.value:
                push_identifier()
            elif char == TokenType.CR.value:
                push_identifier()
            elif char == TokenType.LF.value:
                push_identifier()

            elif char == TokenType.SINGLE_QUOTE.value:
                push_identifier()
                if status is None:
                    status = TokenType.SINGLE_QUOTE
                else:
                    raise SyntaxError(
                        f"Invalid syntax for string at position {i}:{char}"
                    )
            elif char == TokenType.DOUBLE_QUOTE.value:
                push_identifier()
                if status is None:
                    status = TokenType.DOUBLE_QUOTE
                else:
                    raise SyntaxError(
                        f"Invalid syntax for string at position {i}:{char}"
                    )

            elif status is None and (char.isdigit() or char in ["+", "-"]):
                push_identifier()
                status = TokenType.NUMBER
                tmp += char

            else:
                if status is None:
                    status = TokenType.IDENTIFIER
                if status == TokenType.IDENTIFIER:
                    tmp += char

        if tmp != "":
            push_token(TokenType.ACTOR_TEXT, tmp.strip())
            status = None

        return tokens
