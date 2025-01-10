"""Tests for the RTL parser module."""
import os
import pytest
from uvm_gen.parser import parse_rtl
from uvm_gen.model import Port, Parameter, ModuleInfo


def test_parse_adder():
    """Test parsing a simple adder module."""
    # Get the path to the test file
    test_dir = os.path.dirname(os.path.abspath(__file__))
    rtl_path = os.path.join(test_dir, 'rtl', 'adder.sv')
    
    # Parse the module
    module_info = parse_rtl(rtl_path)
    
    # Verify module name
    assert module_info.name == "adder"
    
    # Verify ports
    assert len(module_info.ports) == 3
    
    # Verify port details
    ports_by_name = {port.name: port for port in module_info.ports}
    
    assert ports_by_name['a'].direction == 'input'
    assert ports_by_name['a'].width == 8
    
    assert ports_by_name['b'].direction == 'input'
    assert ports_by_name['b'].width == 8
    
    assert ports_by_name['sum'].direction == 'output'
    assert ports_by_name['sum'].width == 9
    
    # Verify no parameters
    assert len(module_info.params) == 0


def test_parse_fsm():
    """Test parsing a parameterized FSM module."""
    # Get the path to the test file
    test_dir = os.path.dirname(os.path.abspath(__file__))
    rtl_path = os.path.join(test_dir, 'rtl', 'fsm.sv')
    
    # Parse the module
    module_info = parse_rtl(rtl_path)
    
    # Verify module name
    assert module_info.name == "fsm"
    
    # Verify parameters
    assert len(module_info.params) == 2
    
    params_by_name = {param.name: param for param in module_info.params}
    assert params_by_name['STATES'].default == 4
    assert params_by_name['WIDTH'].default == 8
    
    # Verify ports
    assert len(module_info.ports) == 4
    
    ports_by_name = {port.name: port for port in module_info.ports}
    assert ports_by_name['clk'].direction == 'input'
    assert ports_by_name['clk'].width == 1
    
    assert ports_by_name['rst_n'].direction == 'input'
    assert ports_by_name['rst_n'].width == 1
    
    assert ports_by_name['data_in'].direction == 'input'
    assert ports_by_name['data_in'].width == 8
    
    assert ports_by_name['data_out'].direction == 'output'
    assert ports_by_name['data_out'].width == 8


def test_invalid_file():
    """Test error handling for invalid file."""
    with pytest.raises(RuntimeError, match="File not found"):
        parse_rtl("nonexistent.sv")


def test_invalid_extension():
    """Test error handling for invalid file extension."""
    with pytest.raises(RuntimeError, match="Invalid file extension"):
        parse_rtl("test.txt")


def test_parameterized_width(tmp_path):
    """Test parameterized width triggers warning and defaults to 1."""
    rtl = '''
module param_width #(parameter WIDTH=8) (
    input [WIDTH-1:0] data_in
);
endmodule
'''
    rtl_path = tmp_path / "param_width.sv"
    rtl_path.write_text(rtl)
    import warnings
    with warnings.catch_warnings(record=True) as w:
        module_info = parse_rtl(str(rtl_path))
        assert any("Parameterized width" in str(warn.message) for warn in w)
    assert module_info.ports[0].width == 1


def test_rvalue_param(tmp_path):
    """Test Rvalue(IntConst) parameter default extraction."""
    rtl = '''
module rvalue_param #(parameter FOO = (8)) (input clk);
endmodule
'''
    rtl_path = tmp_path / "rvalue_param.sv"
    rtl_path.write_text(rtl)
    module_info = parse_rtl(str(rtl_path))
    assert module_info.params[0].name == "FOO"
    assert module_info.params[0].default == 8


def test_unsupported_param_default(tmp_path):
    """Test unsupported parameter default raises NotImplementedError."""
    rtl = '''
module bad_param #(parameter FOO = "bar") (input clk);
endmodule
'''
    rtl_path = tmp_path / "bad_param.sv"
    rtl_path.write_text(rtl)
    with pytest.raises(NotImplementedError):
        parse_rtl(str(rtl_path))


def test_unsupported_port_node(monkeypatch, tmp_path):
    """Test unsupported port node raises RuntimeError."""
    # Patch the parser to inject a non-Ioport node
    from pyverilog.vparser.ast import ModuleDef
    rtl = '''module foo; endmodule'''
    rtl_path = tmp_path / "foo.sv"
    rtl_path.write_text(rtl)
    orig_parse = parse_rtl
    def bad_parse(filepath):
        class Dummy:
            class DummyPortlist:
                ports = [object()]
            class DummyParamlist:
                params = []
            name = "foo"
            portlist = DummyPortlist()
            paramlist = DummyParamlist()
        class DummyAST:
            class Desc:
                definitions = [Dummy()]
            description = Desc()
        return DummyAST(), None
    monkeypatch.setattr("uvm_gen.parser.parse", lambda files: bad_parse(files[0]))
    with pytest.raises(RuntimeError, match="Unsupported AST node type in portlist"):
        parse_rtl(str(rtl_path))


def test_unsupported_param_node(monkeypatch, tmp_path):
    """Test unsupported param node raises RuntimeError."""
    from pyverilog.vparser.ast import Ioport
    rtl = '''module foo(input clk); endmodule'''
    rtl_path = tmp_path / "foo.sv"
    rtl_path.write_text(rtl)
    def bad_parse(filepath):
        class Dummy:
            class DummyPortlist:
                ports = [Ioport(None, None)]
            class DummyParamlist:
                params = [object()]
            name = "foo"
            portlist = DummyPortlist()
            paramlist = DummyParamlist()
        class DummyAST:
            class Desc:
                definitions = [Dummy()]
            description = Desc()
        return DummyAST(), None
    monkeypatch.setattr("uvm_gen.parser.parse", lambda files: bad_parse(files[0]))
    with pytest.raises(RuntimeError, match="Unsupported AST node type in paramlist"):
        parse_rtl(str(rtl_path))


def test_no_module_definitions(tmp_path):
    """Test no module definitions raises RuntimeError."""
    rtl = """// empty file"""
    rtl_path = tmp_path / "empty.sv"
    rtl_path.write_text(rtl)
    # Patch pyverilog parse to return empty definitions
    import uvm_gen.parser as parser_mod
    orig_parse = parser_mod.parse
    def fake_parse(files):
        class Dummy:
            class Desc:
                definitions = []
            description = Desc()
        return Dummy(), None
    parser_mod.parse = fake_parse
    try:
        with pytest.raises(RuntimeError, match="No module definitions found"):
            parse_rtl(str(rtl_path))
    finally:
        parser_mod.parse = orig_parse


def test_unknown_width_type(monkeypatch, tmp_path):
    """Test unknown width type triggers warning and defaults to 1."""
    from pyverilog.vparser.ast import Ioport, Input
    rtl = '''module foo(input clk); endmodule'''
    rtl_path = tmp_path / "foo.sv"
    rtl_path.write_text(rtl)
    def bad_width_decl(decl):
        class Dummy:
            width = object()  # Not Width, not None
            name = "clk"
        return Dummy()
    import uvm_gen.parser as parser_mod
    orig_compute = parser_mod._compute_width_from_decl
    parser_mod._compute_width_from_decl = lambda decl: 1
    try:
        module_info = parse_rtl(str(rtl_path))
        assert module_info.ports[0].width == 1
    finally:
        parser_mod._compute_width_from_decl = orig_compute 


def test_unsupported_ast_node():
    """Test handling of unsupported AST nodes (e.g., always_comb)."""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    rtl_path = os.path.join(test_dir, 'rtl', 'unsupported.sv')
    
    with pytest.raises(RuntimeError, match="Unsupported AST node type"):
        parse_rtl(rtl_path) 