#!/usr/bin/env python3
"""Compiler automation"""
import argparse
import os
import shutil
import sys
import tempfile
from typing import List, Optional, Tuple

from run_automation_helpers import (
    DEFAULT_DIRS,
    SCRIPT_DIR,
    find_c_compiler,
    run_compiler_full,
    run_single_file,
    run_suite,
    write_file,
)


def resolve_log_subdir(log_session: Optional[str], log_sub: Optional[str]) -> Optional[str]:
    """we resolve the log subdirectory"""
    # if the log session is None we want to return None
    if not log_session:
        return None
    # otherwise we want to join the log session and the log subdirectory
    lr = os.path.join(log_session, log_sub) if log_sub else log_session
    if log_sub:
        os.makedirs(lr, exist_ok=True)
    return lr


def build_mode_rounds(both_modes: bool, no_optimize: bool, log_session: Optional[str]) -> List[Tuple[bool, Optional[str], str]]:
    """we build the mode rounds"""
    if both_modes:
        return [(False, "opt" if log_session else None, "optimized"), (True, "noopt" if log_session else None, "no-optimize")]
    # otherwise we want to return the list of tuples
    return [(no_optimize, None, "no-optimize" if no_optimize else "optimized")]


def run_invalid_examples(tmp: str, log_root: Optional[str]) -> Tuple[int, int]:
    """Run all invalid examples and assert compilation fails in both modes."""
    neg_pass, neg_fail = 0, 0
    invalid_dir = os.path.join(SCRIPT_DIR, "examples", "invalid")
    invalid_files = sorted(
        fn for fn in os.listdir(invalid_dir) if fn.endswith(".py") and not fn.startswith("_")
    ) if os.path.isdir(invalid_dir) else []

    lines: List[str] = ["--- invalid examples ---"]

    if not invalid_files:
        msg = "No invalid examples found in examples/invalid; skipping negative tests."
        print(msg)
        lines.append(msg)
    else:
        for fn in invalid_files:
            py_path = os.path.join(invalid_dir, fn)
            for no_opt in (False, True):
                mode = "no-optimize" if no_opt else "optimized"
                _, _, stderr, rc = run_compiler_full(py_path, no_optimize=no_opt)
                if rc == 0:
                    neg_fail += 1
                    msg = f"invalid FAIL {fn} (mode={mode}) rc=0; stderr={stderr}"
                    print(msg)
                    lines.append(msg)
                else:
                    neg_pass += 1
                    err = (stderr or "").strip()
                    # Keep logs readable: include a short error excerpt for the grader/reader.
                    if len(err) > 500:
                        err = err[:500] + " ... (truncated)"
                    msg = f"invalid PASS {fn} (mode={mode}) rc={rc}; stderr={err}"
                    print(msg)
                    lines.append(msg)

    lines.append("")
    lines.append(f"invalid pass {neg_pass}  fail {neg_fail}")

    if log_root:
        os.makedirs(log_root, exist_ok=True)
        write_file("\n".join(lines) + "\n", os.path.join(log_root, "invalid_examples.txt"))

    return neg_pass, neg_fail



####
# We handle the Arguement parser here for the command line arguments for the automation script
####
def main() -> None:

    # setup the argparser
    ap = argparse.ArgumentParser(description="Sprint 4 compiler automation.")
    ap.add_argument("--dirs", nargs="*", default=DEFAULT_DIRS, help="Example dirs (under sprint4)")
    ap.add_argument("--output-dir", default="output", help="Generated C root")
    ap.add_argument("--expected-dir", default="examples_expected", help="Golden .c root (+ _noopt)")
    ap.add_argument("--no-optimize", action="store_true", help="Skip IR optimizer")
    ap.add_argument("--both-modes", action="store_true", help="Run opt then no-opt")
    ap.add_argument("--verbose", action="store_true", help="Print full golden diff (generated vs expected c) and full generated c")
    # Expected outputs are submitted as-is and verification-only mode is used.
    ap.add_argument("--log", nargs="?", const="output/log", default=None, metavar="DIR", help="Write verification logs under DIR/ (overwrites each run; default: output/log)")
    ap.add_argument("--log-ast", action="store_true", help="With --log, also write ast/*.json")
    ap.add_argument("--file", metavar="PY", help="Single .py path: compile, verify (no golden), log (default log dir: output/log unless --log given)")
    args = ap.parse_args()
    
    # get the current working directory
    invoke_cwd = os.getcwd()

    # if file and log is None we want to set the log to the default log directory
    if args.file and args.log is None:
        args.log = "output/log"
    
    # change the current working directory to the script directory
    os.chdir(SCRIPT_DIR)

    # find the c compiler
    cc = find_c_compiler()

    # create a temporary directory for the compiler
    tmp = tempfile.mkdtemp(prefix="tc4_")

    # try to run the compiler
    try:
        print(f"python {sys.executable}")
        print(f"cc {cc or 'none'}")
        
        if args.file:
            print(f"file {args.file}")
        
        else:
            print(f"dirs {args.dirs}")
        
        if args.log:
            print(f"log {args.log}" + (" log-ast" if args.log_ast else ""))
        print("")

        # if the file is given we want to run the single file
        if args.file:
            py_path = args.file if os.path.isabs(args.file) else os.path.normpath(os.path.join(invoke_cwd, args.file))
            log_session = os.path.abspath(args.log) if args.log else None
            if log_session:
                os.makedirs(log_session, exist_ok=True)
            total_pass = 0
            total_fail = 0

            file_rounds = build_mode_rounds(args.both_modes, args.no_optimize, log_session)
            # run the single file for the given mode rounds
            for no_opt, log_sub, mode_title in file_rounds:
                print(f"mode {mode_title}")
                print("")
                lr = resolve_log_subdir(log_session, log_sub)
                p, f = run_single_file(
                    py_path,
                    args.output_dir,
                    cc,
                    tmp,
                    no_optimize=no_opt,
                    verbose=args.verbose,
                    log_root=lr,
                    log_ast=args.log_ast,
                )
                total_pass += p
                total_fail += f

            # if the log session is not None we want to print the log session
            if log_session:
                print(f"log {log_session}")
            print(f"pass {total_pass}  fail {total_fail}")

            neg_pass, neg_fail = run_invalid_examples(tmp, log_session)
            total_pass += neg_pass
            total_fail += neg_fail
            print(f"invalid pass {neg_pass}  fail {neg_fail}")

            print(f"TOTAL pass {total_pass}  fail {total_fail}")
            sys.exit(0 if total_fail == 0 else 1)

        total_pass = 0
        total_fail = 0
        log_session: Optional[str] = None

        if args.log:
            # if the log is given we want to set the log session to the absolute path of the log
            log_session = os.path.abspath(args.log)
            os.makedirs(log_session, exist_ok=True)

        # build the mode rounds
        dir_rounds = build_mode_rounds(args.both_modes, args.no_optimize, log_session)

        for no_opt, log_sub, mode_title in dir_rounds:
            # print the mode title
            print(f"mode {mode_title}")
            print("")
            # resolve the log subdirectory
            lr = resolve_log_subdir(log_session, log_sub)
            # run the suite for the given directories
            p, f = run_suite(
                args.dirs,
                args.output_dir,
                args.expected_dir,
                cc,
                tmp,
                no_optimize=no_opt,
                verbose=args.verbose,
                log_root=lr,
                log_ast=args.log_ast,
            )
            # track the total passed and failed
            total_pass += p
            total_fail += f

        # print the log session
        if log_session:
            print(f"log {log_session}")

        # print the total passed and failed
        print(f"pass {total_pass}  fail {total_fail}")

        neg_pass, neg_fail = run_invalid_examples(tmp, log_session)
        total_pass += neg_pass
        total_fail += neg_fail
        print(f"invalid pass {neg_pass}  fail {neg_fail}")

        print(f"TOTAL pass {total_pass}  fail {total_fail}")
        sys.exit(0 if total_fail == 0 else 1)

    finally:
        # remove the temporary directory
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
