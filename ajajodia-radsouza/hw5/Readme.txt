Files:
1) decaflexer.py: PLY/lex scanner specification file.
2) decafparser.py: PLY/yacc parser specification file.
3) ast.py: Class declaration for AST, Type check functions 
4) decafc.py: containing the main python function to put together the parser and lexer, perform syntax checking and generate code.
5) absmc.py: definitions for the abstract machine, and for manipulating abstract programs (still under works) 
6) input.decaf: tested inputs. NOTE: tests folder has more tests

How to run: [TERMINAL] python decafch.py [input file name] 
	    e.g. [TERMINAL] python decafc.py input.decaf

Output: If no error exists, a file with input file name and .ami extension is created in the same folder.
	If error exists, it is reported.

Design:
1. We have handled static method resolution (use sap) as well as instance method (use a0) for correct current object scope.
2. We have assumed an unbounded register machine.
3. We calculate offsets for multidimensional array accesses.
