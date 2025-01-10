import pytest
from uvm_gen.codegen import CodeGenerator
from uvm_gen.model import ModuleInfo, Port
import tempfile
import pathlib

def test_port_propagation():
    """Test that port information is correctly propagated to templates."""
    # Create a dummy module with a single port
    mod = ModuleInfo("dummy", [Port("clk", "input", 1)], [])
    
    # Create a temporary directory for generated files
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Generate the testbench
        generator = CodeGenerator()
        generator.render(mod, tmp_dir)
        
        # Read the generated interface file
        interface_path = pathlib.Path(tmp_dir) / "dummy_interface.sv"
        assert interface_path.exists(), f"Interface file not generated at {interface_path}"
        
        content = interface_path.read_text()
        assert "clk" in content, "Port 'clk' not found in interface template!"
        assert "input" in content, "Port direction not found in interface template!"
        assert "logic" in content, "Port type not found in interface template!"

def test_multiple_ports():
    """Test that multiple ports are correctly propagated."""
    mod = ModuleInfo(
        "dummy",
        [
            Port("clk", "input", 1),
            Port("data", "input", 8),
            Port("valid", "output", 1)
        ],
        []
    )
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        generator = CodeGenerator()
        generator.render(mod, tmp_dir)
        
        interface_path = pathlib.Path(tmp_dir) / "dummy_interface.sv"
        content = interface_path.read_text()
        
        # Check all ports are present
        assert "clk" in content
        assert "data" in content
        assert "valid" in content
        
        # Check port directions
        assert "input" in content
        assert "output" in content
        
        # Check port widths
        assert "logic [7:0]" in content  # For 8-bit data
        assert "logic" in content  # For 1-bit signals 