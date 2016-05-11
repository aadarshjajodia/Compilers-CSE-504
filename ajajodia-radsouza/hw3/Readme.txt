Files:
1) decaflexer.py: PLY/lex scanner specification file.
2) decafparser.py: PLY/yacc parser specification file.
3) ast.py: Class declaration for AST 
4) decafch.py: containing the main python function to put together the parser and lexer, take input from given file, etc., and perform syntax checking.
5) input.decaf: tested inputs

How to run: [TERMINAL] python decafch.py [input file name] 
	    e.g. [TERMINAL] python decafch.py input.decaf

Output: AST tree, if no syntax errors found
	List of errors 

Design:
Decaf_Program Class is made out of Decaf_Class Classes which are made out of Decaf_Field, Decaf_Method and Decaf_Constructor Classes. We maintain per Method a Variable table as well as a Variable table per Block for scope resolution. We also maintain a per block mapping to parent block and all its child block. This helps in scope resolution for redefined variables.   

Design Decision and Known issues:
1) As per Piazza discussion and Professor's inputs, we did not resolve scope with Parent classes.
2) IF a method is not resolved, then for now we have not mapped it to other Classes. This is scope related across classes resolution. For now we assume, the method is inheritted by the current class.
