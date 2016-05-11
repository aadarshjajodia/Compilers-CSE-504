import sys
sys.path.insert(0,"../..")
import ply.lex as lex

reserved = (
    'BOOLEAN', 'BREAK', 'CONTINUE', 'CLASS', 'DO',
    'ELSE', 'EXTENDS', 'FALSE', 'FLOAT', 'FOR', 'IF',
    'INT', 'NEW', 'NULL', 'PRIVATE', 'PUBLIC', 'RETURN',
    'STATIC', 'SUPER', 'THIS', 'TRUE', 'VOID', 'WHILE',
    )

other_reserved_keywords = (
    'STDIN', 'STDOUT', 'PRINT', 'SCANINT', 'SCANFLOAT'
)

tokens = reserved + other_reserved_keywords + (
    # Literals (identifier, integer constant, float constant)
    'ID', 'FCONST', 'ICONST', 'SCONST', 

    # Arithmetic Operators (+,-,*,/)
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',

    # Boolean Operators (&&, ||, ==, !=, <, >, <=, >=)
    'AND', 'OR', 'EQ', 'NE', 'LT', 'GT', 'LE', 'GE',

    # Assignment Operators(=)
    'EQUALS',

    # Increment/decrement (++,--)
    'PLUSPLUS', 'MINUSMINUS',

    # Unary Operators ( +, - , !)
    'NOT',

    # Delimeters ( ) [ ] { } , . ;
    'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET',
    'LBRACE', 'RBRACE',
    'COMMA', 'PERIOD', 'SEMI'
    )

# Floating literal
t_FCONST = r'[+-]?(?=\d*[.eE])(?=\.?\d)\d*\.?\d*(?:[eE][+-]?\d+)?'
"""    try:
        t.value = float(t.value)
    except ValueError:
        print "floating value too large", t.value
        t.value = 0
    return t"""

t_ignore           = ' \t'

# Newlines
def t_NEWLINE(t):
    r'[\n]+'
    t.lexer.lineno += t.value.count("\n")

# Arithmetic Operators
t_PLUS             = r'\+'
t_MINUS            = r'-'
t_TIMES            = r'\*'
t_DIVIDE           = r'/'

# Boolean Operators
t_AND              = r'&&'
t_OR               = r'\|\|'
t_EQ               = r'=='
t_NE               = r'!='
t_LT               = r'<'
t_GT               = r'>'
t_LE               = r'<='
t_GE               = r'>='

# Assignment Operators
t_EQUALS           = r'='

# Increment/decrement
t_PLUSPLUS         = r'\+\+'
t_MINUSMINUS       = r'--'

# Unary Operators
t_NOT              = r'!'

# Delimeters
t_LPAREN           = r'\('
t_RPAREN           = r'\)'
t_LBRACKET         = r'\['
t_RBRACKET         = r'\]'
t_LBRACE           = r'\{'
t_RBRACE           = r'\}'
t_COMMA            = r','
t_PERIOD           = r'\.'
t_SEMI             = r';'

reserved_map = { }
for r in reserved:
    reserved_map[r.lower()] = r

other_reserved_keywords_map = { }
other_reserved_keywords_map['In'] = 'STDIN'
other_reserved_keywords_map['Out'] = 'STDOUT'
other_reserved_keywords_map['print'] = 'PRINT'
other_reserved_keywords_map['scan_int'] = 'SCANINT'
other_reserved_keywords_map['scan_float'] = 'SCANFLOAT'

def t_ID(t):
    r'[A-Za-z][\w_]*'
    if t.value in reserved_map:
        t.type = reserved_map.get(t.value)
    elif t.value in other_reserved_keywords_map:
        t.type = other_reserved_keywords_map.get(t.value)
    else:
        t.type = "ID"
    return t

# Integer literal
t_ICONST= r'\d+'
   # try:
   #     t.value = int(t.value)
   # except ValueError:
   #     print "integer value too large", t.value
   #     t.value = 0
   # return t


t_SCONST = r'\"([^\\\n]|(\\.))*?\"'

# Comments
def t_comment(t):
    #todo
    r'//[^\n]*\n|/\*(.|[\r\n])*?\*/'
    t.lexer.lineno += t.value.count('\n')

def t_error(t):
    print("Illegal character %s" % repr(t.value[0]))
    t.lexer.skip(1)

# Build the parser
def make_lexer():
        lexer = lex.lex()
        return lexer
