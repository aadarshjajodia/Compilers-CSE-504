import decaflexer
import ply.yacc as yacc
tokens = decaflexer.tokens

error = False

precedence = (
	('right', 'EQUALS'),
	('left', 'OR'),
	('left', 'AND'),
	('nonassoc', 'EQ', 'NE'),
	('nonassoc', 'LT', 'GT', 'LE', 'GE'),
	('left', 'PLUS', 'MINUS'),
	('left', 'TIMES', 'DIVIDE'),
	('left', 'NOT'),
)

def p_progam(p):
	'program : class_decl_inf'

def p_class_decl_inf(p):
    '''class_decl_inf :
                    | class_decl class_decl_inf'''
def p_class_decl(p):
    'class_decl : CLASS ID extend LBRACE class_body_decl RBRACE'

def p_class_body_decl(p):
    '''class_body_decl : field_decl
                    | method_decl
                    | constructor_decl
                    | field_decl class_body_decl
                    | method_decl class_body_decl
                    | constructor_decl class_body_decl'''

def p_extend(p):
    '''extend :
            | EXTENDS ID'''

def p_field_declaration(p):
    'field_decl : modifier var_decl'

def p_modifier(p):
    '''modifier : modifier_type_public_private modifier_type_static'''

def p_modifier_type(p):
    '''modifier_type_public_private :
                | PUBLIC
                | PRIVATE'''

def p_modifier_type2(p):
    '''modifier_type_static :
                        | STATIC'''

def p_var_decl(p):
    'var_decl : type variables SEMI'

def p_type_declaration(p):
    '''type : INT
            | FLOAT
            | BOOLEAN
            | ID'''

def p_type_variables(p):
    '''variables : variable
                | variable COMMA variables'''
def p_variable(p):
    '''variable : ID array_subscripts'''

def p_array_subscripts(p):
    '''array_subscripts :
                    | LBRACKET RBRACKET array_subscripts'''

def p_method_declaration(p):
    '''method_decl : modifier type ID LPAREN formals_opt RPAREN block
                    | modifier VOID ID LPAREN formals_opt RPAREN block'''

def p_formals_opt(p):
    '''formals_opt :
                | formals'''

def p_formals(p):
    '''formals : formal_param
                | formal_param COMMA formals'''

def p_formal_param(p):
    '''formal_param : type variable'''

def p_constructor_decl(p):
    '''constructor_decl : modifier ID LPAREN formals_opt RPAREN block'''

def p_block_decl(p):
    '''block : LBRACE stat_inf RBRACE'''

def p_stat_inf(p):
    '''stat_inf :
                | stmt stat_inf'''

def p_stmt(p):
    '''stmt : IF LPAREN expression RPAREN stmt else_stmt
            | WHILE LPAREN expression RPAREN stmt
            | FOR LPAREN stmt_expr_opt SEMI expression_opt SEMI stmt_expr_opt RPAREN stmt
            | RETURN expression_opt SEMI
            | stmt_expr SEMI
            | BREAK SEMI
            | CONTINUE SEMI
            | STDOUT PERIOD PRINT LPAREN SCONST RPAREN SEMI
            | STDOUT PERIOD PRINT LPAREN expression RPAREN SEMI
            | DO block WHILE LPAREN expression RPAREN SEMI
            | block
            | var_decl
            | SEMI'''

def p_stmt_error(p):
	'''stmt : IF LPAREN expression RPAREN error else_stmt
	| RETURN expression_opt error
        | stmt_expr error
        | BREAK error
        | CONTINUE error
        | STDOUT PERIOD PRINT LPAREN SCONST RPAREN error
        | STDOUT PERIOD PRINT LPAREN expression RPAREN error
        | DO block WHILE LPAREN expression RPAREN error
	| type variables error'''
	print "Missing Semicolon"

def p_else_stmt(p):
    '''else_stmt :
            | ELSE stmt'''

def p_literal_num(p):
	'''literal : ICONST
			| FCONST
			| SCONST
			| NULL
			| TRUE
			| FALSE'''


def p_primary_num(p):
    '''primary : literal
            | THIS
            | SUPER
            | LPAREN expression RPAREN
            | NEW ID LPAREN arguments_opt RPAREN
            | lhs
            | method_invocation'''

def p_arguments_num(p):
    '''arguments_opt :
                | arguments'''

def p_argumets_num(p):
    '''arguments : expression
                | expression COMMA arguments'''

def p_lhs_num(p):
    '''lhs : field_access
           | array_access'''

def p_field_access(p):
    '''field_access : primary PERIOD ID
                    | ID'''

def p_array_access(p):
    'array_access : primary LBRACKET expression RBRACKET'

def p_method_invocation(p):
    '''method_invocation : field_access LPAREN arguments_opt RPAREN'''

def p_expression_opt(p):
    '''expression_opt :
                | expression'''

def p_expression_one_or_more(p):
    '''expression_one_or_more : LBRACKET expression RBRACKET
                            | LBRACKET expression RBRACKET expression_one_or_more'''

def p_expression_plus_minus(p):
    '''expression : primary
                | assign
                | new_array
                | expression PLUS expression
                | PLUS expression
		| expression MINUS expression
		| MINUS expression
		| NOT expression
		| expression TIMES expression
		| expression DIVIDE expression
		| expression LT expression
		| expression GT expression
		| expression LE expression
		| expression GE expression
		| expression AND expression
		| expression OR expression
		| expression EQ expression
		| expression NE expression
		| STDIN PERIOD SCANINT LPAREN RPAREN
                | STDIN PERIOD SCANFLOAT LPAREN RPAREN'''

def p_assign_num(p):
	'''assign : lhs EQUALS expression
	        | lhs PLUSPLUS
	        | lhs MINUSMINUS
	        | PLUSPLUS lhs
	        | MINUSMINUS lhs'''

def p_new_array(p):
    'new_array : NEW type expression_one_or_more array_subscripts'

def p_stmt_expr_opt(p):
    '''stmt_expr_opt :
                    | stmt_expr'''

def p_stmt_expression(p):
    '''stmt_expr : assign
                 | method_invocation'''

def p_error(p):
	global error
	error = True

	if not p:
		return
 
	if p:
		print "\nSyntax eror at line no. " + str(p.lineno),
	
	#while True:
	#	if len(parser.symstack) == 0 or len(parser.statestack) == 0:
	#		break
        #	tok = parser.symstack.pop()             # Get the next token
	#	state = parser.statestack.pop()
	#	if not tok or tok.type == 'LBRACE': break
	
	#if not len(parser.symstack): 
	#	parser.symstack.append(tok)
	#	parser.statestack.append(state)
	
	while True:
        	tok = parser.token()             # Get the next token
        	if not tok or tok.type == 'SEMI' or tok.type == 'RBRACE': break

	#tok = parser.token()	
	parser.errok()
	#parser.symstack.append(p)

	# Return SEMI to the parser as the next lookahead token
	return tok 

parser = yacc.yacc()

# Build the parser
def make_parser():
	global parser #= yacc.yacc()
	return parser
