#!/usr/bin/env python3
"""package for run_automation"""

# import all the common functions and vars
from run_automation_common import DEFAULT_DIRS, SCRIPT_DIR, diff_lines, generated_c_basename, read_file, run_compiler, run_compiler_full, write_file

# import all the functions and vars from the other modules
from run_automation_extract import PY_TYPE_TO_C
from run_automation_logging import extend_log_golden_section, log_entry_ok_line, write_log_entry
from run_automation_suite import generate_expected, iter_example_py_by_dirs, run_one_example, run_single_file, run_suite
from run_automation_verify import (
    build_equivalence_log_lines,
    checks_for_global,
    compiler_env,
    describe_injected_checks_lines,
    find_c_compiler,
    inject_exit_checks,
    load_python_example_globals,
    test_gcc_run,
    test_golden,
    test_static_semantic,
    test_structure,
)

# export all the functions and variables
__all__ = [
    "DEFAULT_DIRS",
    "SCRIPT_DIR",
    "PY_TYPE_TO_C",
    "build_equivalence_log_lines",
    "checks_for_global",
    "compiler_env",
    "describe_injected_checks_lines",
    "diff_lines",
    "extend_log_golden_section",
    "find_c_compiler",
    "generated_c_basename",
    "generate_expected",
    "inject_exit_checks",
    "iter_example_py_by_dirs",
    "load_python_example_globals",
    "log_entry_ok_line",
    "read_file",
    "run_compiler",
    "run_compiler_full",
    "run_one_example",
    "run_single_file",
    "run_suite",
    "test_gcc_run",
    "test_golden",
    "test_static_semantic",
    "test_structure",
    "write_file",
    "write_log_entry",
]
