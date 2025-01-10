"""Tests for the UVM generator module."""

import os
import tempfile
from pathlib import Path
import shutil

import pytest

from uvm_gen.generator import UVMGenerator
from uvm_gen.model import ModuleInfo, Port, Parameter


@pytest.fixture
def module_info():
    """Create a sample module info for testing."""
    ports = [
        Port(name="clk", direction="input", width=1),
        Port(name="rst_n", direction="input", width=1),
        Port(name="data_in", direction="input", width=8),
        Port(name="data_out", direction="output", width=8),
    ]
    params = [
        Parameter(name="WIDTH", default="8"),
        Parameter(name="DEPTH", default="16"),
    ]
    return ModuleInfo(name="test_module", ports=ports, params=params)


@pytest.fixture
def generator():
    """Create a UVM generator instance for testing."""
    template_dir = Path(__file__).parent.parent / "uvm_gen" / "templates"
    with tempfile.TemporaryDirectory() as tmpdir:
        yield UVMGenerator(str(template_dir), tmpdir)


def test_generate_testbench(generator, module_info):
    """Test testbench generation."""
    generated_files = generator.generate_testbench(module_info)
    
    # The generator writes to its output_dir attribute
    output_dir = generator.output_dir if hasattr(generator, 'output_dir') else '.'
    
    # Check that all expected files were generated
    expected_files = [
        "test_module_agent.sv",
        "test_module_driver.sv",
        "test_module_sequencer.sv",
        "test_module_scoreboard.sv",
        "test_module_env.sv",
        "test_module_tb_top.sv",
        "test_module_test.sv",
        "test_module_sequence.sv",
        "test_module_transaction.sv",
        "test_module_interface.sv",
        "test_module_config.sv",
        "test_module_pkg.sv",
    ]
    
    assert len(generated_files) == len(expected_files)
    for file in generated_files:
        file_path = os.path.join(output_dir, file)
        assert os.path.exists(file_path)
        with open(file_path, "r") as f:
            content = f.read()
            assert "test_module" in content
    # Check that all ports are present in the interface and transaction files
    for fname in ["test_module_interface.sv", "test_module_transaction.sv"]:
        file_path = os.path.join(output_dir, fname)
        with open(file_path, "r") as f:
            content = f.read()
            for port in ["clk", "rst_n", "data_in", "data_out"]:
                assert port in content, f"Port {port} not found in {fname}"
    # Check that all parameters are present in the config file
    file_path = os.path.join(output_dir, "test_module_config.sv")
    with open(file_path, "r") as f:
        content = f.read()
        for param in ["WIDTH", "DEPTH"]:
            assert param in content, f"Parameter {param} not found in test_module_config.sv"


def test_generate_testbench_invalid_template(generator, module_info):
    """Test testbench generation with invalid template."""
    # Create a temporary directory with an invalid template
    with tempfile.TemporaryDirectory() as tmpdir:
        invalid_generator = UVMGenerator(tmpdir, tmpdir)
        with pytest.raises(RuntimeError):
            invalid_generator.generate_testbench(module_info)


def test_custom_template_override(tmp_path):
    """Test custom template override functionality."""
    # Create a custom template directory
    custom_templates = tmp_path / "custom_templates"
    custom_templates.mkdir()
    
    # Copy all default templates into the custom directory
    default_templates = Path(__file__).parent.parent / "uvm_gen" / "templates"
    for template_file in default_templates.glob("*.j2"):
        shutil.copy(template_file, custom_templates / template_file.name)
    
    # Overwrite the agent template with a custom one
    custom_agent = custom_templates / "agent.sv.j2"
    custom_agent.write_text("""
class {{ module.name }}_agent extends uvm_agent;
    // Custom agent implementation
    `uvm_component_utils({{ module.name }}_agent)
    
    function new(string name, uvm_component parent);
        super.new(name, parent);
    endfunction
    
    virtual function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        // Custom build phase
    endfunction
endclass
""")
    
    # Create a test module
    test_dir = os.path.dirname(os.path.abspath(__file__))
    rtl_path = os.path.join(test_dir, 'rtl', 'adder.sv')
    
    # Parse the module info
    from uvm_gen.parser import parse_rtl
    module_info = parse_rtl(rtl_path)
    
    # Generate with custom template
    generator = UVMGenerator(str(custom_templates), tmp_path / "output")
    generator.template_dir = str(custom_templates)
    generator.output_dir = tmp_path / "output"
    generator.generate_testbench(module_info)
    
    # Check that the custom template was used
    agent_file = tmp_path / "output" / "adder_agent.sv"
    assert agent_file.exists()
    content = agent_file.read_text()
    assert "Custom agent implementation" in content 