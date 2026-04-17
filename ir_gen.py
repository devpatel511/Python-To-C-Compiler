#!/usr/bin/env python3

class IRInstruction:
    """Base class for IR instructions."""
    pass

class IRComment(IRInstruction):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return f"    # {self.text}"

class IRAssign(IRInstruction):
    """Assignment: dest := value"""
    def __init__(self, dest, value):
        self.dest = dest
        self.value = value
    
    def __str__(self):
        return f"    {self.dest} := {self.value}"

class IRLabel(IRInstruction):
    """Label marker"""
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"{self.name}:"

class IRJump(IRInstruction):
    """Unconditional jump: goto label"""
    def __init__(self, label):
        self.label = label

    def __str__(self):
        return f"    goto {self.label}"

class IRCondJump(IRInstruction):
    """Conditional jump: if condition goto label (negated if specified)"""
    def __init__(self, condition, label, negated=True):
        self.condition = condition
        self.label = label
        self.negated = negated

    def __str__(self):
        if self.negated:
            return f"    if !({self.condition}) goto {self.label}"
        return f"    if ({self.condition}) goto {self.label}"

class IRPushParam(IRInstruction):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"    PushParam {self.value}"

class IRFuncCall(IRInstruction):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"    FuncCall {self.name}"

class IRPopParams(IRInstruction):
    def __init__(self, count):
        self.count = count

    def __str__(self):
        return f"    PopParams {self.count}"

class IRBeginFunc(IRInstruction):
    def __str__(self):
        return "    BeginFunc"

class IREndFunc(IRInstruction):
    def __str__(self):
        return "    EndFunc"

class IRBeginWhile(IRInstruction):
    def __init__(self, start_label, end_label):
        self.start_label = start_label
        self.end_label = end_label
    def __str__(self):
        return ""

class IREndWhile(IRInstruction):
    def __str__(self):
        return ""

class IRBeginIf(IRInstruction):
    def __init__(self, cond, fbranch_label, tbranch_label):
        self.cond = cond
        self.fbranch_label = fbranch_label
        self.tbranch_label = tbranch_label
    def __str__(self):
        return ""

class IRElse(IRInstruction):
    def __str__(self):
        return ""

class IREndIf(IRInstruction):
    def __str__(self):
        return ""

class TheComPylersIRGen(object):
    """
    Uses the same visitor pattern as AST JSON output. It is modified to
    generate 3AC (Three Address Code) in a simple string.
    """

    def __init__(self):
        """
        IR_lst: list of IR code as strings (kept for printing compatibility)
        IR_obj: list of typed IR instructions (for codegen/optimization passes)
        register_count: integer to keep track of which register to use
        label_count: similar to register_count, but with labels
        """
        self.IR_lst = []
        self.IR_obj = []
        self.register_count = 0
        self.label_count = 0

    def generate(self, node):
        """
        Similar to 'typecheck' method from TypeChecker object
        """
        method = 'gen_' + node.__class__.__name__
        return getattr(self, method)(node)

    ################################
    ## Helper functions
    ################################

    def emit_inst(self, inst):
        self.IR_obj.append(inst)
        self.IR_lst.append(str(inst))

    def add_code(self, code):
        """
        Add raw text code (we kept it for backwards compatibility)
        """
        self.IR_lst.append("    " + code)

    def inc_register(self):
        """
        Increase the register count and return its value for use
        """
        self.register_count += 1
        return self.register_count

    def reset_register(self):
        """
        Can reset the register_count to reuse them

        NOTE: We basically deprecated this as we are now going with SSA to enable easier temp variable naming in final C code gen.
        """
        self.register_count = 0

    def inc_label(self):
        """
        Increase the label count and return its value for use
        """
        self.label_count += 1
        return self.label_count

    def to_label_name(self, label):
        label_str = str(label)
        if label_str.startswith('_L'):
            return label_str
        return "_L{}".format(label_str)

    def mark_label(self, label):
        """
        Add label mark to IR_lst/IR_obj
        """
        self.emit_inst(IRLabel(self.to_label_name(label)))

    def print_ir(self):
        """
        Loop through the generated IR code and print them out to stdout
        """
        for ir in self.IR_lst:
            if str(ir) != "":
                print(ir)

    def gen_Comment(self, node):
        """
        Adding comments into the IR so that it can be preserved through to the final C output in Sprint 3/4
        """
        self.emit_inst(IRComment(node.text))

    ################################
    ## Program and Statements
    ################################

    def gen_Program(self, node):
        for item in node.items:
            self.generate(item)

    def gen_AssignStmt(self, node):
        expr = self.generate(node.expr)
        self.emit_inst(IRAssign(node.name, expr))

    def gen_IfStmt(self, node):
        cond = self.generate(node.condition)

        fbranch_label = self.inc_label()
        tbranch_label = self.inc_label()

        # To help with C code gen
        self.emit_inst(IRBeginIf(cond, self.to_label_name(fbranch_label), self.to_label_name(tbranch_label)))

        # Skip to the false_body if the condition is not met
        self.emit_inst(IRCondJump(cond, self.to_label_name(fbranch_label), True))

        for stmt in node.true_body:
            self.generate(stmt)
        # Make sure the statements from false_body is skipped
        self.emit_inst(IRJump(self.to_label_name(tbranch_label)))

        self.mark_label(fbranch_label)
        if node.false_body is not None:
            self.emit_inst(IRElse()) # To help with C code gen
            for stmt in node.false_body:
                self.generate(stmt)
        self.mark_label(tbranch_label)
        self.emit_inst(IREndIf()) # To help with C code gen

    def gen_WhileStmt(self, node):
        start_label = self.inc_label()
        end_label = self.inc_label()

        # To help with C code gen
        self.emit_inst(IRBeginWhile(self.to_label_name(start_label), self.to_label_name(end_label)))

        self.mark_label(start_label)

        cond = self.generate(node.condition)
        self.emit_inst(IRCondJump(cond, self.to_label_name(end_label), True))

        for stmt in node.body:
            self.generate(stmt)

        self.emit_inst(IRJump(self.to_label_name(start_label)))
        self.mark_label(end_label)
        self.emit_inst(IREndWhile()) # To help with C code gen

    def gen_ReturnStmt(self, node):
        expr = self.generate(node.expr)
        self.emit_inst(IRAssign("ret", expr))

    ################################
    ## Function Declarations and Calls
    ################################

    def gen_FunctionDef(self, node):

        skip_decl = self.inc_label()

        # We want to skip the function code until it is called
        self.emit_inst(IRJump(self.to_label_name(skip_decl)))

        # Function label
        self.mark_label(node.name)

        # Allocate room for function local variables
        self.emit_inst(IRBeginFunc())

        # Actually generate the main body
        for stmt in node.body:
            self.generate(stmt)

        # Do any cleanup before jumping back
        self.emit_inst(IREndFunc())

        self.mark_label(skip_decl)

    def gen_FunctionCall(self, node):

        # Push all of the arguments with "PushParam" function
        for arg in node.args:
            self.emit_inst(IRPushParam(self.generate(arg)))

        # Once all of the parameter has been pushed, actually call the function
        self.emit_inst(IRFuncCall(node.name))

        # After we're done with the function, remove the spaces reserved for the arguments
        self.emit_inst(IRPopParams(len(node.args)))

        reg = self.inc_register()
        temp = '_t%d' % reg
        self.emit_inst(IRAssign(temp, "ret"))

        return temp

    ################################
    ## Expressions
    ################################

    def gen_BinOp(self, node):
        # Left operand
        left = self.generate(node.left)
        # Right operand
        right = self.generate(node.right)

        reg = self.inc_register()
        temp = '_t%d' % reg
        self.emit_inst(IRAssign(temp, "{} {} {}".format(left, node.op, right)))

        return temp

    def gen_UnaryOp(self, node):
        operand = self.generate(node.operand)

        reg = self.inc_register()
        temp = '_t%d' % reg
        self.emit_inst(IRAssign(temp, "{} {}".format(node.op, operand)))

        return temp

    def gen_Constant(self, node):
        return node.value

    def gen_Identifier(self, node):
        return node.name

    ################################
    ## List Operations
    ################################

    def gen_ListLiteral(self, node):
        """
        Generate IR for list literal creation.
        e.g. [1, 2, 3] becomes:
            _t1 := list_new 3
            _t1[0] := 1
            _t1[1] := 2
            _t1[2] := 3
        Empty list [] becomes:
            _t1 := list_new 0
        """
        reg = self.inc_register()
        temp = '_t%d' % reg

        self.emit_inst(IRAssign(temp, "list_new {}".format(len(node.elements))))

        for i, elem in enumerate(node.elements):
            val = self.generate(elem)
            self.emit_inst(IRAssign("{}[{}]".format(temp, i), val))

        return temp

    def gen_ListIndex(self, node):
        """
        Generate IR for list indexing.
        e.g. x[idx] becomes:
            _t1 := <index_expr>
            _t2 := name[_t1]
        """
        index = self.generate(node.index)

        reg = self.inc_register()
        temp = '_t%d' % reg
        self.emit_inst(IRAssign(temp, "{}[{}]".format(node.name, index)))

        return temp

    def gen_LenExpr(self, node):
        """
        Generate IR for len() built-in.
        e.g. len(x) becomes:
            _t1 := len(x)
        """
        expr = self.generate(node.expr)

        reg = self.inc_register()
        temp = '_t%d' % reg
        self.emit_inst(IRAssign(temp, "len({})".format(expr)))

        return temp
