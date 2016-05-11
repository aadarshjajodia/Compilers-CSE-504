Files:
1) decaflexer.py: PLY/lex scanner specification file.
2) decafparser.py: PLY/yacc parser specification file.
3) ast.py: Class declaration for AST, Type check functions 
4) decafc.py: containing the main python function to put together the parser and lexer, perform syntax checking and generate code.
5) absmc.py: definitions for the abstract machine, and for manipulating abstract programs (still under works) 
6) graph_color.py: contains our implementation of graph coloring 
7) input.decaf: tested inputs. NOTE: tests folder has more tests

How to run: [TERMINAL] python decafch.py [input file name] 
	    e.g. [TERMINAL] python decafc.py input.decaf

Output: If no error exists, a file with input file name and .asm extension is created in the same folder.
	If error exists, it is reported.

Design:
1. We have maintained a list of instructions per method and calculated the defined and used vaariable set for the same. Using these we have caluclated in set and out set for live variable analysis.
2. We have implemented a grapg coloring based register reallocation technique which uses the in and out sets caluclated.
3. Handled halloc for classes and mutlidimenasional arrays and static field accesses.
4. We have optimised the code by removing reduntant move instructions after register reallocation.
5. As per the brief we haven't handled spilling of temporary as well as argument registers
6. We have taken each integer to be of 4 bytes as per the MIPS standard, hence all indirect addressing or offset based addressing is done with a miltiple of 4.
7. The main entry point of our program is the function "main" and not "main_entry_point". While testing SPIM gives error
   if it is unable to find a function named "main"
8. We have performed an optimization redundant save, restore instructions are removed from the instructions list, after liveness analysis
   has been performed. 

Known issues: We tried to incorporate basic SSA modelling in the register allocation but its buggy.
