from dataclasses import dataclass
from enum import Enum, auto


class BinOp(Enum):
    Add = auto()
    Sub = auto()
    Mul = auto()
    Div = auto()


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
