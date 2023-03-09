from minic.ir_gen import IrGen
from minic.parser import Parser
from minic.scanner import Scanner
from minic.x86_64_code_gen import X86_64_CodeGen


def main():
    import sys
    from pathlib import Path

    in_filename = Path(sys.argv[1])
    code = in_filename.read_text()
    asm_code = compile_minic(code)
    out_filename = in_filename.with_suffix(".s")
    out_filename.write_text(asm_code)


def compile_minic(code: str) -> str:
    scanner = Scanner(code)
    parser = Parser(scanner)
    ir_gen = IrGen(parser.parse_program())
    code_gen = X86_64_CodeGen(ir_gen.gen_program())
    x86_64_program = code_gen.generate()

    return x86_64_program.dump()


if __name__ == "__main__":
    main()
