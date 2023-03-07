import string
from dataclasses import dataclass
from enum import Enum, auto


class TokenKind(Enum):
    Number = auto()
    Ident = auto()
    Plus = auto()
    Minus = auto()
    Star = auto()
    Slash = auto()
    Equal = auto()
    LeftParen = auto()
    RightParen = auto()
    PrintKw = auto()
    Eof = auto()


@dataclass
class Token:
    kind: TokenKind
    lexeme: str


class Error(Enum):
    NumberStartsWithZero = auto()
    InvalidDigit = auto()


class Scanner:
    kind_by_op = {
        "+": TokenKind.Plus,
        "-": TokenKind.Minus,
        "*": TokenKind.Star,
        "/": TokenKind.Slash,
        "=": TokenKind.Equal,
        "(": TokenKind.LeftParen,
        ")": TokenKind.RightParen,
    }

    def __init__(self, text: str):
        self.iter = iter(text)
        self.peeked = None

    def next_token(self):
        while self.peek() in string.whitespace:
            self.bump()

        if self.peek() in string.digits:
            return self.scan_number()
        elif self.peek() in self.kind_by_op:
            return self.scan_operator()
        elif self.peek() in string.ascii_letters + "_":
            return self.scan_ident()
        else:
            return Token(TokenKind.Eof, "")

    def scan_number(self):
        assert self.peek() in string.digits

        lexeme = []

        while self.peek() in string.digits:
            lexeme.append(self.bump())

        if lexeme[0] == "0" and len(lexeme) > 1:
            return Error.NumberStartsWithZero

        if self.peek() in string.ascii_letters:
            return Error.InvalidDigit

        return Token(
            kind=TokenKind.Number,
            lexeme="".join(lexeme),
        )

    def scan_ident(self):
        assert self.peek() not in string.digits

        lexeme = []

        while self.peek() in string.ascii_letters + string.digits + "_":
            lexeme.append(self.bump())

        lexeme = "".join(lexeme)

        return Token(
            kind=TokenKind.Ident if lexeme != "print" else TokenKind.PrintKw,
            lexeme=lexeme,
        )

    def scan_operator(self):
        op = self.bump()

        return Token(self.kind_by_op[op], op)

    def peek(self):
        if not self.peeked:
            try:
                self.peeked = next(self.iter)
            except StopIteration:
                self.peeked = "\0"
        return self.peeked

    def bump(self):
        c = self.peek()
        self.peeked = None
        return c
