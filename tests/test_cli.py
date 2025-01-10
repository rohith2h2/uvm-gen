"""Tests for the command-line interface.""" 

from click.testing import CliRunner
from uvm_gen.cli import main
import shutil
import os

def test_cli_success(tmp_path):
    rtl = "tests/rtl/adder.sv"
    out = str(tmp_path/"tb")
    runner = CliRunner()
    result = runner.invoke(main, ["--rtl", rtl, "--out", out])
    assert result.exit_code == 0
    assert (tmp_path/"tb"/"adder_agent.sv").exists()
    assert "UVM skeleton generated in" in result.output

def test_cli_invalid_ext():
    runner = CliRunner()
    result = runner.invoke(main, ["--rtl", "file.txt", "--out", "o"])
    assert result.exit_code != 0
    assert "Invalid extension" in result.output 

def test_readonly_directory(tmp_path):
    """Test handling of read-only output directory."""
    # Create a read-only directory
    readonly_dir = tmp_path / "readonly"
    readonly_dir.mkdir()
    readonly_dir.chmod(0o400)  # Read-only
    
    # Get the path to the test RTL file
    test_dir = os.path.dirname(os.path.abspath(__file__))
    rtl_path = os.path.join(test_dir, 'rtl', 'adder.sv')
    
    # Try to generate into the read-only directory
    runner = CliRunner()
    result = runner.invoke(main, ["--rtl", rtl_path, "--out", str(readonly_dir)])
    
    # Should fail with a permission error
    assert result.exit_code != 0
    assert result.exception is not None
    assert "Permission denied" in str(result.exception) 