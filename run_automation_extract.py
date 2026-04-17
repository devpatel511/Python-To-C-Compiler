#!/usr/bin/env python3
"""we parse the c/python snippets for verification"""

import re
from typing import Dict, List, Optional, Tuple

# set the py type to c type mapping for the verification
PY_TYPE_TO_C = {"int": "int", "bool": "bool", "list[int]": "IntList*"}


def python_val_to_ctype(val) -> str:
    """we conver the python value to the c type for the verification"""
    # check the type of val and return the c type
    if isinstance(val, bool):
        return "bool"
    if isinstance(val, int):
        return "int"
    if isinstance(val, float) and val.is_integer():
        return "int"
    if isinstance(val, list):
        return "IntList*"
    # if the value is not a bool, int, float, or list, return int
    return "int"


def extract_main_user_vars(c_code: str) -> Dict[str, str]:
    """we extract the main user variables from the c code for the verification"""
    out: Dict[str, str] = {}
    in_main = False
    depth = 0

    for line in c_code.splitlines():
        s = line.strip()
        # we want to check if the line is the main function declaration
        if "int main(void)" in s:
            in_main = True
            depth += s.count("{") - s.count("}")
            continue

        # we want to skip the lines that are not in the main function
        if not in_main:
            continue

        # count the number of opening and closing braces to check if we are in the main function
        depth += s.count("{") - s.count("}")

        # break out of the loop if we are not in the main function
        if depth <= 0:
            break

        # regex to match the variable declaration
        m = re.match(r"(int|bool|IntList\*)\s+([a-zA-Z_]\w*)", s)

        # if valid pattern then add the variable to the output dictionary
        if m:
            ct, name = m.group(1), m.group(2)
            if not name.startswith("_t"):
                out[name] = ct

    # return the output dict
    return out


def extract_python_funcs(source: str) -> List[Tuple[str, List[str], str]]:
    """we extract the python functions from the source code for the verification"""
    # we want to initialize the result list
    res = []

    # find all the function definitions in the source code
    for m in re.finditer(r"def\s+(\w+)\s*\(([^)]*)\)\s*->\s*(\S+)\s*:", source):
        # get the function name, return type and the param types
        name = m.group(1)
        ret = m.group(3).rstrip(":")
        pts = []

        # split the param types by commas and add to the res list
        for p in m.group(2).split(","):
            p = p.strip()
            # if the param has a colon, split and add the second part to the pts list
            if ":" in p:
                pts.append(p.split(":", 1)[1].strip())

        # add the function name, param types and return type to the result list
        res.append((name, pts, ret))

    return res


def extract_c_functions(c_code: str) -> Dict[str, Tuple[str, List[str]]]:
    """we extract the c functions from the c code for the verification"""
    # initial the output dict
    funcs: Dict[str, Tuple[str, List[str]]] = {}

    # we want to skip the main function, list_new function and int_list_free function
    skip = {"main", "list_new", "int_list_free"}

    # find all the function definitions in the c code
    for m in re.finditer(r"(int|bool)\s+(\w+)\s*\(([^)]*)\)\s*\{", c_code):
        ret, name, ps = m.group(1), m.group(2), m.group(3)
        if name in skip:
            continue

        ptypes = []

        if ps.strip():
            for p in ps.split(","):
                parts = p.strip().rsplit(" ", 1)
                if len(parts) == 2:
                    ptypes.append(parts[0].strip())

        # add the function name, return type and param types to the output dict
        funcs[name] = (ret, ptypes)

    # return the output dict
    return funcs


def find_main_return0_line_index(lines: List[str]) -> Optional[int]:
    """we find the main function return 0 line index for the verification"""

    main_i = None
    # find the main function return 0 line index
    for i, line in enumerate(lines):
        # if named main function then set the main function return 0 line index
        if "int main(void)" in line:
            main_i = i
            break

    # if the main function return 0 line index is not found, return None
    if main_i is None:
        return None

    depth = 0
    # find the main function return 0 line index where we go through the lines
    for i in range(main_i, len(lines)):

        line = lines[i]
        s = line.strip()
        
        # count the number of opening and closing braces to check if we are in the main function
        if i == main_i:
            depth += line.count("{") - line.count("}")
            continue
        
        # if the line is the main function return 0 line and the depth is 1, return the index
        if s == "return 0;" and depth == 1:
            return i
        
        # accumulate depth by the number of opening and closing braces
        depth += line.count("{") - line.count("}")
    
    # if the main function return 0 line index is not found, return None
    return None


def find_verify_insert_line_index(lines: List[str]) -> Optional[int]:
    """we find the insert point before list free / return 0 for the verification"""
    # find the main function return 0 line index
    main_i = None
    for i, line in enumerate(lines):
        if "int main(void)" in line:
            main_i = i
            break
    
    if main_i is None:
        return None
    
    depth = 0
    ret_i = None
    
    # find the insert point before list free / return 0 where we go through the lines
    for i in range(main_i, len(lines)):
        line = lines[i]
        s = line.strip()
        
        if i == main_i:
            depth += line.count("{") - line.count("}")
            continue
        
        depth += line.count("{") - line.count("}")
        
        if s == "return 0;" and depth == 1:
            ret_i = i
            break
    
    if ret_i is None:
        return None
    
    insert_at = ret_i
    
    # we now go through the lines backwards to find the insert point
    for i in range(ret_i - 1, main_i, -1):
        s = lines[i].strip()
        # if the line is the return 0 line or the intlist free line then we want to set the insert at index
        if s == "return 0;" or s.startswith("int_list_free("):
            insert_at = i
        # just break out otherwise
        else:
            break
    
    return insert_at
