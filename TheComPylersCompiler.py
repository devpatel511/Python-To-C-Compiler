#!/usr/bin/env python3

import argparse
import sys

from typing import Any, Dict, List

from parser import TheComPylersParser
from ir_gen import TheComPylersIRGen
from ir_optimizer import TheComPylersIROptimizer
from type_checker import TheComPylersTypeChecker
from c_codegen import TheComPylersCCodeGenerator


def print_ir_list(label: str, ir_list: List[str]) -> None:
    print(label, file=sys.stderr)
    for line in ir_list:
        s = str(line)
        if s:
            print(s, file=sys.stderr)


def compile_source(data: str, *, no_optimize: bool = False) -> Dict[str, Any]:
    """
    Run the full pipeline: parse, typecheck, IR, optional optimize, C codegen.
    Returns AST (JSON-serializable dict), IR text lines, and C source.
    """
    # Build and runs the parser to get AST
    parser = TheComPylersParser()
    parser.build()
    root = parser.parse(data)
    if root is None:
        raise RuntimeError("Parse error: no AST produced")

    type_checker = TheComPylersTypeChecker()
    global_st = type_checker.typecheck(root)

    ir_generator = TheComPylersIRGen()
    ir_generator.generate(root)

    if no_optimize:
        optimized_ir = ir_generator.IR_obj
    else:
        optimized_ir = TheComPylersIROptimizer(ir_generator.IR_obj)

    ir_opt_lines = [str(i) for i in optimized_ir if str(i).strip()]

    c_generator = TheComPylersCCodeGenerator()
    c_code = c_generator.generate(optimized_ir, global_st)

    return {
        "ast_dict": root.to_dict(),
        "ir_unoptimized_lines": list(ir_generator.IR_lst),
        "ir_optimized_lines": ir_opt_lines,
        "c_code": c_code,
    }


if __name__ == "__main__":

    # Python module "argparse" allows you to easily add commandline flags
    # to your program, which can help with adding debugging options, such
    # as '--verbose' and '--print-ast' as described below.
    #
    # Of course, this is entirely optional and not necessary, as long as
    # the compiler functions correctly.
    argparser = argparse.ArgumentParser(description='Take in the Python Subset source code and compile it')
    argparser.add_argument('FILE', help="Input file")
    argparser.add_argument('-p', '--parse-only', action='store_true', help="Stop after scanning and parsing the input")
    argparser.add_argument('-v', '--verbose', action='store_true', help="Provides additional output")
    argparser.add_argument('--no-optimize', action='store_true', help="Skip IR optimization passes")
    argparser.add_argument('--emit-ir', action='store_true', help="Print IR before and after optimization to stderr")
    args = argparser.parse_args()

    # Prints additional output if the flag is set
    if args.verbose:
        print("* Reading file " + args.FILE + "...")

    with open(args.FILE, encoding="utf-8") as f:
        data = f.read()

    # If user asks to quit after parsing, do so.
    if args.parse_only:
        if args.verbose:
            print("* Scanning and Parsing...")
        # Build and runs the parser to get AST
        parser = TheComPylersParser()
        parser.build()
        parser.parse(data)
        quit()

    if args.verbose:
        print("* Compiling (parse, types, IR, codegen)...")

    try:
        result = compile_source(data, no_optimize=args.no_optimize)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    if args.emit_ir:
        print_ir_list("--- IR (unoptimized) ---", result["ir_unoptimized_lines"])
        if args.no_optimize:
            print("--- IR (optimized) --- (skipped, --no-optimize)", file=sys.stderr)
        else:
            print_ir_list("--- IR (optimized) ---", result["ir_optimized_lines"])

    print(result["c_code"])
