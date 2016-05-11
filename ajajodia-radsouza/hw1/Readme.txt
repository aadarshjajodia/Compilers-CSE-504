1) SSM Interpreter: Approach used is multiple pass. 
   File: interpreter.py
	* Basic operations as per given requirements in assignment brief.
	* Multi Line single instruction, Multiple instructions on same line. 
	* Detects label errors: invalid label format, same label declared twice, unknown label jmp etc
	* Handled all comments related case: single line, after instructions etc
	* Handled parameter validation for two argument operations like ildc should be followed by a number etc
	* Handled all invalid stack pops

   How to run: [In Terminal] python interpreter.py
		<<Input Program>> CTRL+D

2) SC Compiler: Approaach used is multipass
   File: simple_calculator.py
	* Basic operations as per given requirements in assignement brief.
	* Validation of Infix expressions
	* Multiple instructions on same line, redundant ';' handling like C compiler
	* Handled same variable reuse in operations like reassigment and calculations
	* Raised error if a variable is used before assigment.
   How to run: [In Terminal] python simple_calculator.py
                <<Input Program>> CTRL+D
 
