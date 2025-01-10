#!/usr/bin/env python3
"""Fixed CLI script for UVM Generator v1."""

import sys
import click
from pathlib import Path

# Add the current directory to the path
import os
sys.path.insert(0, os.path.abspath('.'))

from uvm_gen.parser import parse_rtl
from uvm_gen.generator import UVMGenerator

@click.command(help="Generate UVM TB skeleton from SystemVerilog RTL.")
@click.argument('rtl_file', type=click.Path(exists=True))
@click.option('-o', '--output-dir', required=True, type=click.Path(), help='Output directory')
@click.option('-t', '--template-dir', type=click.Path(exists=True), help='Custom template directory')
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose logging')
def main(rtl_file, output_dir, template_dir, verbose):
    """Generate UVM testbench components from a SystemVerilog RTL file."""
    if not rtl_file.endswith(('.sv', '.v')):
        raise click.UsageError("Invalid extension: RTL file must be .sv or .v")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    if verbose:
        click.echo(f"Parsing RTL file: {rtl_file}")
    
    try:
        # Parse the RTL file
        module_info = parse_rtl(rtl_file)
        
        if verbose:
            click.echo(f"Found module: {module_info.name}")
            click.echo(f"Ports: {len(module_info.ports)}")
            for port in module_info.ports:
                click.echo(f"  {port.direction} [{port.width-1}:0] {port.name}")
            click.echo(f"Parameters: {len(module_info.params)}")
            for param in module_info.params:
                click.echo(f"  parameter {param.name} = {param.default}")
        
        # Generate UVM components
        template_path = template_dir or os.path.join("uvm_gen", "templates")
        if verbose:
            click.echo(f"Using templates from: {template_path}")
            click.echo(f"Generating UVM components in: {output_dir}")
        
        generator = UVMGenerator(template_path, output_dir)
        generated_files = generator.generate_testbench(module_info)
        
        if verbose:
            click.echo(f"Generated {len(generated_files)} files:")
            for f in generated_files:
                click.echo(f"  {f}")
        else:
            click.echo(f"Generated UVM testbench for {module_info.name} in {output_dir}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 