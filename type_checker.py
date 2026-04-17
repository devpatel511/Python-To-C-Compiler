#!/usr/bin/env python3

from symbol_table import SymbolTable, ParseError
import ast_comprehensive as ast

class TheComPylersTypeChecker(object):
    def __init__(self):
        # Since we don't store return statement in FunctionDef AST node, this will help us check if return statements are used within a function and if the returned expression matches the function's return type.
        self.current_return_type = None
        self.in_function = False

    def typecheck(self, node, st=None):
        method = 'check_' + node.__class__.__name__
        return getattr(self, method, self.generic_typecheck)(node, st)

    def generic_typecheck(self, node, st=None):
        if node is None:
            return ''
        else:
            parts = []
            for value in node.to_dict().values():
                if isinstance(value, ast.Node):
                    parts.append(self.typecheck(value, st))
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, ast.Node):
                            parts.append(self.typecheck(item, st))
            return ''.join(parts)

    def eq_type(self, t1, t2):
        """
        Helper function to check if two given type node is that of the
        same type. Precondition is that both t1 and t2 are that of class Type
        """
        if not isinstance(t1, ast.Type) or not isinstance(t2, ast.Type):
            raise ParseError("eq_type invoked on non-type objects")
        return t1.name == t2.name

    def require_type(self, actual_type, expected_name, lineno, context):
        """
        Helper function to validate an expected type with an actual type (provides better debug messages than eq_type())
        """
        expected_type = ast.Type(expected_name, lineno)
        if not self.eq_type(actual_type, expected_type):
            raise ParseError("{} requires type '{}', got '{}'".format(context, expected_type.name, actual_type.name), lineno)

    def check_Program(self, node, st=None):
        """
        Generate global symbol table. Recursively typecheck its classes and
        add its class symbol table to itself.
        """
        # Generate global symbol table
        global_st = SymbolTable()

        for item in node.items:
            self.typecheck(item, global_st)

        return global_st

    def check_FunctionDef(self, node, st):

        # Make sure there are no duplicate parameter names
        names = set()
        for param in node.params:
            if param.name in names:
                raise ParseError("Duplicate parameter named '{}' in function '{}'".format(param.name, node.name), param.lineno)
            names.add(param.name)

        # We declare here to allow recursive function calls.
        st.declare_function(node.name, node, node.lineno)

        st.push_scope()

        # Go through the parameters
        for param in node.params:
            self.typecheck(param, st)

        # Since we don't store return statement in FunctionDef AST node, we address the issue with class attributes being pushed/popped off stack/scope.
        prev_return_type = self.current_return_type
        prev_in_function = self.in_function

        self.current_return_type = node.return_type
        self.in_function = True

        for stmt in node.body:
            self.typecheck(stmt, st)

        self.current_return_type = prev_return_type
        self.in_function = prev_in_function

        st.pop_scope()

        return None

    def check_AssignStmt(self, node, st):
        try:
            var_type = st.lookup_variable(node.name, node.lineno)
        except ParseError:
            var_type = None

        expr_type = self.typecheck(node.expr, st)

        if var_type is None: # When variable is being declared for the first time
            st.declare_variable(node.name, expr_type, node.lineno)
            return expr_type

        if not self.eq_type(var_type, expr_type):
            raise ParseError("Variable \"" + node.name + "\" has the type",
                             var_type.name, "but is being assigned the type",
                             expr_type.name, node.lineno)

        return expr_type

    def check_IfStmt(self, node, st):
        """
        Check if the condition expression is a boolean type, then
        recursively typecheck all of if statement body.
        """

        cond_type = self.typecheck(node.condition, st)
        self.require_type(cond_type, 'bool', node.lineno, "if condition")

        # Did not use push_scope() and pop_scope() here as we need to allow things like in examples/lang/test_nested_blocks.py
        for stmt in node.true_body:
            self.typecheck(stmt, st)
        if node.false_body is not None:
            for stmt in node.false_body:
                self.typecheck(stmt, st)

        return None

    def check_WhileStmt(self, node, st):
        """
        Check if the condition expression is a boolean type, then
        recursively typecheck all of while statement body.
        """
        cond_type = self.typecheck(node.condition, st)
        self.require_type(cond_type, 'bool', node.lineno, "while condition")

        # Did not use push_scope() and pop_scope() here as we need to allow things like in examples/lang/test_nested_blocks.py
        for stmt in node.body:
            self.typecheck(stmt, st)

        return None

    def check_ReturnStmt(self, node, st):
        """
        Makes sure the return statement is used within a function and the returned expression matches the function's return type.
        """
        if not self.in_function or self.current_return_type is None:
            raise ParseError("Return statement used outside of function", node.lineno)

        expr_type = self.typecheck(node.expr, st)
        if not self.eq_type(expr_type, self.current_return_type):
            raise ParseError("Function return type is '{}' but return expression is '{}'".format(self.current_return_type.name, expr_type.name), node.lineno)

        return expr_type

    def check_BinOp(self, node, st):
        """
        NOTE
        Also checks if the type of the left and right operation
        makes sense in the context of the operator (ie., you should not be
        able to add/subtract/multiply/divide strings or booleans).
        """

        left_type = self.typecheck(node.left, st)
        right_type = self.typecheck(node.right, st)

        arith_ops = ['+', '-', '*', '/', '%']
        comp_ops = ['<', '<=', '>', '>=']
        eq_ops = ['==', '!=']
        bool_ops = ['and', 'or']
        if node.op in arith_ops:
            self.require_type(left_type, 'int', node.lineno, "arithmetic")
            self.require_type(right_type, 'int', node.lineno, "arithmetic")
            return ast.Type('int', node.lineno)
        elif node.op in comp_ops:
            self.require_type(left_type, 'int', node.lineno, "comparison")
            self.require_type(right_type, 'int', node.lineno, "comparison")
            return ast.Type('bool', node.lineno)
        elif node.op in eq_ops:
            if not self.eq_type(left_type, right_type):
                raise ParseError("Left and right expressions for equality comparison are of different type", node.lineno)
            return ast.Type('bool', node.lineno)
        elif node.op in bool_ops:
            self.require_type(left_type, 'bool', node.lineno, "boolean operation")
            self.require_type(right_type, 'bool', node.lineno, "boolean operation")
            return ast.Type('bool', node.lineno)
        raise ParseError("Unsupported binary operator '{}'".format(node.op), node.lineno)

    def check_UnaryOp(self, node, st):
        """
        Similar to check_BinOp, also checks if the type of the operand makes sense in the context of the operator (ie., you should not be able to apply unary minus to booleans and "not" to ints).
        """

        operand_type = self.typecheck(node.operand, st)
        if node.op == '-':
            self.require_type(operand_type, 'int', node.lineno, "unary minus")
            return ast.Type('int', node.lineno)
        elif node.op == 'not':
            self.require_type(operand_type, 'bool', node.lineno, "not")
            return ast.Type('bool', node.lineno)
        raise ParseError("Unsupported unary operator '{}'".format(node.op), node.lineno)

    def check_Constant(self, node, st):
        """
        Returns the type of the constant.
        """
        return ast.Type(node.value_type, node.lineno)

    def check_Identifier(self, node, st):
        """
        Refers to some kind of id, then we need to find if the id has been declared.
        """
        return st.lookup_variable(node.name, node.lineno)

    def check_FunctionCall(self, node, st):
        function = st.lookup_function(node.name, node.lineno)

        if len(function.params) != len(node.args):
            raise ParseError("Argument length mismatch with function", node.lineno)

        for i, arg in enumerate(node.args):
            arg_type = self.typecheck(arg, st)
            if not self.eq_type(arg_type, function.params[i].type_node):
                raise ParseError("Argument type mismatch with function parameter", node.lineno)

        return function.return_type

    def check_ListLiteral(self, node, st):
        """
        Make sure all elements in list are of type int.
        """
        for elem in node.elements:
            elem_type = self.typecheck(elem, st)
            self.require_type(elem_type, 'int', node.lineno, "list literal element")
        return ast.Type('list[int]', node.lineno)

    def check_ListIndex(self, node, st):
        """
        Make sure identifier of object is of type list[int], and index is of type int.
        """
        list_type = st.lookup_variable(node.name, node.lineno)
        self.require_type(list_type, 'list[int]', node.lineno, "list indexing")

        index_type = self.typecheck(node.index, st)
        self.require_type(index_type, 'int', node.lineno, "list index")

        return ast.Type('int', node.lineno)

    def check_LenExpr(self, node, st):
        """
        Make sure expression is of type list[int].
        """
        expr_type = self.typecheck(node.expr, st)
        self.require_type(expr_type, 'list[int]', node.lineno, "len()")
        return ast.Type('int', node.lineno)

    def check_Comment(self, node, st):
        return None

    def check_Param(self, node, st):
        """
        Add all of the parameters to the symbol table
        """
        self.typecheck(node.type_node, st)
        st.declare_variable(node.name, node.type_node, node.lineno)
        return node.type_node

    def check_Type(self, node, st):
        return node
