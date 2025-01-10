"""UVM testbench code generation module."""
from pathlib import Path
from uvm_gen.generator import UVMGenerator
from uvm_gen.utils import ensure_dir

class CodeGenerator:
    """Code generator for UVM testbench skeleton."""
    def __init__(self, template_dir=None):
        self.template_dir = template_dir

    def render(self, module, out_dir):
        ensure_dir(out_dir)
        template_dir = self.template_dir or str(Path(__file__).parent / "templates")
        gen = UVMGenerator(template_dir, out_dir)
        return gen.generate_testbench(module) 