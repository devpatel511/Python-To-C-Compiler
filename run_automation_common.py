#!/usr/bin/env python3
"""common functions and vars for run_automation"""
import difflib
import os
from typing import Any, Dict, List, Optional, Tuple

from TheComPylersCompiler import compile_source

# we want to set the script directory to the current file's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# we want to set the default directories to the examples/lang and examples/optimization directories
DEFAULT_DIRS = ["examples/lang", "examples/optimization"]


def generated_c_basename(expected_c_name: str) -> str:
    """we return the generated c basename"""
    return f"generated_{expected_c_name}"


def read_file(path: str) -> str:
    """read the file at the given path"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(text: str, path: str) -> None:
    """write the given text to the file at the given path"""
    # we want to get the directory name of the given path
    d = os.path.dirname(path)
    # if the directory name is not empty, we want to create the directory
    if d:
        os.makedirs(d, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def diff_lines(expected: str, actual: str) -> List[str]:
    """diff the two given strings and return the diff as a list of strings."""
    # we want to use the unified diff function to diff the two given strings and return the diff as a list of strings
    return list(difflib.unified_diff(
        expected.splitlines(keepends=True),
        actual.splitlines(keepends=True),
        fromfile="expected_c",
        tofile="generated_c",
    ))


def run_compiler(src_path: str, no_optimize: bool = False) -> Tuple[str, str, int]:
    """we want to read the file at the given path, compile the source, and return the c code, stderr, and return code."""
    try:
        data = read_file(src_path)
        r = compile_source(data, no_optimize=no_optimize)
        return r["c_code"], "", 0
    
    except Exception as e:
        return "", f"{type(e).__name__}: {e}", 1


def run_compiler_full(src_path: str, no_optimize: bool = False) -> Tuple[Optional[Dict[str, Any]], str, str, int]:
    """we want to read the file at the given path, compile the source, and return the artifacts, c code, stderr, and return code."""
    try:
        data = read_file(src_path)
        r = compile_source(data, no_optimize=no_optimize)
        return r, r["c_code"], "", 0
    
    except Exception as e:
        return None, "", f"{type(e).__name__}: {e}", 1
