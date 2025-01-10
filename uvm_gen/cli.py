"""Command-line interface for UVM testbench generator."""

import click
from pathlib import Path

from uvm_gen.generator import UVMGenerator
from uvm_gen.parser import parse_rtl
from uvm_gen.codegen import CodeGenerator


@click.command(help="Generate UVM TB skeleton from Verilog-2001 RTL.")
@click.option('-r','--rtl',   required=True, type=click.Path(), help='RTL file (.sv)')
@click.option('-o','--out',   required=True, type=click.Path(), help='Output directory')
@click.option('-v','--verbose', is_flag=True, help='Enable verbose logging')
def main(rtl, out, verbose):
    if not rtl.endswith(('.sv','.v')):
        raise click.UsageError("Invalid extension: must be .sv or .v")
    if verbose:
        click.echo(f"Parsing RTL: {rtl}")
    module = parse_rtl(rtl)
    gen = CodeGenerator()
    gen.render(module, out)
    click.echo(f"UVM skeleton generated in {out}")


if __name__ == "__main__":
    main() 