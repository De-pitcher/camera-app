import dis
import sys

def safe_get_instructions(code):
    for instr in dis.get_instructions(code):
        try:
            # Force access to argval now to trigger any IndexError
            if instr.argval is not None:  # This will trigger the constant lookup
                pass
            yield instr
        except IndexError:
            # Create a dummy instruction
            yield dis.Instruction(
                instr.opname, instr.opcode, 
                instr.arg, instr.argval, 
                f"<invalid constant {instr.arg}>", 
                instr.offset, instr.starts_line, 
                instr.is_jump_target
            )

# Monkey-patch PyInstaller's util module
from PyInstaller.lib.modulegraph import util
util.iterate_instructions = safe_get_instructions