#!/usr/bin/env python3

import re

from ir_gen import IRAssign, IRBeginFunc, IRComment, IRCondJump, IREndFunc
from ir_gen import IRFuncCall, IRJump, IRLabel, IRPopParams, IRPushParam
from ir_gen import IRBeginWhile, IREndWhile, IRBeginIf, IREndIf, IRElse


def _ir_bool_literals_to_c(s: str) -> str:
    """IR uses Python True/False; C needs true/false (including inside compound exprs)."""
    s = re.sub(r"\bTrue\b", "true", s)
    return re.sub(r"\bFalse\b", "false", s)


class TheComPylersCCodeGenerator(object):
    """
    Generates C code from Three-Address Code IR.
    """

    def __init__(self):
        self.output = []
        self.indent_level = 0
        self.global_st = None
        self.param_stack = []
        self.last_call = ""
        self.variables = {}
        self.lists_used = False
        self.bools_used = False

        # for generation (each IR instruction)
        self.in_while = []
        self.current_types = {}
        self.declared_vars = set()

    def emit(self, line):
        """Add a line to the output."""
        if line == "":
            self.output.append("")
        else:
            self.output.append(("    " * self.indent_level) + line)

    def generate(self, ir_obj, global_st):
        """Generate C code from IR code."""

        self.global_st = global_st
        
        # checking if lists/bools are used anywhere so that we know to include or not to include.
        self.lists_used = any(isinstance(i, IRAssign) and ('list_new' in str(i.value) or 'len(' in str(i.value) or '[' in str(i.dest) or '[' in str(i.value)) for i in ir_obj)
        self.bools_used = any(isinstance(i, IRCondJump) for i in ir_obj) or any(isinstance(i, IRAssign) and (str(i.value) in ('True', 'False') or any(op in str(i.value) for op in [' == ', ' != ', ' <= ', ' >= ', ' < ', ' > ', ' and ', ' or ', 'not '])) for i in ir_obj)
        
        if global_st:
            for f in global_st.functions.values():
                if f.return_type.name == 'bool': self.bools_used = True
                for p in f.params:
                    if p.type_node.name == 'bool': self.bools_used = True
        
        functions = []
        main_ir = []
        
        i = 0
        # seperating main function in C (i.e. Python outer most code) to actual functions defined in source code
        while i < len(ir_obj):
            instr = ir_obj[i]
            
            if isinstance(instr, IRBeginFunc):
                func_label = main_ir.pop()
                name = func_label.name.replace("_L", "") if hasattr(func_label, 'name') else ""
                
                if len(main_ir) > 0 and isinstance(main_ir[-1], IRJump):
                    main_ir.pop()
                    
                # to maintain comment location from source code examples
                func_comments = []
                while len(main_ir) > 0 and isinstance(main_ir[-1], IRComment):
                    func_comments.insert(0, main_ir.pop())
                    
                i += 1
                func_body = []
                while i < len(ir_obj) and not isinstance(ir_obj[i], IREndFunc):
                    func_body.append(ir_obj[i])
                    i += 1
                    
                functions.append((name, func_comments, func_body))
            else:
                main_ir.append(instr)
            i += 1
                    
        self.emit_headers()
        
        for name, comments, fn_ir in functions:
            for c in comments:
                if not getattr(c, "hidden", False):
                    self.emit(f"// {c.text}")
            self.gen_function(name, fn_ir)
            
        self.gen_main(main_ir)

        return "\n".join(self.output)

    def emit_headers(self):
        """When using bool or list, we need to include some C headers and boilerplate structs to make our lives easier."""

        if self.bools_used:
            self.emit("#include <stdbool.h>")
        if self.lists_used:
            self.emit("#include <stdlib.h>")
            
        if self.bools_used or self.lists_used:
            self.emit("")
            
        if self.lists_used:
            self.emit("typedef struct {")
            self.emit("    int* data;")
            self.emit("    int length;")
            self.emit("} IntList;")
            self.emit("")
            self.emit("IntList* list_new(int len) {")
            self.indent_level += 1
            self.emit("IntList* list = (IntList*)malloc(sizeof(IntList));")
            self.emit("list->length = len;")
            self.emit("if (len > 0) {")
            self.indent_level += 1
            self.emit("list->data = (int*)malloc((size_t)len * sizeof(int));")
            self.indent_level -= 1
            self.emit("} else {")
            self.indent_level += 1
            self.emit("list->data = NULL;")
            self.indent_level -= 1
            self.emit("}")
            self.emit("return list;")
            self.indent_level -= 1
            self.emit("}")
            self.emit("")
            self.emit("void int_list_free(IntList* list) {")
            self.indent_level += 1
            self.emit("if (list != NULL) {")
            self.indent_level += 1
            self.emit("free(list->data);")
            self.emit("free(list);")
            self.indent_level -= 1
            self.emit("}")
            self.indent_level -= 1
            self.emit("}")
            self.emit("")

    def infer_types(self, ir_block, initial_env=None):
        """Our IR doesn't contain type info, hence we need to infer it here."""

        if initial_env is None:
            initial_env = {}
        env = dict(initial_env)
        for instr in ir_block:
            if isinstance(instr, IRAssign):
                dest = instr.dest
                val = str(instr.value)
                
                if '[' in dest: continue
                if dest == 'ret': continue
                
                if 'list_new' in val:
                    env[dest] = 'IntList*'
                elif any(op in val for op in [' == ', ' != ', ' <= ', ' >= ', ' < ', ' > ', ' and ', ' or ', 'not ']):
                    env[dest] = 'bool'
                elif 'len(' in val:
                    env[dest] = 'int'
                elif val == 'True' or val == 'False':
                    env[dest] = 'bool'
                elif val == 'ret':
                    env[dest] = 'int'
                elif val.isdigit() or (val.startswith('-') and val[1:].isdigit()):
                    env[dest] = 'int'
                elif any(op in val for op in ['+', '-', '*', '/']):
                    env[dest] = 'int'
                elif '[' in val:
                    env[dest] = 'int'
                elif val in env:
                    env[dest] = env[val]
                else:
                    env[dest] = 'int'
        return env

    def get_predeclarations(self, ir_block, initial_env):
        """This allows us declare and assign variables on same line rather than declaring all at once on the top (mainly addded this for code readability)"""

        first_assign_depth = {}
        depth = 0
        for instr in ir_block:
            if isinstance(instr, (IRBeginWhile, IRBeginIf)):
                depth += 1
            elif isinstance(instr, (IREndWhile, IREndIf)):
                depth -= 1
            elif isinstance(instr, IRAssign):
                dest = instr.dest.split('[')[0] if '[' in instr.dest else instr.dest
                val = str(instr.value)
                # ensure we don't inline assignment if the variable is USED before it's assigned 
                # (However, I don't think this should happen in our strict block assignments, but just in case):
                if dest not in initial_env and dest not in first_assign_depth and dest != 'ret':
                    first_assign_depth[dest] = depth
        return first_assign_depth
    
    def get_ctype(self, ast_type_name):
        """Helper function for the below method (kept the code a little more organized a t least)."""

        if ast_type_name == 'int': return 'int'
        if ast_type_name == 'bool': return 'bool'
        if ast_type_name == 'list[int]': return 'IntList*'
        return 'int'

    def gen_function(self, name, ir_block):
        """Generate: non-main function."""

        func_node = self.global_st.functions.get(name) if self.global_st else None
        ret_type = self.get_ctype(func_node.return_type.name) if func_node else 'int'
        
        params_str = ""
        initial_types = {}
        if func_node:
            p_strs = []
            for p in func_node.params:
                pt = self.get_ctype(p.type_node.name)
                initial_types[p.name] = pt
                p_strs.append(f"{pt} {p.name}")
            params_str = ", ".join(p_strs)
            
        self.emit(f"{ret_type} {name}({params_str}) {{")
        self.indent_level += 1
        
        self.current_types = self.infer_types(ir_block, initial_types)
        first_assign_depth = self.get_predeclarations(ir_block, initial_types)
        self.declared_vars = set(initial_types.keys())
        
        for var, t in self.current_types.items():
            if var not in self.declared_vars:
                if first_assign_depth.get(var, 0) > 0 or var not in first_assign_depth:
                    self.emit(f"{t} {var};")
                    self.declared_vars.add(var)
                
        for instr in ir_block:
            self.gen_instruction(instr)
            
        self.indent_level -= 1
        self.emit("}")
        self.emit("")

    def gen_main(self, ir_block):
        """Generate: main function."""

        self.emit("int main(void) {")
        self.indent_level += 1
        
        self.current_types = self.infer_types(ir_block)
        first_assign_depth = self.get_predeclarations(ir_block, {})
        self.declared_vars = set()
        
        for var, t in self.current_types.items():
            if first_assign_depth.get(var, 0) > 0 or var not in first_assign_depth:
                self.emit(f"{t} {var};")
                self.declared_vars.add(var)
            
        for instr in ir_block:
            self.gen_instruction(instr)
        
        if self.lists_used:
            to_free = []
            for instr in ir_block:
                if isinstance(instr, IRAssign) and 'list_new' in str(instr.value) and '[' not in instr.dest:
                    to_free.append(instr.dest)
            for var in to_free:
                self.emit(f"int_list_free({var});")
        
        self.emit("return 0;")
        self.indent_level -= 1
        self.emit("}")

    def gen_instruction(self, instr):
        """Generate code for a single IR instruction."""
        if isinstance(instr, IRComment): 
            self.gen_comment(instr)
        elif isinstance(instr, IRAssign): 
            self.gen_assign(instr)
        elif isinstance(instr, IRPushParam): 
            self.gen_push_param(instr)
        elif isinstance(instr, IRFuncCall): 
            self.gen_func_call(instr)
        elif isinstance(instr, IRPopParams): 
            self.gen_pop_params(instr)
        elif isinstance(instr, IRBeginWhile): 
            self.gen_begin_while(instr)
        elif isinstance(instr, IREndWhile): 
            self.gen_end_while(instr)
        elif isinstance(instr, IRBeginIf): 
            self.gen_begin_if(instr)
        elif isinstance(instr, IRElse): 
            self.gen_else(instr)
        elif isinstance(instr, IREndIf): 
            self.gen_end_if(instr)
        elif isinstance(instr, IRCondJump): 
            self.gen_cond_jump(instr)

    def gen_comment(self, instr):
        """Generate: // comment"""
        if not getattr(instr, "hidden", False):
            self.emit(f"// {instr.text}")

    def gen_assign(self, instr):
        """Generate: dest := value"""
        if instr.dest == 'ret':
            self.emit(f"return {instr.value};")
            return

        dest, val = instr.dest, str(instr.value)
        
        # Found it easiest just to manually replace
        if 'list_new' in val:
            val = f"list_new({val.replace('list_new', '').strip()})"
        elif 'len(' in val: val = f"{val[4:-1]}->length"
        elif val == 'True': val = 'true'
        elif val == 'False': val = 'false'
        
        if ' and ' in val: val = val.replace(' and ', ' && ')
        if ' or ' in val: val = val.replace(' or ', ' || ')
        if val.startswith('not '): val = f"!({val[4:]})"
        val = _ir_bool_literals_to_c(val)
        
        if '[' in val and dest != 'ret':
            head, tail = val.split('[', 1)
            if 'list_new' not in head: val = f"{head}->data[{tail}"
                
        if '[' in dest:
            head, tail = dest.split('[', 1)
            dest = f"{head}->data[{tail}"
            
        if val == 'ret': val = self.last_call
            
        var_base = dest.split('[')[0] if '[' in dest else dest
        if var_base in self.current_types and var_base not in self.declared_vars and var_base != 'ret' and '[' not in dest:
            self.emit(f"{self.current_types[var_base]} {dest} = {val};")
            self.declared_vars.add(var_base)
        else:
            self.emit(f"{dest} = {val};")

    def gen_push_param(self, instr):
        """Generate: push_param value"""
        self.param_stack.append(str(instr.value))

    def gen_func_call(self, instr):
        """Generate function call."""
        args = self.param_stack[-instr.count:] if hasattr(instr, 'count') else self.param_stack
        self.param_stack = self.param_stack[:-instr.count] if hasattr(instr, 'count') else []
        self.last_call = f"{instr.name}({', '.join(args)})"

    def gen_pop_params(self, instr):
        pass
        
    def gen_begin_while(self, instr):
        """Generate: while loop."""
        self.emit("while (1) {")
        self.indent_level += 1
        self.in_while.append(instr.end_label)
        
    def gen_end_while(self, instr):
        """Generate: end of while loop."""
        self.indent_level -= 1
        self.emit("}")
        self.in_while.pop()

    def gen_begin_if(self, instr):
        """Generate: if statement."""
        cond_val = str(instr.cond)
        if cond_val.startswith("not "): cond_val = f"!({cond_val[4:]})"
        cond_val = _ir_bool_literals_to_c(cond_val)
        self.emit(f"if ({cond_val}) {{")
        self.indent_level += 1

    def gen_else(self, instr):
        """Generate: else statement."""
        self.indent_level -= 1
        self.emit("} else {")
        self.indent_level += 1

    def gen_end_if(self, instr):
        """Generate: end of if statement."""
        self.indent_level -= 1
        self.emit("}")

    def gen_cond_jump(self, instr):
        """Generate: conditional jump."""
        if len(self.in_while) > 0 and instr.label == self.in_while[-1]:
            cond = f"!({instr.condition})" if instr.negated else str(instr.condition)
            cond = _ir_bool_literals_to_c(cond)
            self.emit(f"if ({cond}) {{")
            self.indent_level += 1
            self.emit("break;")
            self.indent_level -= 1
            self.emit("}")
            