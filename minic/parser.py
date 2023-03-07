from minic.ast import (AssignStmt, BinOp, BinOpExpr, NumberExpr, ParenExpr,
                       PrintStmt, ProgramStmt, VarExpr)
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
