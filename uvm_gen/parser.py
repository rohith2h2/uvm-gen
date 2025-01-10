"""RTL parser for Verilog/SystemVerilog modules."""
import os
import re
import math
from typing import List
from uvm_gen.model import Port, Parameter as ModelParameter, ModuleInfo
import warnings


def _parse_width(width_str: str) -> int:
    """Parse a width expression like '$clog2(NUM_WAYS)-1:0'."""
    if not width_str:
        return 1
    
    # Handle $clog2 expressions
    clog2_match = re.search(r'\$clog2\((\w+)\)', width_str)
    if clog2_match:
        param_name = clog2_match.group(1)
        # Default to 4 for NUM_WAYS
        if param_name == 'NUM_WAYS':
            return int(math.log2(4))
        warnings.warn(f"Unknown parameter {param_name} in width expression - defaulting to 1")
        return 1
    
    # Handle simple ranges like "7:0"
    range_match = re.search(r'(\d+):(\d+)', width_str)
    if range_match:
        msb = int(range_match.group(1))
        lsb = int(range_match.group(2))
        return abs(msb - lsb) + 1
    
    warnings.warn(f"Could not parse width expression {width_str} - defaulting to 1")
    return 1


def parse_rtl(filepath: str) -> ModuleInfo:
    """Parse a Verilog/SystemVerilog file and extract module information."""
    if not filepath.endswith(('.v', '.sv')):
        raise RuntimeError("Invalid file extension. Only .v and .sv are supported.")
    if not os.path.isfile(filepath):
        raise RuntimeError(f"File not found: {filepath}")

    with open(filepath, 'r') as f:
        content = f.read()

    # Extract module name
    module_match = re.search(r'module\s+(\w+)\s*#?\s*\(', content)
    if not module_match:
        raise RuntimeError("No module definition found")
    module_name = module_match.group(1)

    # Extract parameters
    params = []
    param_matches = re.finditer(r'parameter\s+(\w+)\s*=\s*(\d+)', content)
    for match in param_matches:
        name = match.group(1)
        default = int(match.group(2))
        params.append(ModelParameter(name=name, default=default))

    # Extract ports
    ports = []
    port_matches = re.finditer(
        r'(input|output|inout)\s+(?:logic\s+)?(?:\[([^\]]+)\])?\s*(\w+)',
        content
    )
    for match in port_matches:
        direction = match.group(1)
        width_str = match.group(2)
        name = match.group(3)
        width = _parse_width(width_str)
        ports.append(Port(name=name, direction=direction, width=width))

    return ModuleInfo(name=module_name, ports=ports, params=params) 