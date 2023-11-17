#!/usr/bin/env python3

# USAGE:
# python3 compiler.py [input_file [output_file]]

import sys
from sly import Lexer, Parser

#################### LEXER ####################


# Adicionando um conjunto para rastrear variáveis declaradas
declared_variables = set()

class ÇLexer(Lexer):
    
    # token definitions
    literals = {';', '+', '-', '*', '/', '(', ')', '{', '}', ',', '='}
    tokens = {STDIO, INT, MAIN, PRINTF, STRING, NUMBER, NAME}
    STDIO   = '#include <stdio.h>'
    INT     = 'int'
    MAIN    = 'main'
    PRINTF  = 'printf'
    STRING  = r'"[^"]*"'
    NUMBER  = r'\d+'
    NAME    = r'[a-z]+'

    # ignored characters and patterns
    ignore = r' \t'
    ignore_newline = r'\n+'
    ignore_comment = r'//[^\n]*'

    # extra action for newlines
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    # error handling method
    def error(self, t):
        print(f"Illegal character '{t.value[0]}' in line {self.lineno}")
        self.index += 1

#################### PARSER ####################

class ÇParser(Parser):
    tokens = ÇLexer.tokens

    # error handling method
    def error(self, mesg):
        print(mesg, file=sys.stderr)
        sys.exit(1)
        
    # ---------------- program ----------------

    @_('STDIO main')
    def program(self, p):
        pass

    # ---------------- main ----------------

    @_('INT MAIN "(" ")" "{" statements "}"')
    def main(self, p):
        print('LOAD_CONST None')
        print('RETURN_VALUE')

    # ---------------- statements ----------------

    @_('statement statements')
    def statements(self, p):
        pass

    @_('')
    def statements(self, p):
        pass

    # ---------------- statement ----------------

    @_('printf')
    def statement(self, p):
        print()

    @_('declaration')
    def statement(self, p):
        print()

    @_('attribution')
    def statement(self, p):
        print()

    # ---------------- printf ----------------

    @_('STRING')
    def printf_format(self, p):
        print('LOAD_GLOBAL', 'print')
        print('LOAD_CONST', p.STRING)

    @_('PRINTF "(" printf_format "," expression ")" ";"')
    def printf(self, p):
        if p.printf_format is not None:
            variable_name = p.printf_format[2:]  # Extracting the variable name from the printf_format
            if variable_name not in declared_variables:
                print(f"Error: Variable '{variable_name}' not declared.")
                sys.exit(1)
            else:
                print('BINARY_MODULO')
                print('CALL_FUNCTION', 1)
                print('POP_TOP')

    # ---------------- declaration ----------------
    
    @_('INT NAME "=" expression ";"')
    def declaration(self, p):
        variable_name = p.NAME
        if variable_name in declared_variables:
            print(f"Error: Variable '{variable_name}' already declared.")
            sys.exit(1)
        else:
            declared_variables.add(variable_name)
            print('STORE_NAME', variable_name)
    
    # ---------------- attribution ----------------

    @_('NAME "=" expression ";"')
    def attribution(self, p): 
        variable_name = p.NAME
        if variable_name not in declared_variables:
            print(f"Error: Variable '{variable_name}' not declared.")
            sys.exit(1)
        else:
            print('STORE_NAME', variable_name)

    # ---------------- expression ----------------

    @_('expression "+" term')
    def expression(self, p):
        print('BINARY_ADD')

    @_('expression "-" term')
    def expression(self, p):
        print('BINARY_SUBTRACT')

    @_('term')
    def expression(self, p):
        pass

    # ---------------- term ----------------

    @_('term "*" factor')
    def term(self, p):
        print('BINARY_MULTIPLY')

    @_('term "/" factor')
    def term(self, p):
        print('BINARY_DIVIDE')

    @_('factor')
    def term(self, p):
        pass

    # ---------------- factor ----------------

    @_('NUMBER')
    def factor(self, p):
        print('LOAD_CONST', p.NUMBER)

    @_('"(" expression ")"')
    def factor(self, p):
        pass

    @_('NAME')
    def factor(self, p):
        variable_name = p.NAME
        if variable_name not in declared_variables:
            print(f"Error: Variable '{variable_name}' not declared.")
            sys.exit(1)
        else:
            print('LOAD_NAME', variable_name)

#################### MAIN ####################

lexer = ÇLexer()
parser = ÇParser()

if len(sys.argv) > 1:
    sys.stdin = open(sys.argv[1], 'r')
    
    if len(sys.argv) > 2:
        sys.stdout = open(sys.argv[2], 'w')

text = sys.stdin.read()
parser.parse(lexer.tokenize(text))
