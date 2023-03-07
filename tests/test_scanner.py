import string

import hypothesis.strategies as st
from hypothesis import given
from minic.scanner import Error, Scanner, Token, TokenKind


def test_scan_a_single_digit_number():
    for digit in "0123456789":
        scanner = Scanner(text=digit)

        expected_token = Token(
            kind=TokenKind.Number,
            lexeme=digit,
        )

        assert scanner.next_token() == expected_token


@given(
    text=st.from_regex(r"[1-9][0-9]*", fullmatch=True),
)
def test_scan_number_with_multiple_digits(text):
    scanner = Scanner(text=text)

    expected_token = Token(
        kind=TokenKind.Number,
        lexeme=text,
    )

    assert scanner.next_token() == expected_token


@given(
    non_digits_text=st.text(
        alphabet=string.punctuation + string.whitespace,
        min_size=1,
    )
)
def test_stop_scanning_number_at_a_non_digit_char(non_digits_text):
    scanner = Scanner(text=f"123{non_digits_text}456")

    expected_token = Token(
        kind=TokenKind.Number,
        lexeme="123",
    )

    assert scanner.next_token() == expected_token


def test_error_when_number_starts_with_zero():
    scanner = Scanner(text=f"0123")

    assert scanner.next_token() == Error.NumberStartsWithZero


@given(
    alpha_text=st.text(
        alphabet=string.ascii_letters,
        min_size=1,
    )
)
def test_stop_scanning_number_at_a_non_digit_char(alpha_text):
    scanner = Scanner(text=f"123{alpha_text}456")

    assert scanner.next_token() == Error.InvalidDigit


@given(
    text=st.from_regex(r"[a-zA-Z_][a-zA-Z_0-9]*", fullmatch=True),
)
def test_scan_identifier(text):
    scanner = Scanner(text=text)

    expected_token = Token(
        kind=TokenKind.Ident,
        lexeme=text,
    )

    assert scanner.next_token() == expected_token


@given(
    ident_text=st.from_regex(r"[a-zA-Z_][a-zA-Z_0-9]*", fullmatch=True),
    stop_text=st.text(
        alphabet="".join(c for c in string.punctuation if c != "_") + string.whitespace,
        min_size=1,
    ),
)
def test_stop_scanning_identifier_at_non_alphanumeric_char(ident_text, stop_text):
    scanner = Scanner(text=f"{ident_text}{stop_text}")

    expected_token = Token(
        kind=TokenKind.Ident,
        lexeme=ident_text,
    )

    assert scanner.next_token() == expected_token


def test_scan_plus_operator():
    scanner = Scanner(text="+")
    expected_token = Token(kind=TokenKind.Plus, lexeme="+")

    assert scanner.next_token() == expected_token


def test_scan_minus_operator():
    scanner = Scanner(text="-")
    expected_token = Token(kind=TokenKind.Minus, lexeme="-")

    assert scanner.next_token() == expected_token


def test_scan_star_operator():
    scanner = Scanner(text="*")
    expected_token = Token(kind=TokenKind.Star, lexeme="*")

    assert scanner.next_token() == expected_token


def test_scan_slash_operator():
    scanner = Scanner(text="/")
    expected_token = Token(kind=TokenKind.Slash, lexeme="/")

    assert scanner.next_token() == expected_token


def test_scan_equal_operator():
    scanner = Scanner(text="=")
    expected_token = Token(kind=TokenKind.Equal, lexeme="=")

    assert scanner.next_token() == expected_token


def test_scan_left_paren_operator():
    scanner = Scanner(text="(")
    expected_token = Token(kind=TokenKind.LeftParen, lexeme="(")

    assert scanner.next_token() == expected_token


def test_scan_right_paren_operator():
    scanner = Scanner(text=")")
    expected_token = Token(kind=TokenKind.RightParen, lexeme=")")

    assert scanner.next_token() == expected_token


def test_scan_print_keyword():
    scanner = Scanner(text="print")
    expected_token = Token(kind=TokenKind.PrintKw, lexeme="print")

    assert scanner.next_token() == expected_token


def test_scan_empty_text():
    scanner = Scanner(text="")

    assert scanner.next_token() == Token(TokenKind.Eof, "")
    assert scanner.next_token() == Token(TokenKind.Eof, "")
    assert scanner.next_token() == Token(TokenKind.Eof, "")


def test_scan_sequence_of_operators():
    scanner = Scanner(text="+-*/=()")

    expected_tokens = [
        Token(TokenKind.Plus, "+"),
        Token(TokenKind.Minus, "-"),
        Token(TokenKind.Star, "*"),
        Token(TokenKind.Slash, "/"),
        Token(TokenKind.Equal, "="),
        Token(TokenKind.LeftParen, "("),
        Token(TokenKind.RightParen, ")"),
    ]

    tokens = []

    while tok := scanner.next_token():
        if tok.kind == TokenKind.Eof:
            break
        tokens.append(tok)

    assert tokens == expected_tokens


def test_scan_should_skip_whitespace():
    scanner = Scanner(
        text="""
            foo = 2
            print 42 * (bar - 1)
            """
    )

    expected_tokens = [
        Token(TokenKind.Ident, "foo"),
        Token(TokenKind.Equal, lexeme="="),
        Token(TokenKind.Number, lexeme="2"),
        Token(TokenKind.PrintKw, lexeme="print"),
        Token(TokenKind.Number, lexeme="42"),
        Token(TokenKind.Star, lexeme="*"),
        Token(TokenKind.LeftParen, lexeme="("),
        Token(TokenKind.Ident, lexeme="bar"),
        Token(TokenKind.Minus, lexeme="-"),
        Token(TokenKind.Number, lexeme="1"),
        Token(TokenKind.RightParen, lexeme=")"),
    ]

    tokens = []

    while tok := scanner.next_token():
        if tok.kind == TokenKind.Eof:
            break
        tokens.append(tok)

    assert tokens == expected_tokens
