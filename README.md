# UVM Generator (v1)

A Python-based tool for automatically generating UVM testbench skeletons from SystemVerilog RTL modules. This is the v1 implementation that uses a regex-based parser to extract module information.

## Features

- Parses SystemVerilog RTL files to extract:
  - Module name
  - Port details (name, direction, width)
  - Parameter information
- Generates a complete set of UVM testbench components:
  - Agent, driver, monitor, sequencer
  - Environment, scoreboard
  - Transaction, sequence, interface
  - Test, testbench top
  - Configuration and package files
- Command-line interface for easy usage
- Customizable templates

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/uvm-gen.git
cd uvm-gen/v1

# Install in development mode
pip install -e .
```

## Usage

Generate a UVM testbench for an RTL module using the provided script:

```bash
./uvm_gen_cli.py path/to/rtl_file.sv -o output_dir
```

### Options

- `-o, --output-dir`: Directory where generated files will be saved (required)
- `-t, --template-dir`: Directory containing custom Jinja2 templates
- `-v, --verbose`: Enable verbose output

### Example

```bash
# Generate testbench for an adder module with verbose output
./uvm_gen_cli.py tests/rtl/adder.sv -o tb_adder -v

# Use custom templates
./uvm_gen_cli.py tests/rtl/adder.sv -o tb_adder -t my_templates
```

## Limitations

- Limited support for complex SystemVerilog constructs
- No support for interface definitions
- Limited handling of parameterized widths
- No support for hierarchical module instantiation

## Directory Structure

```
v1/
├── uvm_gen/                  # Main package directory
│   ├── model.py              # Data models for module, ports, and parameters
│   ├── parser.py             # RegEx-based SystemVerilog parser
│   ├── generator.py          # UVM component generation using templates
│   ├── cli.py                # Command-line interface
│   ├── utils.py              # Utility functions
│   └── templates/            # Jinja2 templates for UVM components
├── tests/                    # Test directory
│   └── rtl/                  # Test RTL files
├── docs/                     # Documentation
└── uvm_gen_cli.py            # Fixed CLI script for direct usage
```

## Implementation Details

The v1 implementation uses a regex-based approach to parse SystemVerilog files. It extracts:

1. Module declarations with the pattern `module\s+(\w+)`
2. Port declarations with the pattern `(input|output|inout)\s+(?:logic\s+)?(?:\[([^\]]+)\])?\s*(\w+)`
3. Parameter declarations with the pattern `parameter\s+(\w+)\s*=\s*(\d+)`

The extracted information is stored in a `ModuleInfo` object, which is then used to render Jinja2 templates for the UVM components.

## Contributing

Contributions are welcome! This is a v1 implementation with known limitations, and any improvements to make it more robust are appreciated.

## Generated Files

The generator creates the following UVM components:

- Agent (`*_agent.sv`)
- Driver (`*_driver.sv`)
- Sequencer (`*_sequencer.sv`)
- Scoreboard (`*_scoreboard.sv`)
- Environment (`*_env.sv`)
- Testbench Top (`*_tb_top.sv`)
- Test (`*_test.sv`)
- Sequence (`*_sequence.sv`)
- Transaction (`*_transaction.sv`)
- Interface (`*_interface.sv`)
- Configuration (`*_config.sv`)
- Package (`*_pkg.sv`)

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_parser.py -v
```

### Code Style

The project uses:
- Black for code formatting
- isort for import sorting
- mypy for type checking

## License

MIT License 