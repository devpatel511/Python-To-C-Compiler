#!/usr/bin/env python3
"""
NOTE: Grammer spec @ specs/context_free_grammar.txt
"""

import argparse
import json
import ply.yacc as yacc

from scanner import TheComPylersLexer, preprocess_indentation, tokens
from ast_comprehensive import Program, FunctionDef, Param, Type, Comment
from ast_comprehensive import AssignStmt, IfStmt, WhileStmt, ReturnStmt
from ast_comprehensive import BinOp, UnaryOp, Constant, Identifier
from ast_comprehensive import FunctionCall, ListLiteral, ListIndex, LenExpr


class TheComPylersParser:

    # Highest level: program

    def p_program(self, p):
        '''program : item_list'''
        p[0] = Program(p[1])

    def p_program_EPSILON(self, p):
        '''program : EPSILON'''
        p[0] = Program([])

    def p_item_list_multi(self, p):
        '''item_list : item_list item'''
        p[0] = p[1] + [p[2]] if p[2] is not None else p[1]

    def p_item_list_single(self, p):
        '''item_list : item'''
        p[0] = [p[1]] if p[1] is not None else []

    def p_item_func(self, p):
        '''item : function_def'''
        p[0] = p[1]

    def p_item_stmt(self, p):
        '''item : statement'''
        p[0] = p[1]

    # Function definition, parameters and types

    def p_function_def(self, p):
        '''function_def : DEF ID LPAREN param_list RPAREN ARROW type COLON NEWLINE INDENT statement_list DEDENT'''
        p[0] = FunctionDef(p[2], p[4], p[7], p[11], p.lineno(1))

    def p_param_list_params(self, p):
        '''param_list : params'''
        p[0] = p[1]

    def p_param_list_EPSILON(self, p):
        '''param_list : EPSILON'''
        p[0] = []

    def p_params_multi(self, p):
        '''params : params COMMA param'''
        p[0] = p[1] + [p[3]]

    def p_params_single(self, p):
        '''params : param'''
        p[0] = [p[1]]

    def p_param(self, p):
        '''param : ID COLON type'''
        p[0] = Param(p[1], p[3], p.lineno(1))

    def p_type_int(self, p):
        '''type : INT_TYPE'''
        p[0] = Type('int', p.lineno(1))

    def p_type_bool(self, p):
        '''type : BOOL_TYPE'''
        p[0] = Type('bool', p.lineno(1))

    def p_type_list(self, p):
        '''type : LIST_TYPE LBRACK INT_TYPE RBRACK'''
        p[0] = Type('list[int]', p.lineno(1))

    # Higher level statements

    def p_statement_list_multi(self, p):
        '''statement_list : statement_list statement'''
        p[0] = p[1] + [p[2]] if p[2] is not None else p[1]

    def p_statement_list_single(self, p):
        '''statement_list : statement'''
        p[0] = [p[1]] if p[1] is not None else []

    def p_statement_simple(self, p):
        '''statement : simple_statement NEWLINE'''
        p[0] = p[1]

    def p_statement_compound(self, p):
        '''statement : compound_statement'''
        p[0] = p[1]

    def p_statement_newline(self, p):
        '''statement : NEWLINE'''
        p[0] = None
    
    def p_statement_comment(self, p):
        '''statement : COMMENT NEWLINE'''
        p[0] = Comment(p[1], p.lineno(1))

    def p_simple_statement_assign(self, p):
        '''simple_statement : assignment_statement'''
        p[0] = p[1]

    def p_simple_statement_return(self, p):
        '''simple_statement : return_statement'''
        p[0] = p[1]

    def p_compound_statement_if(self, p):
        '''compound_statement : if_statement'''
        p[0] = p[1]

    def p_compound_statement_while(self, p):
        '''compound_statement : while_statement'''
        p[0] = p[1]

    # Precise statements

    def p_assignment_statement(self, p):
        '''assignment_statement : ID EQ expression'''
        p[0] = AssignStmt(p[1], p[3], p.lineno(1))

    def p_if_statement(self, p):
        '''if_statement : IF expression COLON NEWLINE INDENT statement_list DEDENT'''
        p[0] = IfStmt(p[2], p[6], None, p.lineno(1))

    def p_if_else_statement(self, p):
        '''if_statement : IF expression COLON NEWLINE INDENT statement_list DEDENT ELSE COLON NEWLINE INDENT statement_list DEDENT'''
        p[0] = IfStmt(p[2], p[6], p[12], p.lineno(1))

    def p_while_statement(self, p):
        '''while_statement : WHILE expression COLON NEWLINE INDENT statement_list DEDENT'''
        p[0] = WhileStmt(p[2], p[6], p.lineno(1))

    def p_return_statement(self, p):
        '''return_statement : RETURN expression'''
        p[0] = ReturnStmt(p[2], p.lineno(1))

    # Expressions (NOTE: PLY parser/YACC gives precedence lowest to highest, and hence how we have structured them)

    def p_expression(self, p):
        '''expression : or_expression'''
        p[0] = p[1]

    def p_or_expression_binop(self, p):
        '''or_expression : or_expression OR and_expression'''
        p[0] = BinOp('or', p[1], p[3], p.lineno(2))

    def p_or_expression(self, p):
        '''or_expression : and_expression'''
        p[0] = p[1]

    def p_and_expression_binop(self, p):
        '''and_expression : and_expression AND not_expression'''
        p[0] = BinOp('and', p[1], p[3], p.lineno(2))

    def p_and_expression(self, p):
        '''and_expression : not_expression'''
        p[0] = p[1]

    def p_not_expression_unary(self, p):
        '''not_expression : NOT not_expression'''
        p[0] = UnaryOp('not', p[2], p.lineno(1))

    def p_not_expression(self, p):
        '''not_expression : comparison'''
        p[0] = p[1]

    def p_comparison_binop(self, p):
        '''comparison : comparison LESSEQ arith_expression
                      | comparison LESS arith_expression
                      | comparison GREATER arith_expression
                      | comparison GREATEREQ arith_expression
                      | comparison EQOP arith_expression
                      | comparison NEQ arith_expression'''
        p[0] = BinOp(p[2], p[1], p[3], p.lineno(2))

    def p_comparison(self, p):
        '''comparison : arith_expression'''
        p[0] = p[1]

    def p_arith_expression_binop(self, p):
        '''arith_expression : arith_expression PLUS term
                            | arith_expression MINUS term'''
        p[0] = BinOp(p[2], p[1], p[3], p.lineno(2))

    def p_arith_expression(self, p):
        '''arith_expression : term'''
        p[0] = p[1]

    def p_term_binop(self, p):
        '''term : term TIMES factor
                | term DIVIDE factor
                | term MODULO factor'''
        p[0] = BinOp(p[2], p[1], p[3], p.lineno(2))

    def p_term(self, p):
        '''term : factor'''
        p[0] = p[1]

    # Factors (NOTE: PLY parser/YACC gives precedence lowest to highest, and hence how we have structured them)

    def p_factor_uminus(self, p):
        '''factor : MINUS factor'''
        p[0] = UnaryOp('-', p[2], p.lineno(1))

    def p_factor_int(self, p):
        '''factor : INT'''
        p[0] = Constant('int', p[1], p.lineno(1))

    def p_factor_true(self, p):
        '''factor : TRUE'''
        p[0] = Constant('bool', True, p.lineno(1))

    def p_factor_false(self, p):
        '''factor : FALSE'''
        p[0] = Constant('bool', False, p.lineno(1))

    def p_factor_id(self, p):
        '''factor : ID'''
        p[0] = Identifier(p[1], p.lineno(1))

    def p_factor_func_call(self, p):
        '''factor : ID LPAREN args_list RPAREN'''
        p[0] = FunctionCall(p[1], p[3], p.lineno(1))

    def p_factor_list_index(self, p):
        '''factor : ID LBRACK expression RBRACK'''
        p[0] = ListIndex(p[1], p[3], p.lineno(1))

    def p_factor_paren(self, p):
        '''factor : LPAREN expression RPAREN'''
        p[0] = p[2]

    def p_factor_list(self, p):
        '''factor : list_literal'''
        p[0] = p[1]

    def p_factor_len(self, p):
        '''factor : LEN LPAREN expression RPAREN'''
        p[0] = LenExpr(p[3], p.lineno(1))

    # List literals and expression/argument lists

    def p_list_literal_EPSILON(self, p):
        '''list_literal : LBRACK RBRACK'''
        p[0] = ListLiteral([], p.lineno(1))

    def p_list_literal(self, p):
        '''list_literal : LBRACK expr_list RBRACK'''
        p[0] = ListLiteral(p[2], p.lineno(1))

    def p_expr_list_multi(self, p):
        '''expr_list : expr_list COMMA expression'''
        p[0] = p[1] + [p[3]]

    def p_expr_list_single(self, p):
        '''expr_list : expression'''
        p[0] = [p[1]]

    def p_args_list(self, p):
        '''args_list : expr_list'''
        p[0] = p[1]

    def p_args_list_EPSILON(self, p):
        '''args_list : EPSILON'''
        p[0] = []

    # Empty/nothing parsing 
    def p_EPSILON(self, p):
        '''EPSILON :'''
        pass

    # Error handling
    def p_error(self, p):
        if p:
            msg = "Syntax error at token {} (type: {}) on line {}".format(repr(p.value), p.type, p.lineno)
            # NEWLINE is the actual lookahead token; wording helps avoid looking like a logging bug.
            if p.type == "NEWLINE":
                msg += (
                    " (the grammar expected more tokens before end of line, "
                    "e.g. ')', ']', ':', or another continuation of the current construct)"
                )
            raise SyntaxError(msg)
        else:
            raise SyntaxError("Syntax error at end of file")

    # Build the parser
    def build(self, **kwargs):
        self.tokens = tokens
        self.lexer = TheComPylersLexer()
        self.lexer.build()
        self.parser = yacc.yacc(module=self, **kwargs)

    # parse raw source code
    def parse(self, data):
        return self.parser.parse(preprocess_indentation(data))


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Parse the Python Subset source file and print its AST to JSON.')
    arg_parser.add_argument('FILE', help='Input file with Python Subset source code')
    args = arg_parser.parse_args()

    f = open(args.FILE, 'r')
    data = f.read()
    f.close()

    p = TheComPylersParser()
    p.build()
    ast = p.parse(data)

    print(json.dumps(ast.to_dict(), indent=5))
