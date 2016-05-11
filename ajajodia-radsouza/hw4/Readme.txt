Files:
1) decaflexer.py: PLY/lex scanner specification file.
2) decafparser.py: PLY/yacc parser specification file.
3) ast.py: Class declaration for AST, Type check functions 
4) decafch.py: containing the main python function to put together the parser and lexer, take input from given file, etc., and perform syntax checking.
5) input.decaf: tested inputs

How to run: [TERMINAL] python decafch.py [input file name] 
	    e.g. [TERMINAL] python decafch.py input.decaf

Output: AST tree, if no syntax errors found
	List of errors 

Design:
Each Statement/Expression type has a type_check and populate_type fuctions associated with it to resolve the field/method scope. For fields scope and type resolution, we use is_subtype function to allow typecasting as per allowed semantics. Variable tables are used to find scope and resolved recursivelyi if needed across blocks and parent classes. For method resolution, we maintain a list of matching signature methods and if it is called using some class object. The list is then refined to might the best match method (i.e. the one which meets the strict subtype most). Under scenarios, we also look into parent classes if no suitable method/field is found in the child class. Also we have made limited access to private/static members as per the spec provided.

Known Issues: NONE
