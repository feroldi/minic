from minic.ir_gen import (BinOp, BinOpInstr, IrGen, LoadLiteralInstr,
                          LoadRegInstr, PrintInstr, Reg)
from minic.parser import Parser
from minic.scanner import Scanner


def test_load_a_literal_into_a_register():
    code = """
    a = 42
    b = 123
    """

    program = _ir_gen(code)

    assert program.instructions == [
        LoadLiteralInstr(out_reg=Reg(0), value=42),
        LoadRegInstr(out_reg=Reg(1), in_reg=Reg(0)),
        LoadLiteralInstr(out_reg=Reg(2), value=123),
        LoadRegInstr(out_reg=Reg(3), in_reg=Reg(2)),
    ]


def test_load_a_register_into_another_register():
    code = """
    a = 42
    b = a
    """

    program = _ir_gen(code)

    assert program.instructions == [
        LoadLiteralInstr(out_reg=Reg(0), value=42),
        LoadRegInstr(out_reg=Reg(1), in_reg=Reg(0)),
        LoadRegInstr(out_reg=Reg(2), in_reg=Reg(1)),
    ]


def test_simple_addition():
    code = """
    a = 15 + 25
    """

    program = _ir_gen(code)

    assert program.instructions == [
        LoadLiteralInstr(out_reg=Reg(0), value=15),
        LoadLiteralInstr(out_reg=Reg(1), value=25),
        BinOpInstr(out_reg=Reg(2), op=BinOp.Add, left_reg=Reg(0), right_reg=Reg(1)),
        LoadRegInstr(out_reg=Reg(3), in_reg=Reg(2)),
    ]


def test_expression_of_operations():
    code = """
    a = 15
    b = 20 + a * 52
    """

    program = _ir_gen(code)

    assert program.instructions == [
        # a = 15
        LoadLiteralInstr(out_reg=Reg(0), value=15),
        LoadRegInstr(out_reg=Reg(1), in_reg=Reg(0)),
        # 20
        LoadLiteralInstr(out_reg=Reg(2), value=20),
        # 52
        LoadLiteralInstr(out_reg=Reg(3), value=52),
        # a * 52
        BinOpInstr(
            out_reg=Reg(4),
            op=BinOp.Times,
            left_reg=Reg(1),
            right_reg=Reg(3),
        ),
        # 20 +
        BinOpInstr(
            out_reg=Reg(5),
            op=BinOp.Add,
            left_reg=Reg(2),
            right_reg=Reg(4),
        ),
        # b =
        LoadRegInstr(out_reg=Reg(6), in_reg=Reg(5)),
    ]


def test_expression_of_operations():
    code = """
    a = (20 + 15) * 52
    """

    program = _ir_gen(code)

    assert program.instructions == [
        # 20
        LoadLiteralInstr(out_reg=Reg(0), value=20),
        # 15
        LoadLiteralInstr(out_reg=Reg(1), value=15),
        # (20 + 15)
        BinOpInstr(
            out_reg=Reg(2),
            op=BinOp.Add,
            left_reg=Reg(0),
            right_reg=Reg(1),
        ),
        # 52
        LoadLiteralInstr(out_reg=Reg(3), value=52),
        # * 52
        BinOpInstr(
            out_reg=Reg(4),
            op=BinOp.Times,
            left_reg=Reg(2),
            right_reg=Reg(3),
        ),
        # a =
        LoadRegInstr(out_reg=Reg(5), in_reg=Reg(4)),
    ]


def test_subtractions_and_divisions():
    code = """
    a = 15
    b = 20 - a / 52
    """

    program = _ir_gen(code)

    assert program.instructions == [
        # a = 15
        LoadLiteralInstr(out_reg=Reg(0), value=15),
        LoadRegInstr(out_reg=Reg(1), in_reg=Reg(0)),
        # 20
        LoadLiteralInstr(out_reg=Reg(2), value=20),
        # 52
        LoadLiteralInstr(out_reg=Reg(3), value=52),
        # a / 52
        BinOpInstr(
            out_reg=Reg(4),
            op=BinOp.Div,
            left_reg=Reg(1),
            right_reg=Reg(3),
        ),
        # 20 -
        BinOpInstr(
            out_reg=Reg(5),
            op=BinOp.Sub,
            left_reg=Reg(2),
            right_reg=Reg(4),
        ),
        # b =
        LoadRegInstr(out_reg=Reg(6), in_reg=Reg(5)),
    ]


def test_print_a_value():
    code = """
    a = 42
    print 0
    print a
    """

    program = _ir_gen(code)

    assert program.instructions == [
        LoadLiteralInstr(out_reg=Reg(0), value=42),
        LoadRegInstr(out_reg=Reg(1), in_reg=Reg(0)),
        LoadLiteralInstr(out_reg=Reg(2), value=0),
        PrintInstr(arg_reg=Reg(2)),
        PrintInstr(arg_reg=Reg(1)),
    ]


def test_reuse_registers_when_the_same_number_is_found():
    code = """
    x = 42 + 42
    print 42
    """

    program = _ir_gen(code)

    assert program.instructions == [
        LoadLiteralInstr(out_reg=Reg(0), value=42),
        BinOpInstr(
            out_reg=Reg(1),
            op=BinOp.Add,
            left_reg=Reg(0),
            right_reg=Reg(0),
        ),
        LoadRegInstr(out_reg=Reg(2), in_reg=Reg(1)),
        PrintInstr(arg_reg=Reg(0)),
    ]


def test_define_new_reg_when_shadowing_vars():
    code = """
    a = 42
    a = 99
    print a
    """

    program = _ir_gen(code)

    assert program.instructions == [
        LoadLiteralInstr(out_reg=Reg(0), value=42),
        LoadRegInstr(out_reg=Reg(1), in_reg=Reg(0)),
        LoadLiteralInstr(out_reg=Reg(2), value=99),
        LoadRegInstr(out_reg=Reg(3), in_reg=Reg(2)),
        PrintInstr(arg_reg=Reg(3)),
    ]


def test_eliminate_common_subexpressions():
    code = """
    a = (1 + 2) * (1 + 2)
    print a
    """

    program = _ir_gen(code)

    assert program.instructions == [
        LoadLiteralInstr(out_reg=Reg(0), value=1),
        LoadLiteralInstr(out_reg=Reg(1), value=2),
        BinOpInstr(
            out_reg=Reg(2),
            op=BinOp.Add,
            left_reg=Reg(0),
            right_reg=Reg(1),
        ),
        BinOpInstr(
            out_reg=Reg(3),
            op=BinOp.Times,
            left_reg=Reg(2),
            right_reg=Reg(2),
        ),
        LoadRegInstr(out_reg=Reg(4), in_reg=Reg(3)),
        PrintInstr(arg_reg=Reg(4)),
    ]


def test_do_not_eliminate_common_subexpressions_when_var_changes():
    code = """
    a = 42
    b = (a + 2) * (a + 2)
    a = 43
    c = (a + 2) * (a + 2)
    print c
    """

    program = _ir_gen(code)

    assert program.instructions == [
        # a = 42
        LoadLiteralInstr(out_reg=Reg(0), value=42),
        LoadRegInstr(out_reg=Reg(1), in_reg=Reg(0)),
        # (a + 2)
        LoadLiteralInstr(out_reg=Reg(2), value=2),
        BinOpInstr(
            out_reg=Reg(3),
            op=BinOp.Add,
            left_reg=Reg(1),
            right_reg=Reg(2),
        ),
        # b = (a + 2) * (a + 2)
        BinOpInstr(
            out_reg=Reg(4),
            op=BinOp.Times,
            left_reg=Reg(3),
            right_reg=Reg(3),
        ),
        LoadRegInstr(out_reg=Reg(5), in_reg=Reg(4)),
        # a = 43
        LoadLiteralInstr(out_reg=Reg(6), value=43),
        LoadRegInstr(out_reg=Reg(7), in_reg=Reg(6)),
        # (a + 2)
        BinOpInstr(
            out_reg=Reg(8),
            op=BinOp.Add,
            left_reg=Reg(7),
            right_reg=Reg(2),
        ),
        # c = (a + 2) * (a + 2)
        BinOpInstr(
            out_reg=Reg(9),
            op=BinOp.Times,
            left_reg=Reg(8),
            right_reg=Reg(8),
        ),
        LoadRegInstr(out_reg=Reg(10), in_reg=Reg(9)),
        # print c
        PrintInstr(arg_reg=Reg(10)),
    ]


def _ir_gen(code: str):
    scanner = Scanner(code)
    parser = Parser(scanner=scanner)
    ir_gen = IrGen(parser.parse_program())

    return ir_gen.gen_program()
