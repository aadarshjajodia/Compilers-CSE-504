import ply.yacc as yacc
import decaflexer
from decaflexer import tokens
#from decaflexer import errorflag
from decaflexer import lex
from ast import *
error = False

fieldIdCount=1
methodIdCount=1
constructorIdCount=1
import sys
import logging

operator_dict = {'+':'add', '-':'sub', '*':'mul', '/':'div', '&&':'and', '||':'or', \
                 '==':'eq', '!=':'neq', '<':'lt', '<=':'leq', '>':'gt', '>=':'geq'}
prog = None
precedence = (
    ('right', 'ASSIGN'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQ', 'NEQ'),
    ('nonassoc', 'LEQ', 'GEQ', 'LT', 'GT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('right', 'NOT'),
    ('right', 'UMINUS'),
    ('right', 'ELSE'),
    ('right', 'RPAREN'),
)


def init():
    decaflexer.errorflag = False


### DECAF Grammar

# Top-level
def p_pgm(p):
    'pgm : class_decl_list'
    p[0] = decaf_program(p[1])
    global prog
    prog = p[0]
    pass

def p_class_decl_list_nonempty(p):
    'class_decl_list : class_decl class_decl_list'
    p[0] = []
    p[0].append(p[1])
    if p[2]:
        while len(p[2]) > 0:
            p[0].append(p[2].pop(0))

def p_class_decl_list_empty(p):
    'class_decl_list : '
    pass

def p_class_decl(p):
    'class_decl : CLASS ID extends LBRACE class_body_decl_list RBRACE'
    p[0] = decaf_class(p[2], p[3], p[5])
    p[0].update(p[2])
    #p[0].print_class()
    pass
def p_class_decl_error(p):
    'class_decl : CLASS ID extends LBRACE error RBRACE'
    error = True
    # error in class declaration; skip to next class decl.
    pass

def p_extends_id(p):
    'extends : EXTENDS ID '
    p[0] = p[2]
    pass
def p_extends_empty(p):
    ' extends : '
    pass

def p_class_body_decl_list_plus(p):
    'class_body_decl_list : class_body_decl_list class_body_decl'
    p[0] = []
    while len(p[1]) > 0:
        p[0].append(p[1].pop(0))
    p[0].append(p[2])
    pass
def p_class_body_decl_list_single(p):
    'class_body_decl_list : class_body_decl'
    p[0] = []
    p[0].append(p[1])
    pass

def p_class_body_decl_field(p):
    'class_body_decl : field_decl'
    p[0] = p[1]
    pass
def p_class_body_decl_method(p):
    'class_body_decl : method_decl'
    p[0] = p[1]
    pass
def p_class_body_decl_constructor(p):
    'class_body_decl : constructor_decl'
    p[0] = p[1]
    pass

# Field/Method/Constructor Declarations

def p_field_decl(p):
    'field_decl : mod var_decl'
    global fieldIdCount
    p[0] = []
    if p[2]:
        for x in p[2]:
            p[0].append(decaf_class_field(x.name, fieldIdCount, "", p[1].visibility, p[1].applicability, x.type))
            fieldIdCount = fieldIdCount + 1
    pass

def p_method_decl_void(p):
    'method_decl : mod VOID ID LPAREN param_list_opt RPAREN block'
    if error == False:
        global methodIdCount
        p[0] = decaf_class_method(p[3], methodIdCount, "", p[1].visibility, p[1].applicability, p[7])
        if p[5]:
            p[0].update_varList(p[5])
        p[0].error_check_duplicate_var()
        p[7].formalParams = p[5]
        if p[7].variableTable:
            p[0].update_varList(p[7].variableTable)
        outermostblock  = p[7].childblock
        lastblock = p[7].childblock
        while outermostblock != None:
            outermostblock.error_check_duplicate_var()
            p[0].update_varList(outermostblock.variableTable)
            lastblock = outermostblock
            outermostblock = outermostblock.childblock
        #lastblock.field_access_lookup(lastblock)
        methodIdCount = methodIdCount + 1
        p[0].update_var(p[5])
    #todo Iterate over the first block and assign variables to the local variables of the function
    pass
def p_method_decl_nonvoid(p):
    'method_decl : mod type ID LPAREN param_list_opt RPAREN block'
    if error == False:
        global methodIdCount
        p[0] = decaf_class_method(p[3], methodIdCount, "", p[1].visibility, p[1].applicability, p[7], p[2])
        if p[5]:
            p[0].update_varList(p[5])
        p[0].error_check_duplicate_var()
        p[7].formalParams = p[5]
        if p[7].variableTable:
            p[0].update_varList(p[7].variableTable)
        outermostblock = p[7].childblock
        lastblock = p[7].childblock
        while outermostblock != None:
            outermostblock.error_check_duplicate_var()
            p[0].update_varList(outermostblock.variableTable)
            lastblock = outermostblock
            outermostblock = outermostblock.childblock
        #lastblock.field_access_lookup(lastblock)
        methodIdCount = methodIdCount + 1
        p[0].update_var(p[5])
    pass

def p_constructor_decl(p):
    'constructor_decl : mod ID LPAREN param_list_opt RPAREN block'
    if error == False:
        global constructorIdCount
        p[0] = decaf_class_constructor(constructorIdCount, p[1].visibility, p[6])
        if p[4]:
            p[0].update_varList(p[4])
        p[0].error_check_duplicate_var()
        p[6].formalParams = p[4]
        if p[6].variableTable:
            p[0].update_varList(p[6].variableTable)
        outermostblock = p[6].childblock
        lastblock = p[6].childblock
        while outermostblock != None:
            outermostblock.error_check_duplicate_var()
            p[0].update_varList(outermostblock.variableTable)
            lastblock = outermostblock
            outermostblock = outermostblock.childblock
        #   lastblock.field_access_lookup(lastblock)
        constructorIdCount = constructorIdCount + 1
        p[0].update_var(p[4])
    pass

def p_mod(p):
    'mod : visibility_mod storage_mod'
    p[0] = decaf_mod(p[1], p[2])
    pass

def p_visibility_mod_pub(p):
    'visibility_mod : PUBLIC'
    p[0] = p[1]
    pass
def p_visibility_mod_priv(p):
    'visibility_mod : PRIVATE'
    p[0] = p[1]
    pass
def p_visibility_mod_empty(p):
    'visibility_mod : '
    p[0] = "private"
    pass

def p_storage_mod_static(p):
    'storage_mod : STATIC'
    p[0] = p[1]
    pass

def p_storage_mod_empty(p):
    'storage_mod : '
    p[0] = "instance"
    pass

def p_var_decl(p):
    'var_decl : type var_list SEMICOLON'
    p[0] = []
    for x in p[2]:
        p[0].append(decaf_variable(p[1], x, "local"))
    #p[0] = add_member(p[1],p[2])
    pass

def p_type_int(p):
    'type :  INT'
    p[0] = decaf_type_record(p[1])
    pass
def p_type_bool(p):
    'type :  BOOLEAN'
    p[0] = decaf_type_record(p[1])
    pass
def p_type_float(p):
    'type :  FLOAT'
    p[0] = decaf_type_record(p[1])
    pass
def p_type_id(p):
    'type :  ID'
    p[0] = decaf_type_record(p[1])
    pass

def p_var_list_plus(p):
    'var_list : var_list COMMA var'
    p[0] = []
    while len(p[1]) > 0:
        p[0].append(p[1].pop(0))
    p[0].append(p[3])
    pass
def p_var_list_single(p):
    'var_list : var'
    p[0] = []
    p[0].append(p[1])
    pass

def p_var_id(p):
    'var : ID'
    p[0] = p[1]
    pass
def p_var_array(p):
    'var : var LBRACKET RBRACKET'
    p[0] = p[1]
    pass

def p_param_list_opt(p):
    'param_list_opt : param_list'
    p[0] = p[1]
    pass
def p_param_list_empty(p):
    'param_list_opt : '
    pass

def p_param_list(p):
    'param_list : param_list COMMA param'
    p[0] = []
    while len(p[1]) > 0:
        p[0].append(p[1].pop(0))
    p[0].append(p[3])
    pass
def p_param_list_single(p):
    'param_list : param'
    p[0] = []
    p[0].append(p[1])
    pass

def p_param(p):
    'param : type var'
    p[0] = decaf_variable(p[1], p[2], "formal")
    pass

# Statements

def p_block(p):
    'block : LBRACE stmt_list RBRACE'
    p[0] = decaf_block_statement(p[2])
    if error == False:
        p[0].update_block()
    pass
def p_block_error(p):
    'block : LBRACE stmt_list error RBRACE'
    error = True
    # error within a block; skip to enclosing block
    pass

def p_stmt_list_empty(p):
    'stmt_list : '
    pass
def p_stmt_list(p):
    'stmt_list : stmt_list stmt'
    p[0] = []
    if p[1]:
        while len(p[1]) > 0:
            p[0].append(p[1].pop(0))
    p[0].append(p[2])
    pass


def p_stmt_if(p):
    '''stmt : IF LPAREN expr RPAREN stmt ELSE stmt
          | IF LPAREN expr RPAREN stmt'''
    if len(p)>6:
    	p[0] = decaf_if_statement(p[3],p[5],p[7])
    else:
    	p[0] = decaf_if_statement(p[3],p[5])
    pass
def p_stmt_while(p):
    'stmt : WHILE LPAREN expr RPAREN stmt'
    p[0] = decaf_while_statement(p[3],p[5])
    pass
def p_stmt_for(p):
    'stmt : FOR LPAREN stmt_expr_opt SEMICOLON expr_opt SEMICOLON stmt_expr_opt RPAREN stmt'
    p[0] = decaf_for_statement(p[9],p[3],p[5],p[7])
    pass
def p_stmt_return(p):
    'stmt : RETURN expr_opt SEMICOLON'
    p[0] = decaf_return_statement(p[2])
    pass
def p_stmt_stmt_expr(p):
    'stmt : stmt_expr SEMICOLON'
    p[0] = p[1]
    pass
def p_stmt_break(p):
    'stmt : BREAK SEMICOLON'
    p[0] = decaf_break_statement()
    pass
def p_stmt_continue(p):
    'stmt : CONTINUE SEMICOLON'
    p[0] = decaf_continue_statement()
    pass
def p_stmt_block(p):
    'stmt : block'
    p[0] = p[1]
    pass
def p_stmt_var_decl(p):
    'stmt : var_decl'
    p[0] = decaf_variable_list(p[1])
    #print p[1]
    #p[0] = p[1]
    #print "Inside Var Decl" , p[1].type, p[1].fields
    pass
def p_stmt_error(p):
    'stmt : error SEMICOLON'
    print("Invalid statement near line {}".format(p.lineno(1)))
    error = True
    decaflexer.errorflag = True

# Expressions
def p_literal_int_const(p):
    'literal : INT_CONST'
    p[0] = decaf_constant_expression("int", p[1])
    pass
def p_literal_float_const(p):
    'literal : FLOAT_CONST'
    p[0] = decaf_constant_expression("float", p[1])
    pass
def p_literal_string_const(p):
    'literal : STRING_CONST'
    p[0] = decaf_constant_expression("string", p[1])
    pass
def p_literal_null(p):
    'literal : NULL'
    p[0] = decaf_constant_expression("", p[1])
    pass
def p_literal_true(p):
    'literal : TRUE'
    p[0] = decaf_constant_expression("boolean", p[1])
    pass
def p_literal_false(p):
    'literal : FALSE'
    p[0] = decaf_constant_expression("boolean", p[1])
    pass

def p_primary_literal(p):
    'primary : literal'
    p[0] = p[1]
    pass
def p_primary_this(p):
    'primary : THIS'
    p[0] = decaf_this_expression()
    pass
def p_primary_super(p):
    'primary : SUPER'
    p[0] = decaf_super_expression()
    pass
def p_primary_paren(p):
    'primary : LPAREN expr RPAREN'
    pass
def p_primary_newobj(p):
    'primary : NEW ID LPAREN args_opt RPAREN'
    p[0] = decaf_new_object_expression(p[2], p[4])
    pass
def p_primary_lhs(p):
    'primary : lhs'
    p[0] = p[1]
    pass
def p_primary_method_invocation(p):
    'primary : method_invocation'
    p[0] = p[1]
    pass

def p_args_opt_nonempty(p):
    'args_opt : arg_plus'
    p[0] = p[1]
    pass
def p_args_opt_empty(p):
    'args_opt : '
    pass

def p_args_plus(p):
    'arg_plus : arg_plus COMMA expr'
    p[0] = []
    while len(p[1]) > 0:
        p[0].append(p[1].pop(0))
    p[0].append(p[3])
    pass
def p_args_single(p):
    'arg_plus : expr'
    p[0] = []
    p[0].append(p[1])
    pass

def p_lhs(p):
    '''lhs : field_access
           | array_access'''
    p[0] = p[1]
    pass

def p_field_access_dot(p):
    'field_access : primary DOT ID'
    p[0] = decaf_field_access_expression(decaf_var_expression(p[3]),p[1])
    pass
def p_field_access_id(p):
    'field_access : ID'
    p[0] = decaf_field_access_expression(decaf_var_expression(p[1]))
    pass

def p_array_access(p):
    'array_access : primary LBRACKET expr RBRACKET'
    p[0] = decaf_array_access_expression(p[1], p[3])
    pass

def p_method_invocation(p):
    'method_invocation : field_access LPAREN args_opt RPAREN'
    if error == False:
        p[1].update_field_access_expression()
        p[0] = decaf_method_invocation_expression(p[1], p[3])
    pass

def p_expr_basic(p):
    '''expr : primary
            | assign
            | new_array'''
    p[0] = p[1]
    pass
def p_expr_binop(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr MULTIPLY expr
            | expr DIVIDE expr
            | expr EQ expr
            | expr NEQ expr
            | expr LT expr
            | expr LEQ expr
            | expr GT expr
            | expr GEQ expr
            | expr AND expr
            | expr OR expr
    '''
    p[0] = decaf_binary_expression(p[1], p[3], operator_dict[p[2]])
    pass
def p_expr_unop(p):
    '''expr : PLUS expr %prec UMINUS
            | MINUS expr %prec UMINUS
            | NOT expr'''
    if p[1] == "-":
        val = "neg"
    elif p[1] == '!':
        val = "not"
    else:
        val = ""
    p[0] = decaf_unary_expression(p[2], val)
    pass

def p_assign_equals(p):
    'assign : lhs ASSIGN expr'
    p[0] = decaf_expression_statement(decaf_assign_expression(p[1], p[3]))
    pass
def p_assign_post_inc(p):
    'assign : lhs INC'
    p[0] = decaf_expression_statement(decaf_auto_expression(p[1], "inc", "post"))
    pass
def p_assign_pre_inc(p):
    'assign : INC lhs'
    p[0] = decaf_expression_statement(decaf_auto_expression(p[1], "inc", "pre"))
    pass
def p_assign_post_dec(p):
    'assign : lhs DEC'
    p[0] = decaf_expression_statement(decaf_auto_expression(p[1], "dec", "post"))
    pass
def p_assign_pre_dec(p):
    'assign : DEC lhs'
    p[0] = decaf_expression_statement(decaf_auto_expression(p[1], "dec", "pre"))
    pass

def p_new_array(p):
    'new_array : NEW type dim_expr_plus dim_star'
    if error == False:
        p[2].update_type_record_to_array(p[3], p[4])
        p[0] = decaf_new_array_expression(p[2])
    pass

def p_dim_expr_plus(p):
    'dim_expr_plus : dim_expr_plus dim_expr'
    p[0] = []
    while len(p[1]) > 0:
        p[0].append(p[1].pop(0))
    p[0].append(p[2])
    pass
def p_dim_expr_single(p):
    'dim_expr_plus : dim_expr'
    p[0] = []
    p[0].append(p[1])
    pass

def p_dim_expr(p):
    'dim_expr : LBRACKET expr RBRACKET'
    p[0] = p[2]
    pass

def p_dim_star(p):
    'dim_star : LBRACKET RBRACKET dim_star'
    p[0] = 1
    p[0] = p[0] + p[3]
    pass
def p_dim_star_empty(p):
    'dim_star : '
    p[0] = 0
    pass

def p_stmt_expr(p):
    '''stmt_expr : assign
                 | method_invocation'''
    p[0] = p[1]
    pass

def p_stmt_expr_opt(p):
    'stmt_expr_opt : stmt_expr'
    p[0] = p[1]
    pass
def p_stmt_expr_empty(p):
    'stmt_expr_opt : '
    pass

def p_expr_opt(p):
    'expr_opt : expr'
    p[0] = p[1]
    pass
def p_expr_empty(p):
    'expr_opt : '
    pass


def p_error(p):
    global error
    error = True
    if p is None:
        print ("Unexpected end-of-file")
    else:
        print ("Unexpected token '{0}' near line {1}".format(p.value, p.lineno))
    decaflexer.errorflag = True

parser = yacc.yacc()

def from_file(filename):
    try:
        with open(filename, "rU") as f:
            init()
            parser.parse(f.read(), lexer=lex.lex(module=decaflexer), debug=None)
        return not decaflexer.errorflag
    except IOError as e:
        print "I/O error: %s: %s" % (filename, e.strerror)


if __name__ == "__main__" :
    f = open(sys.argv[1], "r")
    logging.basicConfig(
            level=logging.CRITICAL,
    )
    log = logging.getLogger()
    res = parser.parse(f.read(), lexer=lex.lex(module=decaflexer), debug=log)
    if parser.errorok :
        print("Parse succeed")
    else:
        print("Parse failed")
