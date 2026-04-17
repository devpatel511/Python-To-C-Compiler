#!/usr/bin/env python3

"""
NOTE: Token spec @ specs/lexical_specification.txt
"""

import argparse
from ply import lex
import re


tokens = [
    'PLUS', 
    'MINUS', 
    'TIMES', 
    'DIVIDE', 
    'MODULO',
    'LESSEQ', 
    'LESS', 
    'GREATEREQ', 
    'GREATER', 
    'EQOP', 
    'NEQ',
    'EQ',
    'COLON', 
    'COMMA', 
    'ARROW',
    'LPAREN', 
    'RPAREN', 
    'LBRACK', 
    'RBRACK',
    'NEWLINE', 
    'INT', 
    'ID',
    'COMMENT',
]

reserved = {
    'def' : 'DEF',
    'if' : 'IF',
    'else' : 'ELSE',
    'while' : 'WHILE',
    'return' : 'RETURN',
    'True' : 'TRUE',
    'False' : 'FALSE',
    'and' : 'AND',
    'or' : 'OR',
    'not' : 'NOT',
    'len' : 'LEN',
    'int' : 'INT_TYPE',
    'bool' : 'BOOL_TYPE',
    'list' : 'LIST_TYPE',
    # adding to reserved as we preprocess data and inject INDENT and DEDENT tokens
    'INDENT' : 'INDENT',
    'DEDENT' : 'DEDENT',
}

tokens += list(reserved.values())


def preprocess_indentation(data):
    """We preprocess data here to inject INDENT and DEDENT tokens and make our lives easier."""
    result = []
    indent_stack = [0]

    for line in data.splitlines():
        line = line.replace('\t', '    ')
        stripped = line.lstrip(' ')

        indent_level = len(line) - len(stripped)

        # Emit INDENT
        if indent_level > indent_stack[-1]:
            indent_stack.append(indent_level)
            result.append('INDENT')

        # Emit DEDENT(s)
        elif indent_level < indent_stack[-1]:
            while indent_stack[-1] > indent_level:
                indent_stack.pop()
                result.append('DEDENT')

        # Emit line content + NEWLINE
        result.append(stripped + '\n')

    # Close remaining indents at EOF
    while len(indent_stack) > 1:
        indent_stack.pop()
        result.append('DEDENT')

    return ' '.join(result)


class TheComPylersLexer:

    t_ignore = ' \t'

    # NOTE: longer tokens defined before shorter ones to ensure correct matching
    t_ARROW     = r'->'
    t_LESSEQ    = r'<='
    t_GREATEREQ = r'>='
    t_EQOP      = r'=='
    t_NEQ       = r'!='
    t_PLUS      = r'\+'
    t_MINUS     = r'-'
    t_TIMES     = r'\*'
    t_DIVIDE    = r'/'
    t_MODULO    = r'%'
    t_LESS      = r'<'
    t_GREATER   = r'>'
    t_EQ        = r'='
    t_COLON     = r':'
    t_COMMA     = r','
    t_LPAREN    = r'\('
    t_RPAREN    = r'\)'
    t_LBRACK    = r'\['
    t_RBRACK    = r'\]'

    # A regular expression rule with some action code
    def t_INT(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        # Disallowing identifier names we use in Sprint 2 IR Gen.
        if re.match(r'^_t\d+$', t.value) or t.value == 'ret':
            raise SyntaxError("Line {}: '{}' is a reserved internal name and cannot be used as an identifier.".format(t.lineno, t.value))
        t.type = reserved.get(t.value, 'ID') # Check for reserved words
        return t
    
    def t_COMMENT(self, t):
        r'\#.*'
        t.value = t.value.lstrip('#').strip() # Remove the '#' and surrounding whitespace
        return t

    # Define a rule so we can track line numbers. DO NOT MODIFY
    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        return t

    # Error handling rule. DO NOT MODIFY
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0] + " at line %d" % t.lineno)
        t.lexer.skip(1)

     # Build the lexer. DO NOT MODIFY
    def build(self, **kwargs):
        self.tokens = tokens
        self.lexer = lex.lex(module=self, **kwargs)

    # Test the output. DO NOT MODIFY
    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)


# Main function. DO NOT MODIFY
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Take in the Python Subset source code and perform lexical analysis.')
    parser.add_argument('FILE', help='Input file with Python Subset source code')
    args = parser.parse_args()

    f = open(args.FILE, 'r')
    data = f.read()
    f.close()

    m = TheComPylersLexer()
    m.build()
    m.test(preprocess_indentation(data))
