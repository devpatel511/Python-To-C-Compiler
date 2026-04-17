#!/usr/bin/env python3
"""we perform the structure checks, python to c semantic checks, golden diff, gcc compile+run"""

import os
import shutil
import subprocess
import sys

from typing import Any, Dict, List, NamedTuple, Optional, Tuple

from run_automation_common import SCRIPT_DIR, read_file, write_file, diff_lines
from run_automation_extract import (
    PY_TYPE_TO_C,
    extract_c_functions,
    extract_main_user_vars,
    extract_python_funcs,
    find_main_return0_line_index,
    find_verify_insert_line_index,
    python_val_to_ctype,
)


def load_python_example_globals(
    src_path: str,
    source_text: Optional[str] = None,
) -> Tuple[Optional[Dict[str, Any]], Optional[str], str]:
    """
    we run the example .py the same way static/gcc checks do: top-level user globals only.
    On success: (globals_dict, None, source). On exec failure: (None, error_message, source).
    Pass source_text to avoid reading the file twice when you already have it.
    """
    src = source_text if source_text is not None else read_file(src_path)

    # we want to initialize the namespace
    ns: Dict = {}

    # try to execute the source code
    try:
        exec(compile(src, src_path, "exec"), ns)
    except Exception as e:
        return None, str(e), src

    # intialize py vars dictionary (skip special names and callables; same filter everywhere)
    py_g = {
        k: v
        for k, v in ns.items()
        if not k.startswith("_") and k != "__builtins__" and not callable(v)
    }
    return py_g, None, src


def compiler_env(cc_exe: str) -> dict:
    """we set the compiler environment for the verification"""
    # we want to copy the environment variables
    env = os.environ.copy()
    # we want to get the directory name of the given compiler executable
    bindir = os.path.dirname(os.path.abspath(cc_exe))
    env["PATH"] = bindir + os.pathsep + env.get("PATH", "")
    
    return env


def find_c_compiler() -> Optional[str]:
    """we find the c compiler for the verification"""
    # we want to get the compiler executable from the environment variables
    env = os.environ.get("GCC_PATH") or os.environ.get("CC")
    # if the compiler executable is found, return it
    if env and os.path.isfile(env):
        return env
    # we want to get the bundled compiler executable
    bundled = os.path.join(
        SCRIPT_DIR, "tools", "w64devkit", "w64devkit", "bin", "gcc.exe"
    )

    # if the bundled compiler executable is found, return it
    if os.path.isfile(bundled):
        return bundled
    # we want to search for the compiler executable in the PATH
    for name in ["gcc", "cc", "tcc"]:
        p = shutil.which(name)
        # if the compiler executable is found, return it
        if p:
            return p

    return None


def checks_for_global(name: str, val, ctype: str) -> List[str]:
    """we generate the checks for the global variable for the verification"""

    out: List[str] = [] # output list default is list of strings

    # if the value is a boolean, we want to generate the checks for the boolean variable
    if isinstance(val, bool):

        if ctype == "bool":
            out.append(f"if ({name} != {'true' if val else 'false'}) return 1;")
        else:
            out.append(f"if ({name} != {1 if val else 0}) return 1;")
    # if the value is an integer or float, we want to generate the checks for the integer or float variable
    elif isinstance(val, (int, float)) and (not isinstance(val, bool)):
        out.append(f"if ({name} != {int(val)}) return 1;")
    
    # if the value is a list we want to generate the checks for the list variable
    elif isinstance(val, list):
        out.append(f"if ({name} == NULL) return 1;")
        out.append(f"if ({name}->length != {len(val)}) return 1;")
        
        for j, e in enumerate(val):
            out.append(f"if ({name}->data[{j}] != {int(e)}) return 1;")


    return out


def inject_exit_checks(c_code: str, py_globals: Dict[str, object], c_types: Dict[str, str]) -> str:
    """we inject the exit checks for the global variables for the verification"""
    # we want to split the c code into lines
    lines = c_code.splitlines()

    # we want to find the insert point before list free
    idx = find_verify_insert_line_index(lines)
    # if the insert point is not found, return the c code
    if idx is None:
        return c_code

    # generate checks for global vars
    block: List[str] = [] # output list default is list of strings

    # we want to sort global variables and go through them to generate the checks
    for name in sorted(py_globals):
        val = py_globals[name]
        if name not in c_types:
            continue
        block.extend(checks_for_global(name, val, c_types[name]))
    
    # if no checks just return the c code
    if not block:
        return c_code
    
    # indent checks and auto verify comment
    indent = "    "
    injected = [indent + "/* auto verify */"] + [indent + s for s in block]
    # return the c code with the injected checks
    return "\n".join(lines[:idx] + injected + lines[idx:]) + "\n"


def test_structure(c_code: str) -> Tuple[bool, str]:
    """we test the structure of the c code for the verification"""

    bad = [] # output list to store the errors

    # if the main function is not found, add the error to the output list
    if "int main(void)" not in c_code:
        bad.append("missing main()")

    # check valid braces
    if c_code.count("{") != c_code.count("}"):
        bad.append("unbalanced braces")
    
    # check bool and IntList usage
    if "bool " in c_code and "#include <stdbool.h>" not in c_code:
        bad.append("bool without stdbool.h")
    
    if "IntList" in c_code and "#include <stdlib.h>" not in c_code:
        bad.append("IntList without stdlib.h")

    # check main return 0
    lines = c_code.splitlines()
    if find_main_return0_line_index(lines) is None:
        bad.append("main() missing return 0")
    
    # return the res
    return (not bad, "; ".join(bad) if bad else "ok")


class StaticCompareBundle(NamedTuple):
    """bundle to store the source code, python variables, c variables, python functions and c functions"""

    # we just define a class with variables to store the source code, python variables, c variables, python functions and c functions
    source: str
    # dictionary to store the python variables
    py_vars: Dict[str, Any]
    # dictionary to store the c variables
    c_vars: Dict[str, str]
    # list and dictionary to store functions
    py_funcs: List[Tuple[str, List[str], str]]
    c_funcs: Dict[str, Tuple[str, List[str]]]


def load_static_compare_bundle(src_path: str, c_code: str) -> Tuple[Optional[str], Optional[StaticCompareBundle]]:
    """we read the .py, execute it, and pull C-side info once and return the exec error and the bundle"""
    
    # we want to read the source code from the given path
    source = read_file(src_path)

    # try to execute the source code (shared helper filters to user globals like gcc path)
    py_vars, exec_err, _ = load_python_example_globals(src_path, source)
    
    if exec_err is not None:
        return exec_err, None

    # extract the main user variables from the c code
    c_vars = extract_main_user_vars(c_code)

    # extract the python functions from the source code
    py_funcs = extract_python_funcs(source)

    # extract the c functions from the c code
    c_funcs = extract_c_functions(c_code)

    return None, StaticCompareBundle(source, py_vars, c_vars, py_funcs, c_funcs)


def _classify_py_var_vs_c_main(name: str, v: Any, c_vars: Dict[str, str]) -> Tuple[str, Optional[str], Optional[str]]:
    """we classify the py var vs the c main and return the kind, expected and actual"""

    # if the var is not in the c vars then we want to flag missing
    if name not in c_vars:
        return ("missing", None, None)
    
    # get the expected c type from the python value
    exp = python_val_to_ctype(v)

    # get the actual c type
    act = c_vars[name]

    # if the expect c type is a bool and the actual c type is an int skip it
    if exp == "bool" and act == "int":
        return ("bool_int", None, None)

    # if the actual c type is not matching the expected then we want to flag mismatch
    if act != exp:
        return ("mismatch", exp, act)

    # if the py var is ok then we want to flag ok
    return ("ok", None, None)


def static_issues_for_py_var(name: str, v: Any, c_vars: Dict[str, str]) -> List[str]:
    """Build issue strings for test_static_semantic (same rules as equivalence type check)."""

    # we classify the py var vs the c main
    kind, exp, act = _classify_py_var_vs_c_main(name, v, c_vars)

    # if the py var is missing in the c main then return the error
    if kind == "missing":
        return [f"missing '{name}' in C main()"]
    
    # if the py var is a mismatch then return the error
    if kind == "mismatch":
        return [f"'{name}': C {act} vs Python {exp}"]
    
    # if the py var is ok then return empty list
    return []


def equivalence_log_line_for_py_var(name: str, v: Any, c_vars: Dict[str, str]) -> Tuple[str, bool]:
    """we return the line for the py var in the equivalence log and bool False if this row fails overall static in the log"""
    # we classify the py var vs the c main
    kind, exp, act = _classify_py_var_vs_c_main(name, v, c_vars)
    
    if kind == "missing":
        return f"  {name}  missing in c", False
    
    if kind == "mismatch":
        return f"  {name}  fail  want {exp}  got {act}", False
    
    if kind == "bool_int":
        return f"  {name}  ok (bool as int)", True

    # if the py var is ok then return the line and True
    return f"  {name}  ok", True


def analyze_py_func_vs_c(fname: str, ppt: List[str], pret: str, c_funcs: Dict[str, Tuple[str, List[str]]]) -> Tuple[List[str], str, Optional[int]]:
    """we analyze the python function vs the c function for the verification and return the issues, kind and param index"""
    issues: List[str] = []

    # if the function in python is not in the c code we want to add the error
    if fname not in c_funcs:
        return [f"func '{fname}' missing in C"], "missing", None

    # get the c function return type and param types
    cr, cpt = c_funcs[fname]

    # get the expected return type from the python function
    er = PY_TYPE_TO_C.get(pret, "int")

    # if the c return type is not matching the expected return type then add this as an error
    if cr != er:
        issues.append(f"'{fname}' return {cr} expected {er}")

    # if the c param count is not matching the expected param count then add this as an error
    if len(cpt) != len(ppt):
        issues.append(f"'{fname}' param count mismatch")
        return issues, "sig", None

    # go through the param types and add the errors if any
    for i, (a, b) in enumerate(zip(ppt, cpt)):

        # get the expected param type from the python function
        ept = PY_TYPE_TO_C.get(a, "int")

        # if the c param type is not matching the expected param type then add this as an error
        if b != ept:
            issues.append(f"'{fname}' param {i} {b} vs {ept}")
            return issues, "param", i

    if issues:
        return issues, "sig", None
    
    return [], "ok", None


def equivalence_log_line_for_func(fname: str, kind: str, param_i: Optional[int]) -> Tuple[str, bool]:
    """we return the line for the function in the equivalence log and bool False if that function row failed"""
    
    # if the function is missing in the c code then we want to flag missing
    if kind == "missing":
        return f"  {fname}  missing in c", False
    
    # if the func is a signature mismatch then we we want to flag signature mismatch
    if kind == "sig":
        return f"  {fname}  fail  sig mismatch", False
    
    # if the func is a param mismatch then we we want to flag param mismatch
    if kind == "param":
        return f"  {fname}  fail  param {param_i}", False
    
    # if the function is ok then we want to flag ok
    return f"  {fname}  ok", True


def test_static_semantic(src_path: str, c_code: str) -> Tuple[bool, str]:
    """we test the static semantic of the c code for the verification"""

    # we want to load the static compare bundle
    exec_err, bundle = load_static_compare_bundle(src_path, c_code)


    if exec_err is not None:
        # if the source code exec fails just return the error
        return False, f"Python exec failed: {exec_err}"
    
    if bundle is None:
        return False, "bundle is None"
    
    # we want to initialize the output list to store the errors
    issues: List[str] = []

    # go through py vars and add the errors to the output list
    for name in sorted(bundle.py_vars):
        v = bundle.py_vars[name]
        issues.extend(static_issues_for_py_var(name, v, bundle.c_vars))

    # now same thing again except for the functions
    for fname, ppt, pret in bundle.py_funcs:
        func_issues, _, _ = analyze_py_func_vs_c(fname, ppt, pret, bundle.c_funcs)
        issues.extend(func_issues)

    # finally if there are any issues then return the errors
    if issues:
        return False, "; ".join(issues)

    # return the success and the number of vars and functions verified
    return True, f"{len(bundle.py_vars)} var(s), {len(bundle.py_funcs)} func(s)"


def build_equivalence_log_lines(src_path: str, c_code: str) -> Tuple[bool, List[str]]:
    """we build the equivalence log lines for the verification"""
    # we want to initialize the output list
    lines: List[str] = []

    # we want to read the source code from the given path (and run the same load/exec/extracts as test_static_semantic)
    exec_err, bundle = load_static_compare_bundle(src_path, c_code)
    if exec_err is not None:
        lines.append(f"python exec error: {exec_err}")
        return False, lines

    # if the bundle is not None then we want to return the errors
    if bundle is None:
        return False, "bundle is None"

    # we want to add the python globals to the output list
    lines.append("python globals (name  repr  ctype):")

    # we want to go through the python variables
    for name in sorted(bundle.py_vars):

        # get the python value and the python type
        v = bundle.py_vars[name]
        py_t = python_val_to_ctype(v)
        rep = repr(v)
        # if the representation is longer than 100 characters then we want to truncate it
        if len(rep) > 100:
            rep = rep[:97] + "..."
        
        # we want to add the python variable to the output list
        lines.append(f"  {name}  {rep}  {py_t}")
    
    # we want to add the c main declarations to the output list
    lines.append("c main decls (name  ctype):")

    # we want to go through the c variables
    for name in sorted(bundle.c_vars):
        lines.append(f"  {name}  {bundle.c_vars[name]}")
    
    # we want to add the type check to the output list
    lines.append("type check:")
    ok = True

    # we want to go through the python variables and add the type check to the output list
    for name in sorted(bundle.py_vars):
        line, row_ok = equivalence_log_line_for_py_var(name, bundle.py_vars[name], bundle.c_vars)
        lines.append(line)
        if not row_ok:
            ok = False

    lines.append("functions:")

    # we want to go through the python functions and add the functions to the output list
    for fname, ppt, pret in bundle.py_funcs:
        # we want to analyze the python function vs the c function
        _, kind, param_i = analyze_py_func_vs_c(fname, ppt, pret, bundle.c_funcs)
        # we want to add the function to the output list
        line, row_ok = equivalence_log_line_for_func(fname, kind, param_i)

        # we want to add the function to the output list
        lines.append(line)

        # if the function is not ok then we want to flag the static verification as failed
        if not row_ok:
            ok = False

    # we want to add the static verification status to the output list
    lines.append("static: " + ("verified" if ok else "fail"))
    return ok, lines


def describe_injected_checks_lines(src_path: str, c_code: str) -> List[str]:
    """we list the gcc injected checks for the verification log"""

    # we want to extract the main user variables from the c code
    c_vars = extract_main_user_vars(c_code)

    # we want to load the python example globals
    py_g, exec_err, _ = load_python_example_globals(src_path)


    if exec_err is not None:
        return [f"python exec error: {exec_err}"]
    
    # we want to initialize the output list
    lines: List[str] = ["gcc injected (before free/return):"]
    n = 0
    
    # we want to go through the python variables and add the checks
    for name in sorted(py_g):

        # if the variable is not in the c vars then we want to skip it
        if name not in c_vars:
            continue

        # get the python value and the c type
        val = py_g[name]
        ctype = c_vars[name]

        # we want to go through the checks and add them to the output list
        for stmt in checks_for_global(name, val, ctype):
            lines.append(stmt)
            n += 1
    
    # if there are no checks then we want to add a message to the output list
    if n == 0:
        lines.append("(none)")

    return lines


def test_golden(c_code: str, path: str) -> Tuple[Optional[bool], str]:
    """we diff generated c against the golden expected file when present"""

    # if the path is not a file then we want to return the error
    if not os.path.isfile(path):
        return None, "(no expected c file)"

    
    # we want to read the expected file and the generated c code
    exp = read_file(path).replace("\r\n", "\n").rstrip("\n")
    act = c_code.replace("\r\n", "\n").rstrip("\n")

    # we want to diff the expected and the actual c code
    d = diff_lines(exp + "\n", act + "\n")

    # if the diff is not empty we want to return the error
    if d:
        return False, "".join(d)

    # if the diff is empty just return sucess
    return True, "ok"


def test_gcc_run(c_code: str, cc: str, tmp: str, stem: str, src_path: str) -> Tuple[bool, str]:
    """we compile and run patched c with injected checks to verify against python globals"""

    # we extract the main user variables from the c code
    c_vars = extract_main_user_vars(c_code)

    # load the python example globals
    py_g, exec_err, _ = load_python_example_globals(src_path)
    if exec_err is not None:
        return False, f"Python exec failed: {exec_err}"

    # inject the exit checks into the c code
    patched = inject_exit_checks(c_code, py_g, c_vars)

    # write the patched c code to a file
    c_path = os.path.join(tmp, f"{stem}_v.c")
    ext = ".exe" if sys.platform == "win32" else ""
    exe = os.path.join(tmp, f"{stem}_v{ext}")
    write_file(patched, c_path)

    # compile the c code
    comp = subprocess.run(
        [cc, c_path, "-o", exe],
        capture_output=True,
        text=True,
        timeout=60,
        env=compiler_env(cc),
    )

    comp_stdout = (comp.stdout or "").strip()
    comp_stderr = (comp.stderr or "").strip()
    comp_raw: str = ""
    if comp_stdout or comp_stderr:
        comp_raw = f"gcc stdout:\n{comp_stdout}\n\ngcc stderr:\n{comp_stderr}".strip()

    # if compile fails then return the error, including raw gcc output
    if comp.returncode != 0:
        if comp_raw:
            return False, f"gcc compile failed (rc={comp.returncode})\n{comp_raw}"
        return False, f"gcc compile failed (rc={comp.returncode})"

    # if it passes, then run the executable
    run = subprocess.run(
        [exe], capture_output=True, text=True, timeout=15, env=compiler_env(cc)
    )

    run_stdout = (run.stdout or "").strip()
    run_stderr = (run.stderr or "").strip()
    run_raw: str = ""
    if run_stdout or run_stderr:
        run_raw = f"program stdout:\n{run_stdout}\n\nprogram stderr:\n{run_stderr}".strip()

    # if the run fails then return the error
    if run.returncode != 0:
        parts = [f"program exit {run.returncode} (value mismatch)"]
        if comp_raw:
            parts.append(comp_raw)
        if run_raw:
            parts.append(run_raw)
        return False, "\n\n".join(parts)

    # if it passes, then return success
    if comp_raw:
        return True, f"ok\n\n{comp_raw}"
    return True, "ok"
