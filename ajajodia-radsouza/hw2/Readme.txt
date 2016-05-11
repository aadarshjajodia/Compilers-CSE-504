Files:
1) decaflexer.py: PLY/lex scanner specification file.
2) decafparser.py: PLY/yacc parser specification file.
3) decafch.py: containing the main python function to put together the parser and lexer, take input from given file, etc., and perform syntax checking.
4) input.txt: tested inputs

How to run: [TERMINAL] python decafch.py [input file name] 
	    e.g. [TERMINAL] python decafch.py input.txt

Output: Yes, if no syntax errors found
	List of errors and corresponding line numbers 

Known Shift Reduce Conflicts:
1) 2 Shift/Reduce Conflict for this production
	stmt -> IF LPAREN expression RPAREN stmt . else_stmt
	else_stmt -> .
	else_stmt -> . ELSE stmt

	Resolution: shift/reduce conflict for ELSE resolved as shift
	The resolution of this conflict as shift is acceptable because we want the ELSE statement to be associated with the innermost IF statment

2)	1 Shift/Reduce conflict for this production
	stmt -> STDOUT PERIOD PRINT LPAREN SCONST . RPAREN SEMI
	literal -> SCONST .

	Resolution: shift/reduce conflict for RPAREN resolved as shift
	The resolution of this conflict is again perfectly valid because when we encounter a RPAREN in this production we are still expecting a SEMICOLON to follow this
	terminal after which the reduction should be applied.

3)	expression_one_or_more -> LBRACKET expression RBRACKET .
    expression_one_or_more -> LBRACKET expression RBRACKET . expression_one_or_more
    expression_one_or_more -> . LBRACKET expression RBRACKET
    expression_one_or_more -> . LBRACKET expression RBRACKET expression_one_or_more

	Resolution : shift/reduce conflict for LBRACKET resolved as shift
	The resolution of this rule as shift is acceptable as when we see a RBRACE we want to reduce and want to shift on a LBRACE

* KNOWN ISSUES:
1) We added the error resynchronization rules for Missing Semilcolon. We could incremental add more error rules but it started causing more shift reduce conflicts. 
2) Inorder To handle multiple errors in the code the current parser flags more errors than there actually are in the code. The most likely reason for this should be the symbol stack and state stack of the parser. We tried to flush the stack to a stable state as per the below code:
def p_error(p):
        global error
        error = True

        if not p:
                return

        if p:
                print "\nSyntax eror at line no. " + str(p.lineno),

        while True:
               if len(parser.symstack) == 0 or len(parser.statestack) == 0:
                       break
               tok = parser.symstack.pop()             # Get the next token
               state = parser.statestack.pop()
               if not tok or tok.type == 'LBRACE': break

        if not len(parser.symstack): 
               parser.symstack.append(tok)
               parser.statestack.append(state)

        while True:
                tok = parser.token()             # Get the next token
                if not tok or tok.type == 'SEMI' or tok.type == 'RBRACE': break
   
        parser.errok()
        
        # Return SEMI to the parser as the next lookahead token
        return tok
 
