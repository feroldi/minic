from minic.ir import (BinOp, BinOpInstr, LoadLiteralInstr, LoadRegInstr,
                      PrintInstr, Program, Reg)
from minic.x86_64 import (Add, Call, Cqo, Idiv, Imm, Imul, Label, MemOffset,
                          Mov, Pop, Push, R, Ret, Size, Sub, X86_64_Program)
from minic.x86_64_code_gen import X86_64_CodeGen


def test_generate_instructions_to_return_zero_for_empty_ir():
    program = Program(instructions=[])

    code_gen = X86_64_CodeGen(program)
    code = code_gen.generate()

    assert code == X86_64_Program(
        instructions=[
            # Header.
            Push(R.Rbp),
            Mov(R.Rbp, R.Rsp),
            # Footer.
            Pop(R.Rbp),
            Mov(R.Eax, Imm(0)),
            Ret(),
        ]
    )


def test_generate_mov_instructions_for_load_literal():
    program = Program(
        instructions=[
            LoadLiteralInstr(out_reg=Reg(0), value=42),
            LoadLiteralInstr(out_reg=Reg(1), value=123),
        ]
    )

    code_gen = X86_64_CodeGen(program)
    code = code_gen.generate()

    assert code == X86_64_Program(
        instructions=[
            # Header.
            Push(R.Rbp),
            Mov(R.Rbp, R.Rsp),
            Sub(R.Rsp, Imm(16)),
            # Code
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -8), Imm(42)),
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -16), Imm(123)),
            # Footer.
            Pop(R.Rbp),
            Mov(R.Eax, Imm(0)),
            Ret(),
        ]
    )


def test_generate_mov_instructions_for_load_reg():
    program = Program(
        instructions=[
            LoadLiteralInstr(out_reg=Reg(0), value=42),
            LoadLiteralInstr(out_reg=Reg(1), value=123),
            LoadRegInstr(out_reg=Reg(2), in_reg=Reg(0)),
            LoadRegInstr(out_reg=Reg(3), in_reg=Reg(0)),
        ]
    )

    code_gen = X86_64_CodeGen(program)
    code = code_gen.generate()

    assert code == X86_64_Program(
        instructions=[
            # Header.
            Push(R.Rbp),
            Mov(R.Rbp, R.Rsp),
            Sub(R.Rsp, Imm(32)),
            # Code
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -8), Imm(42)),
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -16), Imm(123)),
            Mov(R.Rax, MemOffset(Size.QWordPtr, R.Rbp, -8)),
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -24), R.Rax),
            Mov(R.Rax, MemOffset(Size.QWordPtr, R.Rbp, -8)),
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -32), R.Rax),
            # Footer.
            Pop(R.Rbp),
            Mov(R.Eax, Imm(0)),
            Ret(),
        ]
    )


def test_generate_add_instruction():
    program = Program(
        instructions=[
            LoadLiteralInstr(out_reg=Reg(0), value=20),
            LoadLiteralInstr(out_reg=Reg(1), value=15),
            BinOpInstr(
                out_reg=Reg(2),
                op=BinOp.Add,
                left_reg=Reg(0),
                right_reg=Reg(1),
            ),
        ]
    )

    code_gen = X86_64_CodeGen(program)
    code = code_gen.generate()

    assert code == X86_64_Program(
        instructions=[
            # Header.
            Push(R.Rbp),
            Mov(R.Rbp, R.Rsp),
            Sub(R.Rsp, Imm(24)),
            # Code
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -8), Imm(20)),
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -16), Imm(15)),
            Mov(R.Rdx, MemOffset(Size.QWordPtr, R.Rbp, -8)),
            Mov(R.Rax, MemOffset(Size.QWordPtr, R.Rbp, -16)),
            Add(R.Rax, R.Rdx),
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -24), R.Rax),
            # Footer.
            Pop(R.Rbp),
            Mov(R.Eax, Imm(0)),
            Ret(),
        ]
    )


def test_generate_sub_instruction():
    program = Program(
        instructions=[
            LoadLiteralInstr(out_reg=Reg(0), value=20),
            LoadLiteralInstr(out_reg=Reg(1), value=15),
            BinOpInstr(
                out_reg=Reg(2),
                op=BinOp.Sub,
                left_reg=Reg(0),
                right_reg=Reg(1),
            ),
        ]
    )

    code_gen = X86_64_CodeGen(program)
    code = code_gen.generate()

    assert code == X86_64_Program(
        instructions=[
            # Header.
            Push(R.Rbp),
            Mov(R.Rbp, R.Rsp),
            Sub(R.Rsp, Imm(24)),
            # Code
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -8), Imm(20)),
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -16), Imm(15)),
            Mov(R.Rdx, MemOffset(Size.QWordPtr, R.Rbp, -8)),
            Mov(R.Rax, MemOffset(Size.QWordPtr, R.Rbp, -16)),
            Sub(R.Rax, R.Rdx),
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -24), R.Rax),
            # Footer.
            Pop(R.Rbp),
            Mov(R.Eax, Imm(0)),
            Ret(),
        ]
    )


def test_generate_imul_instruction():
    program = Program(
        instructions=[
            LoadLiteralInstr(out_reg=Reg(0), value=20),
            LoadLiteralInstr(out_reg=Reg(1), value=15),
            BinOpInstr(
                out_reg=Reg(2),
                op=BinOp.Mul,
                left_reg=Reg(0),
                right_reg=Reg(1),
            ),
        ]
    )

    code_gen = X86_64_CodeGen(program)
    code = code_gen.generate()

    assert code == X86_64_Program(
        instructions=[
            # Header.
            Push(R.Rbp),
            Mov(R.Rbp, R.Rsp),
            Sub(R.Rsp, Imm(24)),
            # Code
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -8), Imm(20)),
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -16), Imm(15)),
            Mov(R.Rdx, MemOffset(Size.QWordPtr, R.Rbp, -8)),
            Mov(R.Rax, MemOffset(Size.QWordPtr, R.Rbp, -16)),
            Imul(R.Rax, R.Rdx),
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -24), R.Rax),
            # Footer.
            Pop(R.Rbp),
            Mov(R.Eax, Imm(0)),
            Ret(),
        ]
    )


def test_generate_div_instruction():
    program = Program(
        instructions=[
            LoadLiteralInstr(out_reg=Reg(0), value=20),
            LoadLiteralInstr(out_reg=Reg(1), value=15),
            BinOpInstr(
                out_reg=Reg(2),
                op=BinOp.Div,
                left_reg=Reg(0),
                right_reg=Reg(1),
            ),
        ]
    )

    code_gen = X86_64_CodeGen(program)
    code = code_gen.generate()

    assert code == X86_64_Program(
        instructions=[
            # Header.
            Push(R.Rbp),
            Mov(R.Rbp, R.Rsp),
            Sub(R.Rsp, Imm(24)),
            # Code
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -8), Imm(20)),
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -16), Imm(15)),
            Mov(R.Rax, MemOffset(Size.QWordPtr, R.Rbp, -8)),
            Cqo(),
            Idiv(MemOffset(Size.QWordPtr, R.Rbp, -16)),
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -24), R.Rax),
            # Footer.
            Pop(R.Rbp),
            Mov(R.Eax, Imm(0)),
            Ret(),
        ]
    )


def test_generate_call_to_print():
    program = Program(
        instructions=[
            LoadLiteralInstr(out_reg=Reg(0), value=42),
            PrintInstr(arg_reg=Reg(0)),
        ]
    )

    code_gen = X86_64_CodeGen(program)
    code = code_gen.generate()

    assert code == X86_64_Program(
        instructions=[
            # Header.
            Push(R.Rbp),
            Mov(R.Rbp, R.Rsp),
            Sub(R.Rsp, Imm(8)),
            # Code
            Mov(MemOffset(Size.QWordPtr, R.Rbp, -8), Imm(42)),
            Mov(R.Rax, MemOffset(Size.QWordPtr, R.Rbp, -8)),
            Mov(R.Rsi, R.Rax),
            Mov(R.Rdi, Label(".PRINTF_FMT_LLD")),
            Mov(R.Eax, Imm(0)),
            Call(Label("printf")),
            # Footer.
            Pop(R.Rbp),
            Mov(R.Eax, Imm(0)),
            Ret(),
        ]
    )
