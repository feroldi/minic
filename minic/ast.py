from dataclasses import dataclass
from enum import Enum, auto


class BinOp(Enum):
    Add = auto()
    Sub = auto()
    Times = auto()
    Div = auto()


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


class AstVisitor:
    def visit_program_stmt(self, program_stmt: ProgramStmt):
        raise NotImplementedError()

    def visit_assign_stmt(self, assign_stmt: AssignStmt):
        raise NotImplementedError()

    def visit_print_stmt(self, print_stmt: PrintStmt):
        raise NotImplementedError()

    def visit_paren_expr(self, paren_expr: ParenExpr):
        raise NotImplementedError()

    def visit_bin_op_expr(self, bin_op_expr: BinOpExpr):
        raise NotImplementedError()

    def visit_var_expr(self, var_expr: VarExpr):
        raise NotImplementedError()

    def visit_number_expr(self, number_expr: NumberExpr):
        raise NotImplementedError()
