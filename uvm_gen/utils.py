"""Utility functions for UVM testbench generation.""" 

import os

def ensure_dir(path: str):
    """Ensure that a directory exists at the given path."""
    os.makedirs(path, exist_ok=True) 