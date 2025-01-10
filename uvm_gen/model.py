"""Data models for UVM testbench components."""
from dataclasses import dataclass
from typing import List, Any


@dataclass
class Port:
    """Represents a module port with its properties."""
    name: str
    direction: str  # "input", "output", or "inout"
    width: int = 1  # Default to 1-bit width


@dataclass
class Parameter:
    """Represents a module parameter with its default value."""
    name: str
    default: Any


@dataclass
class ModuleInfo:
    """Represents the extracted information from a Verilog module."""
    name: str
    ports: List[Port]
    params: List[Parameter] 