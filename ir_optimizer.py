#!/usr/bin/env python3

import re

from ir_gen import IRAssign, IRBeginFunc, IRCondJump, IREndFunc
from ir_gen import IRFuncCall, IRJump, IRLabel, IRPopParams, IRPushParam
from ir_gen import IRBeginWhile, IREndWhile, IRBeginIf, IREndIf, IRElse

def is_constant(val):
    """Check if a value is a numeric constant."""
    try:
        int(str(val))
        return True
    except Exception:
        return False

def is_temp(name):
    return isinstance(name, str) and re.match(r'^_t\d+$', name) is not None

def parse_binop(value):
    if not isinstance(value, str):
        return None
    ops = ['<=', '>=', '==', '!=', '<<', '>>', 'and', 'or', '+', '-', '*', '/', '%', '<', '>']
    for op in ops:
        token = f' {op} '
        if token in value:
            left, right = value.split(token, 1)
            return left.strip(), op, right.strip()
    return None

def constant_folding(ir_code):
    """
    Optimization: Evaluate constant expressions at compile time.

    Example:
        _t1 := 2 + 3  -->  _t1 := 5
    """
    result = []

    for instr in ir_code:
        folded = None

        if isinstance(instr, IRAssign) and isinstance(instr.value, str):
            # Unary fold
            if instr.value.startswith('not '):
                operand = instr.value[4:].strip()
                if str(operand) in ('True', 'False') or is_constant(operand):
                    val = bool(int(str(operand))) if is_constant(operand) else (str(operand) == 'True')
                    folded = 'True' if (not val) else 'False'
            elif instr.value.startswith('- '):
                operand = instr.value[2:].strip()
                if is_constant(operand):
                    folded = str(-int(str(operand)))

            parsed_binop = parse_binop(instr.value) if folded is None else None
            if parsed_binop is not None and folded is None:
                left, op, right = parsed_binop
                left_is_const = is_constant(left) or str(left) in ('True', 'False')
                right_is_const = is_constant(right) or str(right) in ('True', 'False')

                if left_is_const and right_is_const:
                    l = int(str(left)) if is_constant(left) else (1 if str(left) == 'True' else 0)
                    r = int(str(right)) if is_constant(right) else (1 if str(right) == 'True' else 0)

                    if op == '+':
                        folded = str(l + r)
                    elif op == '-':
                        folded = str(l - r)
                    elif op == '*':
                        folded = str(l * r)
                    elif op == '/' and r != 0:
                        folded = str(l // r)
                    elif op == '%' and r != 0:
                        folded = str(l % r)
                    elif op == '==':
                        folded = 'True' if l == r else 'False'
                    elif op == '!=':
                        folded = 'True' if l != r else 'False'
                    elif op == '<':
                        folded = 'True' if l < r else 'False'
                    elif op == '>':
                        folded = 'True' if l > r else 'False'
                    elif op == '<=':
                        folded = 'True' if l <= r else 'False'
                    elif op == '>=':
                        folded = 'True' if l >= r else 'False'
                    elif op == 'and':
                        folded = 'True' if (bool(l) and bool(r)) else 'False'
                    elif op == 'or':
                        folded = 'True' if (bool(l) or bool(r)) else 'False'
                    elif op == '<<':
                        folded = str(l << r)
                    elif op == '>>':
                        folded = str(l >> r)

        if folded is not None:
            result.append(IRAssign(instr.dest, folded))
        else:
            result.append(instr)

    return result

def constant_propagation(ir_code):
    """
    Optimization: Replace variables with known constant values.

    Example:
        x := 5
        y := x + 3  -->  y := 5 + 3
    """
    constants = {}  # var -> constant value
    result = []

    for instr in ir_code:
        # some control flow may change values, hence it is easier to just clear here to avoid any extra headache in codegen
        if isinstance(instr, (IRLabel, IRJump, IRCondJump, IRBeginIf, IRElse, IREndIf, IRBeginWhile, IREndWhile, IRBeginFunc, IREndFunc, IRPushParam, IRFuncCall, IRPopParams)):
            constants.clear()
            result.append(instr)
            continue

        if isinstance(instr, IRAssign):
            dest = instr.dest
            val = instr.value

            # skipping list elements
            if isinstance(dest, str) and '[' in dest:
                if isinstance(val, str):
                    for var, c in constants.items():
                        val = re.sub(rf'\b{re.escape(var)}\b', str(c), val)
                result.append(IRAssign(dest, val))
                continue

            new_val = val
            if isinstance(val, str):
                for var, c in constants.items():
                    new_val = re.sub(rf'\b{re.escape(var)}\b', str(c), new_val)

            result.append(IRAssign(dest, new_val))

            if is_constant(new_val) or str(new_val) in ('True', 'False'):
                constants[dest] = new_val
            else:
                constants.pop(dest, None)

            continue

        result.append(instr)

    return result

def copy_propagation(ir_code):
    """
    Optimization: Replace variables assigned by copy with their source.

    Example:
        x := y
        z := x + 1  -->  z := y + 1
    """
    copies = {}  # var -> source var
    result = []

    for instr in ir_code:
        # some control flow may change values, hence it is easier to just clear here to avoid any extra headache in codegen
        if isinstance(instr, (IRLabel, IRJump, IRCondJump, IRBeginIf, IRElse, IREndIf, IRBeginWhile, IREndWhile, IRBeginFunc, IREndFunc, IRPushParam, IRFuncCall, IRPopParams)):
            copies.clear()
            result.append(instr)
            continue

        if isinstance(instr, IRAssign):
            dest = instr.dest
            val = instr.value

            if isinstance(dest, str) and '[' in dest:
                if isinstance(val, str):
                    for var, src in copies.items():
                        val = re.sub(rf'\b{re.escape(var)}\b', str(src), val)
                result.append(IRAssign(dest, val))
                continue

            new_val = val
            if isinstance(new_val, str):
                for var, src in copies.items():
                    new_val = re.sub(rf'\b{re.escape(var)}\b', str(src), new_val)

            result.append(IRAssign(dest, new_val))

            is_id = isinstance(new_val, str) and re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', new_val) is not None
            if isinstance(new_val, str) and is_id and new_val != 'ret' and not is_constant(new_val) and str(new_val) not in ('True', 'False'):
                copies[dest] = new_val
            else:
                copies.pop(dest, None)

            # Invalidate aliases that depended on overwritten destination.
            to_remove = [k for k, v in copies.items() if v == dest]
            for k in to_remove:
                del copies[k]

            continue

        result.append(instr)

    return result

def dead_code_elimination(ir_code, live_out=None):
    """
    Optimization: Remove assignments to variables that are never used.

    Example:
        x := 5
        y := 10   <- removed if y never used
        z := x
    """
    # NOTE: We decided to perform a less aggressive dead code elimination where we only remove unused temporary variables, and there were 2 main reasons why:
    # 1. it cleaned up the messy C code gen very we have a ton of intermediary temp variables, making it not easier to read
    # 2. as our languages do not have prints, dead code on variables would basically remove all of them and wouldn't help showcase examples, with just temporary variables, we can all the main variables from source, allowing us to easily verify correctness and also see the other optimizations in action.
    if live_out is None:
        live_out = set()

    # Find all used variables
    used = set(live_out)
    keywords = {'True', 'False', 'and', 'or', 'not', 'len', 'list_new'}
    for instr in ir_code:
        if isinstance(instr, IRAssign):
            dest = instr.dest
            val = instr.value
            if isinstance(dest, str) and '[' in dest:
                if isinstance(dest, str):
                    used_dest = set(re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', dest))
                    used.update(x for x in used_dest if x not in keywords)
                if isinstance(val, str):
                    used_val = set(re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', val))
                    used.update(x for x in used_val if x not in keywords)
                continue
            if isinstance(val, str):
                used_val = set(re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', val))
                used.update(x for x in used_val if x not in keywords)
            continue
        if isinstance(instr, IRCondJump):
            if isinstance(instr.condition, str):
                used_cond = set(re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', instr.condition))
                used.update(x for x in used_cond if x not in keywords)
        elif isinstance(instr, IRBeginIf):
            if isinstance(instr.cond, str):
                used_cond = set(re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', instr.cond))
                used.update(x for x in used_cond if x not in keywords)
        elif isinstance(instr, IRPushParam):
            if isinstance(instr.value, str):
                used_param = set(re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', instr.value))
                used.update(x for x in used_param if x not in keywords)

    # Keep only assignments to used variables (or non-assignments)
    result = []
    for instr in ir_code:
        if isinstance(instr, IRAssign):
            dest = instr.dest
            if isinstance(dest, str) and '[' in dest:
                result.append(instr)
                continue
            removable = is_temp(dest) and dest != 'ret'
            if removable and dest not in used:
                continue
        result.append(instr)

    return result

def common_subexpression_elimination(ir_code):
    """
    Optimization: Don't compute the same expression twice.

    Example:
        _t1 := a + b
        _t2 := a + b  -->  _t2 := _t1
    """
    expressions = {}  # "left op right" -> temp
    result = []

    for instr in ir_code:
        # some control flow may change values, hence it is easier to just clear here to avoid any extra headache in codegen
        if isinstance(instr, (IRLabel, IRJump, IRCondJump, IRBeginIf, IRElse, IREndIf, IRBeginWhile, IREndWhile, IRBeginFunc, IREndFunc, IRPushParam, IRFuncCall, IRPopParams)):
            expressions.clear()
            result.append(instr)
            continue

        if isinstance(instr, IRAssign) and isinstance(instr.value, str):
            parsed = parse_binop(instr.value)
            if parsed is not None:
                left, op, right = parsed
                expr_key = f'{left} {op} {right}'

                if expr_key in expressions:
                    # Reuse previous result
                    result.append(IRAssign(instr.dest, expressions[expr_key]))
                else:
                    # New expression
                    if is_temp(instr.dest):
                        expressions[expr_key] = instr.dest
                    result.append(instr)
            else:
                result.append(instr)
            # Invalidate expressions if a variable used by expression is reassigned.
            if isinstance(instr.dest, str):
                to_remove = [k for k, v in expressions.items() 
                            if instr.dest in k.split()]
                for k in to_remove:
                    del expressions[k]
            continue

        result.append(instr)

    return result

def strength_reduction(ir_code):
    """
    Optimization: Replace expensive operations with cheaper ones.
    
    Example:
        x * 2  -->  x << 1  (or x + x)
        x * 1  -->  x
        x + 0  -->  x
    """
    result = []

    for instr in ir_code:
        if isinstance(instr, IRAssign) and isinstance(instr.value, str):
            parsed = parse_binop(instr.value)
            if parsed is not None:
                left, op, right = parsed

                # Multiply by power of 2 -> shift
                if op == '*' and is_constant(right):
                    val = int(str(right))
                    if val == 0:
                        result.append(IRAssign(instr.dest, '0'))
                        continue
                    elif val == 1:
                        result.append(IRAssign(instr.dest, left))
                        continue
                    elif val == 2:
                        result.append(IRAssign(instr.dest, f'{left} << 1'))
                        continue
                    elif val == 4:
                        result.append(IRAssign(instr.dest, f'{left} << 2'))
                        continue
                    elif val == 8:
                        result.append(IRAssign(instr.dest, f'{left} << 3'))
                        continue
                    # we could technically go further, but for functionality and demo, this will suffice

                # Add/subtract 0 -> copy
                if op in ['+', '-'] and is_constant(right):
                    if int(str(right)) == 0:
                        result.append(IRAssign(instr.dest, left))
                        continue

        result.append(instr)

    return result

def TheComPylersIROptimizer(ir_code, iterations=3):
    """Apply all optimizations in sequence."""
    current = list(ir_code)
    
    for _ in range(iterations):
        prev = current

        # OPTIMIZATION ORDER MATTERS
        current = constant_propagation(current)
        current = constant_folding(current)
        current = copy_propagation(current)
        current = common_subexpression_elimination(current)
        current = strength_reduction(current)
        current = dead_code_elimination(current)

        if len(current) == len(prev) and all(str(a) == str(b) for a, b in zip(current, prev)):
            break

    return current
