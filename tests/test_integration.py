"""Integration tests for the UVM generator."""
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from uvm_gen.cli import main as cli_main


def test_full_cli_workflow():
    """Test the full CLI workflow with SV compilation."""
    # Get the path to the test RTL file
    test_dir = Path(__file__).parent
    rtl_path = test_dir / "rtl" / "adder.sv"
    
    # Create a temporary directory for generated files
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Run the CLI
        args = ["--rtl", str(rtl_path), "--out", tmp_dir]
        exit_code = cli_main(args)
        assert exit_code == 0, f"CLI failed with exit code {exit_code}"
        
        # Verify all expected files were generated
        expected_files = [
            "adder_agent.sv",
            "adder_driver.sv",
            "adder_sequencer.sv",
            "adder_scoreboard.sv",
            "adder_env.sv",
            "adder_tb_top.sv",
            "adder_test.sv",
            "adder_sequence.sv",
            "adder_transaction.sv",
            "adder_interface.sv",
            "adder_config.sv",
            "adder_pkg.sv",
        ]
        
        for file in expected_files:
            file_path = Path(tmp_dir) / file
            assert file_path.exists(), f"Expected file {file} not generated"
        
        # Try to compile the generated files with Verilator
        try:
            # Create a simple testbench wrapper
            wrapper_path = Path(tmp_dir) / "tb_wrapper.sv"
            wrapper_path.write_text("""
module tb_wrapper;
    initial begin
        $display("Compilation successful");
        $finish;
    end
endmodule
""")
            
            # Compile with Verilator
            cmd = ["verilator", "--lint-only", str(wrapper_path)]
            for file in expected_files:
                cmd.append(str(Path(tmp_dir) / file))
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Verilator compilation failed: {result.stderr}"
            
        except FileNotFoundError:
            pytest.skip("Verilator not installed") 