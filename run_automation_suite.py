#!/usr/bin/env python3
"""run the actual example(s) or input file(s)"""

import os
from typing import Any, Dict, Iterator, List, Optional, Tuple

from run_automation_common import SCRIPT_DIR, generated_c_basename, read_file, run_compiler, run_compiler_full, write_file
from run_automation_logging import write_log_entry
from run_automation_verify import test_gcc_run, test_golden, test_static_semantic, test_structure

# Log tail for write_log_entry when compile produced no C (golden/static/gcc N/A).
_PIPELINE_FAIL_LOG_TAIL = (None, "", False, "-", False, "-", None, "-")


def iter_example_py_by_dirs(dirs: List[str], *, warn_missing: bool = False) -> Iterator[Tuple[str, str, str, str, str, str]]:
    """we yield the directory, file name, stem, source path, sub, and output name per example"""
    multi = len(dirs) > 1

    # we want to iterate over the directories
    for d in dirs:
        dpath = os.path.join(SCRIPT_DIR, d)

        if not os.path.isdir(dpath):
            # if the directory is not found we want to warn the user
            if warn_missing:
                print(f"skip missing dir {d}")
            continue

        # get sub dir name
        sub = d.replace(os.sep, "_").replace("/", "_")
        
        # iterate over files in the dir ending with .py
        for fn in sorted(x for x in os.listdir(dpath) if x.endswith(".py")):
            # yield the directory, file name, stem, source path, sub, and output name
            stem = os.path.splitext(fn)[0]
            src = os.path.join(dpath, fn)
            out_name = f"{sub}__{stem}.c" if multi else f"{stem}.c"
            yield d, fn, stem, src, sub, out_name


def log_pipeline_failure(
    log_root: Optional[str],
    out_name: str,
    opt_label: str,
    rel: str,
    src: str,
    source_text: str,
    artifacts: Optional[Dict[str, Any]],
    err: str,
    log_ast: bool,
) -> None:
    """we log the pipeline failure"""
    # if the log root is not None we want to write the log entry
    print(f"  pipeline fail  {err}")

    if log_root:
        write_log_entry(log_root, out_name, opt_label, rel, src, source_text, artifacts, err, "", *_PIPELINE_FAIL_LOG_TAIL, log_ast)
    # we want to print a new line
    print()

# for running one example or input file
def run_one_example(
    src: str,
    rel: str,
    out_name: str,
    gcc_stem: str,
    exp_path: Optional[str],
    output_root: str,
    cc: Optional[str],
    tmp: str,
    no_optimize: bool,
    verbose: bool,
    log_root: Optional[str] = None,
    log_ast: bool = False,
) -> Tuple[int, int]:
    """we run one example, compile one .py, run structure / optional golden / static / gcc. we return the passed and failed counts"""

    # we want to get the optimization label, src text and outpath path
    opt_label = "unoptimized" if no_optimize else "optimized"
    source_text = read_file(src)
    out_path = os.path.join(output_root, opt_label, generated_c_basename(out_name))
    print(f"{rel}  ({opt_label})")

    # we want to run the compiler full or not depending on the log root
    if log_root:
        artifacts, c_raw, stderr_c, rc = run_compiler_full(src, no_optimize=no_optimize)
    else:
        artifacts, c_raw, stderr_c, rc = None, *run_compiler(src, no_optimize=no_optimize)
    
    # we want to get the c code
    c_code = (c_raw or "").strip()

    # if the compiler returned an error we want to log the pipeline failure
    if rc != 0:
        log_pipeline_failure(log_root, out_name, opt_label, rel, src, source_text, artifacts, stderr_c or str(rc), log_ast)
        return 0, 1
    
    # if the c code is empty we want to log the pipeline failure
    if not c_code:
        log_pipeline_failure(log_root, out_name, opt_label, rel, src, source_text, artifacts, "empty c", log_ast)
        return 0, 1

    print(f"  pipeline pass  {len(c_code.splitlines())} lines")

    # we want to write the c code to the output path
    write_file(c_code + "\n", out_path)
    
    # if verbose is True we want to print the c code
    if verbose:
        print("\n".join(f"  {ln}" for ln in c_code.splitlines()))

    
    struct_ok, struct_msg = test_structure(c_code)
    print(f"  structure {'pass' if struct_ok else 'fail  ' + struct_msg}")
    bad = not struct_ok
    
    # if the expected path is None we want to set the golden ok and message to None and "(single file / no golden compare)"
    if exp_path is None:
        golden_ok, golden_msg = None, "(single file / no golden compare)"
    else:
        golden_ok, golden_msg = test_golden(c_code, exp_path)

    # if the golden ok is None we want to print the golden skip message
    # For suite verification (exp_path is provided), a missing expected file should fail loudly.
    if golden_ok is None:
        print(f"  golden skip  {golden_msg}")
        if exp_path is not None:
            bad = True

    elif golden_ok:
        print(f"  golden pass (gen vs expected c)  {golden_msg}")

    else:
        # if the golden ok is False we want to print the golden fail message
        print("  golden fail (gen vs expected c)")

        if verbose and golden_msg.strip():
            print("\n".join(golden_msg.splitlines()))
        bad = True

    # we want to test the static semantic
    static_ok, static_msg = test_static_semantic(src, c_code)
    print(f"  static {'pass  ' + static_msg if static_ok else 'fail  ' + static_msg}")
    bad = bad or not static_ok

    # we want to test the gcc run
    gcc_ok, gcc_msg = None, "no compiler"
    
    if cc:
        gcc_ok, gcc_msg = test_gcc_run(c_code, cc, tmp, gcc_stem, src)
        print(f"  gcc {'pass' if gcc_ok else 'fail'}  {gcc_msg}")
        bad = bad or not gcc_ok

    else:
        print("  gcc skip")

    # if the log root is not None we want to write the log entry
    if log_root:
        write_log_entry(log_root, out_name, opt_label, rel, src, source_text, artifacts, "", c_code, golden_ok, golden_msg, struct_ok, struct_msg, static_ok, static_msg, gcc_ok, gcc_msg, log_ast)
    
    print()

    return (int(not bad), int(bad))


# just running one file using run one example
def run_single_file(
    py_path: str,
    output_root: str,
    cc: Optional[str],
    tmp: str,
    no_optimize: bool,
    verbose: bool,
    log_root: Optional[str] = None,
    log_ast: bool = False,
) -> Tuple[int, int]:
    """we run one file using run one example"""
    # if the py path is not a file we want to print the error and return 0, 1
    if not os.path.isfile(py_path):
        print(f"not found: {py_path}")
        return 0, 1
    
    if not py_path.endswith(".py"):
        print(f"expected .py file: {py_path}")
        return 0, 1
    
    stem = os.path.splitext(os.path.basename(py_path))[0]
    out_name = stem + ".c"
    
    return run_one_example(py_path, stem + "_file", out_name, stem + "_file", None, output_root, cc, tmp, no_optimize, verbose, log_root, log_ast)


def run_suite(
    dirs: List[str],
    output_root: str,
    expected_root: str,
    cc: Optional[str],
    tmp: str,
    no_optimize: bool,
    verbose: bool,
    log_root: Optional[str] = None,
    log_ast: bool = False,
) -> Tuple[int, int]:
    """we run the suite, iterate over the directories, run one example for each file"""
    passed = failed = 0
    suffix = "_noopt" if no_optimize else ""

    # iterate over the directories, run one example for each file
    # get the directory, file name, stem, source path, sub, and output name
    for d, fn, stem, src, sub, out_name in iter_example_py_by_dirs(dirs, warn_missing=True):
        # expected path
        exp_path = os.path.join(expected_root + suffix, out_name)
        # relative path
        rel = f"{d}/{fn}"
        p_inc, f_inc = run_one_example(src, rel, out_name, stem + "_" + sub, exp_path, output_root, cc, tmp, no_optimize, verbose, log_root, log_ast)
        # track what passed and failed
        passed += p_inc
        failed += f_inc

    # return the passed and failed counts
    return passed, failed


def generate_expected(dirs: List[str], expected_root: str, no_optimize: bool):
    """we generate the expected output, iterate over the directories, run one example for each file"""
    # suffix for no optimization
    suf = "_noopt" if no_optimize else ""
    # root for the expected output
    root = expected_root + suf
    os.makedirs(root, exist_ok=True)
    # iterate over the directories, run one example for each file
    # get the directory, file name, stem, source path, sub, and output name
    for _d, _fn, _stem, src, _sub, out_name in iter_example_py_by_dirs(dirs, warn_missing=False):
        out = os.path.join(root, out_name)
        # run the compiler
        c_out, _, rc = run_compiler(src, no_optimize=no_optimize)
        # if the compiler returned an error we want to print the error and continue
        if rc == 0 and c_out.strip():
            write_file(c_out.strip() + "\n", out)
            print(f"wrote {out_name}")
        
        else:
            print(f"err {out_name}")
