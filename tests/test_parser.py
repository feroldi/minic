import string

import hypothesis.strategies as st
from hypothesis import given
from minic.parser import (AssignStmt, BinOp, BinOpExpr, NumberExpr, ParenExpr,
                          Parser, PrintStmt, ProgramStmt, VarExpr)
from minic.scanner import Scanner, Token, TokenKind


def st_idents():
    return st.from_regex(r"[a-zA-Z_][a-zA-Z_0-9]*", fullmatch=True)


def st_numbers():
    return st.from_regex(r"[1-9][0-9]*", fullmatch=True)


@given(
    ident_text=st_idents(),
    number_text=st_numbers(),
)
def test_parse_assignment_of_number_to_ident(ident_text, number_text):
    code = f"""
    {ident_text} = {number_text}
    """

    expected_ast = ProgramStmt(
        stmts=[
            AssignStmt(
                target_ident=ident_text,
                value=NumberExpr(val=int(number_text)),
            ),
        ]
    )

    assert _parse(code) == expected_ast


@given(
    target_ident_text=st_idents(),
    source_ident_text=st_idents(),
)
def test_parse_assignment_of_ident_to_ident(target_ident_text, source_ident_text):
    code = f"""
    {target_ident_text} = {source_ident_text}
    """

    expected_ast = ProgramStmt(
        stmts=[
            AssignStmt(
                target_ident=target_ident_text,
                value=VarExpr(ident=source_ident_text),
            ),
        ]
    )

    assert _parse(code) == expected_ast


def test_parse_assignment_of_number_to_ident():
    code = f"""
    foo = 42
    bar = foo
    bar = bar
    """

    expected_ast = ProgramStmt(
        stmts=[
            AssignStmt(
                target_ident="foo",
                value=NumberExpr(val=42),
            ),
            AssignStmt(
                target_ident="bar",
                value=VarExpr(ident="foo"),
            ),
            AssignStmt(
                target_ident="bar",
                value=VarExpr(ident="bar"),
            ),
        ]
    )

    assert _parse(code) == expected_ast


@given(number_text=st_numbers())
def test_parse_print_a_number(number_text):
    code = f"""
    print {number_text}
    """

    expected_ast = ProgramStmt(
        stmts=[
            PrintStmt(
                arg=NumberExpr(val=int(number_text)),
            ),
        ]
    )

    assert _parse(code) == expected_ast


@given(ident_text=st_idents())
def test_parse_print_an_ident(ident_text):
    code = f"""
    print {ident_text}
    """

    expected_ast = ProgramStmt(
        stmts=[
            PrintStmt(
                arg=VarExpr(ident=ident_text),
            ),
        ]
    )

    assert _parse(code) == expected_ast


def test_parse_addictive_operations():
    code = f"""
    print 2 + foo
    print a - b
    """

    expected_ast = ProgramStmt(
        stmts=[
            PrintStmt(
                arg=BinOpExpr(
                    op=BinOp.Add,
                    left=NumberExpr(val=2),
                    right=VarExpr(ident="foo"),
                ),
            ),
            PrintStmt(
                arg=BinOpExpr(
                    op=BinOp.Sub,
                    left=VarExpr(ident="a"),
                    right=VarExpr(ident="b"),
                ),
            ),
        ]
    )

    assert _parse(code) == expected_ast


def test_addition_has_left_associativity():
    code = f"""
    print x + y - z
    """

    expected_ast = ProgramStmt(
        stmts=[
            PrintStmt(
                arg=BinOpExpr(
                    op=BinOp.Sub,
                    left=BinOpExpr(
                        op=BinOp.Add,
                        left=VarExpr(ident="x"),
                        right=VarExpr(ident="y"),
                    ),
                    right=VarExpr(ident="z"),
                ),
            ),
        ]
    )

    assert _parse(code) == expected_ast


def test_parse_product_operations():
    code = f"""
    print 2 * foo
    print a / b
    """

    expected_ast = ProgramStmt(
        stmts=[
            PrintStmt(
                arg=BinOpExpr(
                    op=BinOp.Times,
                    left=NumberExpr(val=2),
                    right=VarExpr(ident="foo"),
                ),
            ),
            PrintStmt(
                arg=BinOpExpr(
                    op=BinOp.Div,
                    left=VarExpr(ident="a"),
                    right=VarExpr(ident="b"),
                ),
            ),
        ]
    )

    assert _parse(code) == expected_ast


def test_product_has_left_associativity():
    code = f"""
    print x * y / z
    """

    expected_ast = ProgramStmt(
        stmts=[
            PrintStmt(
                arg=BinOpExpr(
                    op=BinOp.Div,
                    left=BinOpExpr(
                        op=BinOp.Times,
                        left=VarExpr(ident="x"),
                        right=VarExpr(ident="y"),
                    ),
                    right=VarExpr(ident="z"),
                ),
            ),
        ]
    )

    assert _parse(code) == expected_ast


def test_product_has_more_precedence_than_addition():
    code = f"""
    print x + y * z
    """

    expected_ast = ProgramStmt(
        stmts=[
            PrintStmt(
                arg=BinOpExpr(
                    op=BinOp.Add,
                    left=VarExpr(ident="x"),
                    right=BinOpExpr(
                        op=BinOp.Times,
                        left=VarExpr(ident="y"),
                        right=VarExpr(ident="z"),
                    ),
                ),
            ),
        ]
    )

    assert _parse(code) == expected_ast


def test_parse_parenthesized_expressions():
    code = f"""
    print (a + b) * (c - d)
    """

    a_add_b = ParenExpr(
        inner=BinOpExpr(
            op=BinOp.Add,
            left=VarExpr(ident="a"),
            right=VarExpr(ident="b"),
        )
    )

    c_sub_d = ParenExpr(
        inner=BinOpExpr(
            op=BinOp.Sub,
            left=VarExpr(ident="c"),
            right=VarExpr(ident="d"),
        )
    )

    expected_ast = ProgramStmt(
        stmts=[
            PrintStmt(
                arg=BinOpExpr(
                    op=BinOp.Times,
                    left=a_add_b,
                    right=c_sub_d,
                ),
            ),
        ]
    )

    assert _parse(code) == expected_ast


def test_parse_parenthesized_terms():
    code = f"""
    print (a)
    print (42)
    print (((how_deep_can_you_go)))
    """

    expected_ast = ProgramStmt(
        stmts=[
            PrintStmt(
                arg=ParenExpr(
                    inner=VarExpr(ident="a"),
                ),
            ),
            PrintStmt(
                arg=ParenExpr(
                    inner=NumberExpr(val=42),
                ),
            ),
            PrintStmt(
                arg=ParenExpr(
                    inner=ParenExpr(
                        inner=ParenExpr(
                            inner=VarExpr(ident="how_deep_can_you_go"),
                        ),
                    ),
                ),
            ),
        ]
    )

    assert _parse(code) == expected_ast


def test_parse_parenthesized_complex_operations():
    code = f"""
    print a * ((b + c) / e)
    """

    a = VarExpr(ident="a")
    b = VarExpr(ident="b")
    c = VarExpr(ident="c")
    e = VarExpr(ident="e")

    b_add_c = ParenExpr(inner=BinOpExpr(op=BinOp.Add, left=b, right=c))
    div_e = ParenExpr(inner=BinOpExpr(op=BinOp.Div, left=b_add_c, right=e))
    a_times = BinOpExpr(op=BinOp.Times, left=a, right=div_e)

    expected_ast = ProgramStmt(
        stmts=[
            PrintStmt(
                arg=a_times,
            ),
        ]
    )

    assert _parse(code) == expected_ast


def _parse(code: str):
    scanner = Scanner(code)
    parser = Parser(scanner=scanner)

    return parser.parse_program()
