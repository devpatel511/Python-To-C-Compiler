#!/usr/bin/env python3

class ParseError(Exception): pass

class SymbolTable(object):
    def __init__(self):
        self.scope_stack = [dict()]
        self.functions = dict()

    def push_scope(self):
        self.scope_stack.append(dict())

    def pop_scope(self):
        assert len(self.scope_stack) > 1
        self.scope_stack.pop()

    def declare_variable(self, name, type, line_number):
        """
        Add a new variable.
        Need to do duplicate variable declaration error checking.
        """
        if name in self.scope_stack[-1]:
            raise ParseError("Redeclaring variable named \"" + name + "\"", line_number)
        self.scope_stack[-1][name] = type

    def lookup_variable(self, name, line_number):
        """
        Return the type of the variable named 'name', or throw
        a ParseError if the variable is not declared in the scope.
        """
        # You should traverse through the entire scope stack
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        raise ParseError("Referencing undefined variable \"" + name + "\"", line_number)

    def declare_function(self, function_name, function_node, line_number):
        """
        Declare a new function in this program, checking for duplicates
        """
        if function_name in self.functions:
            raise ParseError("Redeclaring function named \"" + function_name + "\"", line_number)
        self.functions[function_name] = function_node

    def lookup_function(self, function_name, line_number):
        """
        Return the FunctionDef node associated with the function named 'function_name',
        or throw a ParseError if the function is not declared
        """
        function = self.functions.get(function_name)
        if function is None:
            raise ParseError("Referencing undefined function \"" + function_name + "\"", line_number)
        return function
