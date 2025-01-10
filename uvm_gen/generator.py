"""UVM testbench generator module.

This module provides functionality to generate UVM testbench components
from RTL module information using Jinja2 templates.
"""

import os
from pathlib import Path
from typing import List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from uvm_gen.model import ModuleInfo


class UVMGenerator:
    """UVM testbench generator class.

    This class handles the generation of UVM testbench components from
    RTL module information using Jinja2 templates.

    Attributes:
        template_dir: Directory containing the Jinja2 templates.
        output_dir: Directory where generated files will be saved.
        env: Jinja2 environment for template rendering.
    """

    def __init__(self, template_dir: str, output_dir: str):
        """Initialize the UVM generator.

        Args:
            template_dir: Directory containing the Jinja2 templates.
            output_dir: Directory where generated files will be saved.
        """
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate_testbench(self, module_info: ModuleInfo) -> List[str]:
        """Generate UVM testbench components for a module.

        Args:
            module_info: Information about the RTL module.

        Returns:
            List of paths to generated files.

        Raises:
            RuntimeError: If template rendering or file writing fails.
        """
        generated_files = []
        templates = [
            "agent.sv.j2",
            "driver.sv.j2",
            "sequencer.sv.j2",
            "scoreboard.sv.j2",
            "env.sv.j2",
            "tb_top.sv.j2",
            "test.sv.j2",
            "sequence.sv.j2",
            "transaction.sv.j2",
            "interface.sv.j2",
            "config.sv.j2",
            "pkg.sv.j2",
        ]

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate each component
        for template_name in templates:
            try:
                template = self.env.get_template(template_name)
                output_file = self.output_dir / f"{module_info.name}_{template_name[:-3]}"
                content = template.render(module=module_info)
                
                with open(output_file, "w") as f:
                    f.write(content)
                
                generated_files.append(str(output_file))
            except Exception as e:
                raise RuntimeError(f"Failed to generate {template_name}: {str(e)}")

        return generated_files 