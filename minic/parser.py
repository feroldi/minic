from dataclasses import dataclass
from enum import Enum, auto

from minic.scanner import TokenKind


class Parser:
    def __init__(self, scanner):
        self.scanner = scanner
        self.peeked_token = None

    def parse_program(self):
        stmts = []
        while self.peek_tok().kind != TokenKind.Eof:
            stmts.append(self.parse_stmt())

        return ProgramStmt(stmts)

    def parse_stmt(self):
        if self.peek_tok().kind == TokenKind.PrintKw:
            return self.parse_print()
        else:
            return self.parse_assignment()

    def parse_assignment(self):
        target_tok = self.consume_tok()
        assert target_tok.kind == TokenKind.Ident

        target_ident = target_tok.lexeme

        op = self.consume_tok()
        assert op.kind == TokenKind.Equal

        value = self.parse_expr()

        return AssignStmt(
            target_ident,
            value,
        )

    def parse_print(self):
        assert self.peek_tok().kind == TokenKind.PrintKw

        self.consume_tok()
        arg = self.parse_expr()

        return PrintStmt(arg)

    def parse_expr(self):
        left_expr = self.parse_product()

        while self.peek_tok().kind in [TokenKind.Plus, TokenKind.Minus]:
            op_tok = self.consume_tok()
            right_expr = self.parse_product()

            left_expr = BinOpExpr(
                op=bin_op_from_tok_kind(op_tok.kind),
                left=left_expr,
                right=right_expr,
            )

        return left_expr

    def parse_product(self):
        left_expr = self.parse_enclosed()

        while self.peek_tok().kind in [TokenKind.Star, TokenKind.Slash]:
            op_tok = self.consume_tok()
            right_expr = self.parse_enclosed()

            left_expr = BinOpExpr(
                op=bin_op_from_tok_kind(op_tok.kind),
                left=left_expr,
                right=right_expr,
            )

        return left_expr

    def parse_enclosed(self):
        if self.peek_tok().kind == TokenKind.LeftParen:
            self.consume_tok()
            expr = self.parse_expr()

            tok = self.consume_tok()
            assert tok.kind == TokenKind.RightParen

            return ParenExpr(inner=expr)
        else:
            return self.parse_term()

    def parse_term(self):
        token = self.consume_tok()

        if token.kind == TokenKind.Number:
            return NumberExpr(val=int(token.lexeme))
        elif token.kind == TokenKind.Ident:
            return VarExpr(ident=token.lexeme)
        else:
            assert False

    def peek_tok(self):
        if not self.peeked_token:
            self.peeked_token = self.scanner.next_token()

        return self.peeked_token

    def consume_tok(self):
        tok = self.peek_tok()
        self.peeked_token = None

        return tok


class BinOp(Enum):
    Add = auto()
    Sub = auto()
    Times = auto()
    Div = auto()


def bin_op_from_tok_kind(tok_kind: TokenKind) -> BinOp:
    match tok_kind:
        case TokenKind.Plus:
            return BinOp.Add
        case TokenKind.Minus:
            return BinOp.Sub
        case TokenKind.Star:
            return BinOp.Times
        case TokenKind.Slash:
            return BinOp.Div

    assert False


class Expr:
    def accept(self, visitor):
        raise NotImplementedError()


class Stmt:
    def accept(self, visitor):
        raise NotImplementedError()


@dataclass(frozen=True)
class NumberExpr(Expr):
    val: int

    def accept(self, visitor):
        visitor.visit_number_expr(self)


@dataclass(frozen=True)
class VarExpr(Expr):
    ident: str

    def accept(self, visitor):
        visitor.visit_var_expr(self)


@dataclass(frozen=True)
class BinOpExpr(Expr):
    op: BinOp
    left: Expr
    right: Expr

    def accept(self, visitor):
        self.left.accept(visitor)
        self.right.accept(visitor)
        visitor.visit_bin_op_expr(self)


@dataclass(frozen=True)
class ParenExpr(Expr):
    inner: Expr

    def accept(self, visitor):
        self.inner.accept(visitor)
        visitor.visit_paren_expr(self)


@dataclass(frozen=True)
class PrintStmt(Stmt):
    arg: Expr

    def accept(self, visitor):
        self.arg.accept(visitor)
        visitor.visit_print_stmt(self)


@dataclass(frozen=True)
class AssignStmt(Stmt):
    target_ident: str
    value: Expr

    def accept(self, visitor):
        self.value.accept(visitor)
        visitor.visit_assign_stmt(self)


@dataclass(frozen=True)
class ProgramStmt(Stmt):
    stmts: list[Stmt]

    def accept(self, visitor):
        for stmt in self.stmts:
            stmt.accept(visitor)
        visitor.visit_program_stmt(self)
