from minic.ir import (BinOp, BinOpInstr, Instr, LoadLiteralInstr, LoadRegInstr,
                      PrintInstr, Program, Reg)
from minic.x86_64 import (Add, Call, Cqo, Idiv, Imm, Imul, Label, MemOffset,
                          Mov, Pop, Push, R, Ret, Size, Sub, X86_64_Program)


class X86_64_CodeGen:
    def __init__(self, program: Program):
        self.program = program
        self.mem_offset_by_reg = {}
        self.allocated_size = 0

    def generate(self):
        translated = self.translate_instructions()

        header = [
            Push(R.Rbp),
            Mov(R.Rbp, R.Rsp),
        ]

        if self.allocated_size:
            header.append(Sub(R.Rsp, Imm(self.allocated_size)))

        footer = [
            Pop(R.Rbp),
            Mov(R.Eax, Imm(0)),
            Ret(),
        ]

        return X86_64_Program(
            instructions=[
                *header,
                *translated,
                *footer,
            ]
        )

    def translate_instructions(self):
        instrs = []

        for instr in self.program.instructions:
            translated = self.translate_instr(instr)
            if isinstance(translated, list):
                instrs.extend(translated)
            else:
                instrs.append(translated)

        return instrs

    def translate_instr(self, instr: Instr):
        match instr:
            case LoadLiteralInstr(out_reg, value):
                out_mem_offset = self.create_mem_offset_for_reg(out_reg, Size.QWordPtr)
                return Mov(out_mem_offset, Imm(value))

            case LoadRegInstr(out_reg, in_reg):
                in_mem_offset = self.get_mem_offset_for_reg(in_reg)
                out_mem_offset = self.create_mem_offset_for_reg(out_reg, Size.QWordPtr)

                return [
                    Mov(R.Rax, in_mem_offset),
                    Mov(out_mem_offset, R.Rax),
                ]

            case BinOpInstr(out_reg, BinOp.Add, left_reg, right_reg):
                out_mem_offset = self.create_mem_offset_for_reg(out_reg, Size.QWordPtr)
                left_mem_offset = self.get_mem_offset_for_reg(left_reg)
                right_mem_offset = self.get_mem_offset_for_reg(right_reg)

                return [
                    Mov(R.Rdx, left_mem_offset),
                    Mov(R.Rax, right_mem_offset),
                    Add(R.Rax, R.Rdx),
                    Mov(out_mem_offset, R.Rax),
                ]

            case BinOpInstr(out_reg, BinOp.Sub, left_reg, right_reg):
                out_mem_offset = self.create_mem_offset_for_reg(out_reg, Size.QWordPtr)
                left_mem_offset = self.get_mem_offset_for_reg(left_reg)
                right_mem_offset = self.get_mem_offset_for_reg(right_reg)

                return [
                    Mov(R.Rdx, left_mem_offset),
                    Mov(R.Rax, right_mem_offset),
                    Sub(R.Rax, R.Rdx),
                    Mov(out_mem_offset, R.Rax),
                ]

            case BinOpInstr(out_reg, BinOp.Mul, left_reg, right_reg):
                out_mem_offset = self.create_mem_offset_for_reg(out_reg, Size.QWordPtr)
                left_mem_offset = self.get_mem_offset_for_reg(left_reg)
                right_mem_offset = self.get_mem_offset_for_reg(right_reg)

                return [
                    Mov(R.Rdx, left_mem_offset),
                    Mov(R.Rax, right_mem_offset),
                    Imul(R.Rax, R.Rdx),
                    Mov(out_mem_offset, R.Rax),
                ]

            case BinOpInstr(out_reg, BinOp.Div, left_reg, right_reg):
                out_mem_offset = self.create_mem_offset_for_reg(out_reg, Size.QWordPtr)
                left_mem_offset = self.get_mem_offset_for_reg(left_reg)
                right_mem_offset = self.get_mem_offset_for_reg(right_reg)

                return [
                    Mov(R.Rax, left_mem_offset),
                    Cqo(),
                    Idiv(right_mem_offset),
                    Mov(out_mem_offset, R.Rax),
                ]

            case PrintInstr(arg_reg):
                arg_mem_offset = self.get_mem_offset_for_reg(arg_reg)

                return [
                    Mov(R.Rax, arg_mem_offset),
                    Mov(R.Rsi, R.Rax),
                    Mov(R.Rdi, Label(".PRINTF_FMT_LLD")),
                    Mov(R.Eax, Imm(0)),
                    Call(Label("printf")),
                ]

        assert False

    def create_mem_offset_for_reg(self, reg: Reg, size: Size) -> MemOffset:
        assert reg not in self.mem_offset_by_reg

        self.allocated_size += size_to_bytes(size)
        mem_offset = MemOffset(size, R.Rbp, -self.allocated_size)
        self.mem_offset_by_reg[reg] = mem_offset

        return mem_offset

    def get_mem_offset_for_reg(self, reg: Reg) -> MemOffset:
        assert reg in self.mem_offset_by_reg

        return self.mem_offset_by_reg[reg]


def size_to_bytes(size: Size):
    match size:
        case Size.QWordPtr:
            return 8

    assert False


# TODO: For optimizations
class IrCursor:
    def __init__(self, window_matcher, window_size: int, program: Program):
        self.window_matcher = window_matcher
        self.window_size = window_size
        self.program = program

    def traverse(self):
        out = []
        window = []
        instr_idx = 0

        while instr_idx < len(program.instructions):
            instr = program.instructions[instr_idx]
            window.append(instr)

            while match_result := self.window_matcher(window):
                window = match_result
