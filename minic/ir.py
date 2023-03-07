from dataclasses import dataclass
from enum import Enum, auto

from minic import ast
from minic.ast import (AssignStmt, AstVisitor, BinOpExpr, NumberExpr,
                       ParenExpr, PrintStmt, ProgramStmt, VarExpr)


class IrGen(AstVisitor):
    def __init__(self, program_ast):
        self.program_ast = program_ast
        self.reg_by_term = {}
        self.reg_stack = []
        self.reg_idx_counter = 0
        self.instructions = []

    def gen_program(self):
        self.program_ast.accept(self)

        return Program(
            instructions=self.instructions,
        )

    def new_reg(self):
        reg = Reg(self.reg_idx_counter)
        self.reg_idx_counter += 1
        return reg

    def intern_term(self, term_key, reg):
        self.reg_by_term[term_key] = reg

    def get_interned_term(self, term_key):
        assert self.is_term_interned(term_key)
        return self.reg_by_term.get(term_key)

    def is_term_interned(self, term_key):
        return term_key in self.reg_by_term

    def visit_program_stmt(self, program_stmt: ProgramStmt):
        pass

    def visit_assign_stmt(self, assign_stmt: AssignStmt):
        out_reg = self.new_reg()
        self.intern_term(assign_stmt.target_ident, out_reg)
        in_reg = self.reg_stack.pop()
        load_instr = LoadRegInstr(out_reg, in_reg)
        self.instructions.append(load_instr)

    def visit_print_stmt(self, print_stmt: PrintStmt):
        arg_reg = self.reg_stack.pop()
        print_instr = PrintInstr(arg_reg)
        self.instructions.append(print_instr)

    def visit_paren_expr(self, paren_expr: ParenExpr):
        pass

    def visit_bin_op_expr(self, bin_op_expr: BinOpExpr):
        right_reg = self.reg_stack.pop()
        left_reg = self.reg_stack.pop()

        instr_op = bin_op_from_node_op(bin_op_expr.op)
        term = (instr_op, right_reg, left_reg)

        if self.is_term_interned(term):
            out_reg = self.get_interned_term(term)
        else:
            out_reg = self.new_reg()
            self.intern_term(term, out_reg)

            bin_op_instr = BinOpInstr(
                out_reg=out_reg,
                op=instr_op,
                left_reg=left_reg,
                right_reg=right_reg,
            )
            self.instructions.append(bin_op_instr)

        self.reg_stack.append(out_reg)

    def visit_var_expr(self, var_expr: VarExpr):
        var_reg = self.reg_by_term[var_expr.ident]
        self.reg_stack.append(var_reg)

    def visit_number_expr(self, number_expr: NumberExpr):
        if self.is_term_interned(number_expr.val):
            out_reg = self.get_interned_term(number_expr.val)
        else:
            out_reg = self.new_reg()
            self.intern_term(number_expr.val, out_reg)

            load_instr = LoadLiteralInstr(
                out_reg=out_reg,
                value=number_expr.val,
            )
            self.instructions.append(load_instr)

        self.reg_stack.append(out_reg)


class BinOp(Enum):
    Add = auto()
    Sub = auto()
    Times = auto()
    Div = auto()


def bin_op_from_node_op(node_op: ast.BinOp) -> BinOp:
    match node_op:
        case ast.BinOp.Add:
            return BinOp.Add
        case ast.BinOp.Sub:
            return BinOp.Sub
        case ast.BinOp.Times:
            return BinOp.Times
        case ast.BinOp.Div:
            return BinOp.Div

    assert False


@dataclass(frozen=True)
class Reg:
    idx: int


class Instr:
    pass


@dataclass
class Program:
    instructions: list[Instr]


@dataclass
class LoadLiteralInstr(Instr):
    out_reg: Reg
    value: int


@dataclass
class LoadRegInstr(Instr):
    out_reg: Reg
    in_reg: Reg


@dataclass
class BinOpInstr(Instr):
    out_reg: Reg
    op: BinOp
    left_reg: Reg
    right_reg: Reg


@dataclass
class PrintInstr(Instr):
    arg_reg: Reg
