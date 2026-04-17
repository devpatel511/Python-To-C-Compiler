#!/usr/bin/env python3
"""setup log files."""

import json
import os
from typing import Any, Dict, List, Optional

from run_automation_common import generated_c_basename, write_file
from run_automation_verify import build_equivalence_log_lines, describe_injected_checks_lines


def extend_log_golden_section(lines: List[str], golden_ok: Optional[bool], golden_msg: str) -> None:
    """we extend the log golden section"""

    lines.extend(["", "--- golden (generated c vs expected c) ---"])

    # if the golden ok is None then we want to add the skipped message
    if golden_ok is None:
        lines.append("skipped")
        if golden_msg.strip():
            lines.append(golden_msg.rstrip())
    
    # if the golden ok is True then we want to add the pass message
    elif golden_ok:
        lines.append("pass")
    
    # if the golden ok is False then we want to add the fail message
    else:
        lines.append("fail")
        if golden_msg.strip():
            lines.append(golden_msg.rstrip())


def log_entry_ok_line(
    compile_err: str, c_code: str, static_ok: bool, gcc_ok: Optional[bool],
) -> str:
    """we return the ok: yes/no summary line"""

    # if the compile error is not empty and the c code is empty then we want to return the no message
    if compile_err and not c_code.strip():
        return "ok: no"
    
    # if the static ok is False then we want to return the no static message
    if not static_ok:
        return "ok: no  static"

    # if the gcc ok is False then we want to return the no gcc message
    if gcc_ok is False:
        return "ok: no  gcc"
    
    # if the gcc ok is True and the static ok is True then we want to return the yes static+gcc message
    if gcc_ok is True and static_ok:
        return "ok: yes  static+gcc"

    return "ok: yes  static only"


def write_log_entry(
    log_root: str,
    out_name: str,
    mode_label: str,
    rel_src: str,
    src_path: str,
    source_text: str,
    artifacts: Optional[Dict[str, Any]],
    compile_err: str,
    c_code: str,
    golden_ok: Optional[bool],
    golden_msg: str,
    struct_ok: bool,
    struct_msg: str,
    static_ok: bool,
    static_msg: str,
    gcc_ok: Optional[bool],
    gcc_msg: str,
    log_ast: bool,
) -> None:

    # we want to get the base name of the output file
    base = os.path.splitext(out_name)[0]
    
    # we want to get the generated c basename
    gen_bn = generated_c_basename(out_name)
    
    # we want to create the log root directory if it doesn't exist
    os.makedirs(log_root, exist_ok=True)
    
    # we want to create the log path
    path = os.path.join(log_root, base + ".txt")
    
    # we want to initialize the output list
    lines: List[str] = [
        rel_src,
        mode_label,
        f"generated file {gen_bn}",
        f"expected c (golden) {out_name}",
        "",
        "--- python ---",
        source_text.rstrip(),
        "",
        "--- c ---",
    ]

    # if the c code is not empty then we want to add it to the output list
    if c_code.strip():
        lines.append(c_code)
    
    # if the c code is empty then we want to add the compile error or (no c) message
    else:
        lines.append(compile_err or "(no c)")

    # we want to extend the log golden section
    extend_log_golden_section(lines, golden_ok, golden_msg)

    # we want to add the structure section
    lines.extend(["", "--- structure ---", f"{'pass' if struct_ok else 'fail'}  {struct_msg}"])
    
    # we want to add the static section
    lines.extend(["", "--- static ---", f"{'pass' if static_ok else 'fail'}  {static_msg}"])

    # if the c code is not empty then we want to add the python vs c section
    if c_code.strip():
        lines.extend(["", "--- python vs c ---"])
        _eq_ok, eq_lines = build_equivalence_log_lines(src_path, c_code)
        lines.extend(eq_lines)
    
    # we want to add the ast section
    lines.extend(["", "--- ast ---"])
    if log_ast and artifacts and "ast_dict" in artifacts:
        apath = os.path.join(log_root, "ast", base + ".json")
        os.makedirs(os.path.dirname(apath), exist_ok=True)
        with open(apath, "w", encoding="utf-8") as af:
            json.dump(artifacts["ast_dict"], af, indent=2)
        lines.append(f"written  {apath}")
    else:
        lines.append("skipped")
        if not log_ast:
            lines.append("(--log-ast not set)")
        elif not (artifacts and "ast_dict" in artifacts):
            lines.append("(no ast_dict in compile result)")
    
    # now we add the gcc section
    lines.extend(["", "--- gcc ---"])
    if gcc_ok is None:
        lines.append(f"skip  {gcc_msg}")
    else:
        lines.append(f"{'pass' if gcc_ok else 'fail'}  {gcc_msg}")
    
    # if the c code is not empty then we want to add the injected checks section
    if c_code.strip():
        lines.append("")
        lines.extend(describe_injected_checks_lines(src_path, c_code))
    
    # finally we add the ok line
    lines.append("")
    lines.append(log_entry_ok_line(compile_err, c_code, static_ok, gcc_ok))
    lines.append("")

    # then we write the lines to the file
    write_file("\n".join(lines), path)
