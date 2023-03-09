from dataclasses import dataclass
from enum import Enum, auto
from typing import Union


class R(Enum):
    Eax = auto()
    Edi = auto()
    Rax = auto()
    Rbp = auto()
    Rdi = auto()
    Rdx = auto()
    Rip = auto()
    Rsi = auto()
    Rsp = auto()

    def dump(self) -> str:
        return self.name.lower()


@dataclass
class Imm:
    value: int

    def dump(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Label:
    value: str

    def dump(self) -> str:
        return str(self.value)


class Size(Enum):
    QWordPtr = auto()

    def dump(self) -> str:
        match self:
            case QWordPtr:
                return "QWORD PTR"


@dataclass
class MemOffset:
    size: Size
    base: R
    displacement: Union[int, Label]

    def dump(self) -> str:
        if isinstance(self.displacement, Label):
            disp = f" + {self.displacement.dump()}"
        else:
            disp = (
                f"+{self.displacement}"
                if self.displacement > 0
                else str(self.displacement)
            )

        return f"{self.size.dump()} [{self.base.dump()}{disp}]"


class X86_64_Instr:
    def dump(self) -> str:
        raise NotImplementedError()


@dataclass(frozen=True)
class Push(X86_64_Instr):
    src: R

    def dump(self) -> str:
        return f"push {self.src.dump()}"


@dataclass(frozen=True)
class Pop(X86_64_Instr):
    dst: R

    def dump(self) -> str:
        return f"pop {self.dst.dump()}"


@dataclass(frozen=True)
class Mov(X86_64_Instr):
    dst: Union[R, MemOffset]
    src: Union[R, Imm, MemOffset, Label]

    def dump(self) -> str:
        return f"mov {self.dst.dump()}, {self.src.dump()}"


@dataclass(frozen=True)
class Lea(X86_64_Instr):
    dst: Union[R, MemOffset]
    src: Union[R, Imm, MemOffset, Label]

    def dump(self) -> str:
        return f"lea {self.dst.dump()}, {self.src.dump()}"


@dataclass(frozen=True)
class Add(X86_64_Instr):
    dst: Union[R, MemOffset]
    src: Union[R, Imm, MemOffset]

    def dump(self) -> str:
        return f"add {self.dst.dump()}, {self.src.dump()}"


@dataclass(frozen=True)
class Sub(X86_64_Instr):
    dst: Union[R, MemOffset]
    src: Union[R, Imm, MemOffset]

    def dump(self) -> str:
        return f"sub {self.dst.dump()}, {self.src.dump()}"


@dataclass(frozen=True)
class Imul(X86_64_Instr):
    dst: Union[R, MemOffset]
    src: Union[R, Imm, MemOffset]

    def dump(self) -> str:
        return f"imul {self.dst.dump()}, {self.src.dump()}"


@dataclass(frozen=True)
class Idiv(X86_64_Instr):
    dst: Union[R, MemOffset]

    def dump(self) -> str:
        return f"idiv {self.dst.dump()}"


@dataclass(frozen=True)
class Cqo(X86_64_Instr):
    def dump(self) -> str:
        return "cqo"


@dataclass(frozen=True)
class Ret(X86_64_Instr):
    def dump(self) -> str:
        return "ret"


@dataclass(frozen=True)
class Call(X86_64_Instr):
    target: Union[R, Imm, Label]

    def dump(self) -> str:
        return f"call {self.target.dump()}"


@dataclass(frozen=True)
class X86_64_Program:
    instructions: list[X86_64_Instr]

    def dump(self) -> str:
        output = [
            ".intel_syntax noprefix",
            "",
            ".data",
            ".PRINTF_FMT_LLD:",
            '    .string "%lld\\n"',
            "",
            ".text",
            ".global main",
            "main:",
        ]

        for instr in self.instructions:
            dumped = instr.dump()
            output.append(f"    {dumped}")

        return "\n".join(output) + "\n"
