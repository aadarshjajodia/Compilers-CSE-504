import sys

#Main Program class
class decaf_program:
	classCount = 0
	decafClass = []
	def __init__(self, classes):
		decaf_program.decafClass = classes 
		decaf_program.classCount = len(classes)
	#check redefination of classes and fields
	def verify_classes(self):
                for x in range(0, len(decaf_program.decafClass)):
                        for y in range(x+1, len(decaf_program.decafClass)):
                                if decaf_program.decafClass[x].className is decaf_program.decafClass[y].className:
                                        print "Error Class " + decaf_program.decafClass[x].className +" Redefination"
                                        sys.exit(0)
		for x in decaf_program.decafClass:
			for y in range(0,len(x.decafFields)):
				for z in range(y+1,len(x.decafFields)):
					if x.decafFields[y].fieldName is x.decafFields[z].fieldName:
						 print "Error: Field "+ x.decafFields[y].fieldName + " redeclaration in Class " + x.className
                                        	 sys.exit(0)

	#print prog
	def print_prog(self):
		self.verify_classes()
		print "------------------------------------------------------------------------------------------------------------"
		for x in decaf_program.decafClass:
			x.print_class()
			print "------------------------------------------------------------------------------------------------------------"
	#update each variable  with parent class
	def update(self, className):
		for x in decaf_program.decafClass:
			x.update(className)
# class to hold methods and fields
class decaf_class:
	def __init__(self, className, superclassName, fields):
		self.className = className
		self.superclassName = superclassName
		self.decafMethods = []
		self.decafFields = []
		self.decafConstructors = []
		for x in fields:
			if(isinstance(x,decaf_class_method)):
				self.decafMethods.append(x)
			elif(isinstance(x,decaf_class_constructor)):
				self.decafConstructors.append(x)
			elif(isinstance(x, list)):
				for l in x:
					self.decafFields.append(l)
			elif(isinstance(x,decaf_class_field)):
				self.decafFields.append(x)
	def print_class(self):
		print "Class Name:",self.className
		print "Superclass Name:",self.superclassName
		print "Fields:"
		for x in self.decafFields:
			print "FIELD ",
			x.print_field()
		print "Constructors:"
		for x in self.decafConstructors:
			x.print_constructor()
		print "Methods:"
		for x in self.decafMethods:
			x.print_method()
	def update(self, className):
		for x in self.decafFields:
			x.update_fields(className)
		for x in self.decafMethods:
			x.update_method(className)
class decaf_class_field:
	def __init__(self, fieldName, fieldId, className, visibility, applicability, vartype):
		self.fieldName = fieldName
		self.fieldId = fieldId
		self.className = className
		self.visibility = visibility
		self.applicability = applicability
		self.type = vartype
	def print_field(self):
		print self.fieldId, ",", self.fieldName, ",", \
			  self.className, "," , self.visibility, ",", \
			  self.applicability, "," , self.type.type_record
	def update_fields(self, className):
		self.className = className
class decaf_class_method:
	def __init__(self, methodName, methodID, className, visibility, applicability, outermostblock, return_type = None):
		self.methodName = methodName
		self.methodID = methodID
		self.className = className
		self.visibility = visibility
		self.applicability = applicability
		self.variableTable = []
		self.block = outermostblock
		self.return_type = return_type
		self.variableID = 1
		#self.type = decaf_class_type(field_type)
	def print_method(self):
		print "METHOD:",self.methodID, ",", self.methodName, ",", \
			  self.className, ",", self.visibility, ",", \
			  self.applicability,
		if self.return_type != None:
			print ",",
			self.return_type.print_type()
		print
		print "Method Parameters:"
		print "Variable Table:"
		if self.variableTable:
			for index, x in enumerate(self.variableTable):
				if index != len(self.variableTable) - 1:
					x.print_variable()
					print
				else:
					x.print_variable()
			print
		if self.block:
			print "Method Body:"
			self.block.print_block()

	def error_check_duplicate_var(self):
		functionVarTable = []
		if self.variableTable:
			for x in self.variableTable:
				if x:
					functionVarTable.append(x.name)
		if self.block:
			for x in self.block.variableTable:
				if x:
					functionVarTable.append(x.name)
		if len(functionVarTable) != len(set(functionVarTable)):
			print("Formal and Local Variables of the Functions should be distinct"), functionVarTable
			sys.exit(0)
	def update_method(self, className):
		self.className = className
	def update_varList(self, variableList):
		self.variableTable = self.variableTable + variableList
		for x in variableList:
			x.id = self.variableID
			self.variableID = self.variableID + 1
	def update_var(self, variableTable):
		if self.block:
			self.block.update_var(variableTable)
class decaf_type_record:
	def __init__(self, type_record):
		if type_record in ["int", "float", "boolean"]:
			self.type_record = type_record
		else:
			self.type_record = "user(" + type_record + ")"
		self.array_type = False
		self.array_dimensions = None
		self.hierarchy_of_base_type = 0
	def update_type_record_to_array(self, array_dimensions, hierarchy_of_base_type):
		base_type = ""
		for x in range(hierarchy_of_base_type):
			base_type = base_type + "array("
		base_type = base_type + self.type_record
		for x in range(hierarchy_of_base_type):
			base_type = base_type + ")"
		self.array_dimensions = array_dimensions
		self.type_record = base_type
		self.array_type = True
	def print_type(self):
		print self.type_record,
		if self.array_type == True:
			print ",[",
			for x in self.array_dimensions:
				x.print_statement()
				print ","
			print "]",
class decaf_class_constructor:
	def __init__(self, constructor_id, visibility, outermostblock):
		self.constructor_id = constructor_id
		self.visibility = visibility
		self.variableTable = []
		self.block = outermostblock
		self.variableID = 1
	def print_constructor(self):
		print "CONSTRUCTOR:",self.constructor_id, ",", self.visibility
		print "Constructor Parameters:"
		print "Variable Table:"
		if self.variableTable:
			for index, x in enumerate(self.variableTable):
				if index != len(self.variableTable) - 1:
					x.print_variable()
					print
				else:
					x.print_variable()
			print
		if self.block:
			print "Constructor Body:"
			self.block.print_block()
	def error_check_duplicate_var(self):
		functionVarTable = []
		for x in self.variableTable:
			functionVarTable.append(x.name)
		for x in self.block.variableTable:
			functionVarTable.append(x.name)
		if len(functionVarTable) != len(set(functionVarTable)):
			print("Formal and Local Variables of the Constructor should be distinct")
			sys.exit(0)
	def update_varList(self, variableList):
		self.variableTable = self.variableTable + variableList
		for x in variableList:
			x.id = self.variableID
			self.variableID = self.variableID + 1
	def update_var(self, variableTable):
		if self.block:
			self.block.update_var(variableTable)
class decaf_mod:
	def __init__(self, visibility, applicability):
		self.visibility = visibility
		self.applicability = applicability
class decaf_variable:
	def __init__(self, vartype, name, kind):
		self.type = vartype
		self.name = name
		self.kind = kind
		self.id = 0
	def print_variable(self):
		print "VARIABLE", self.id, ",", self.name, ",", self.kind, ",", 
		self.type.print_type()
class decaf_break_statement:
	def __init__(self):
		self.type = "Break"
	def print_statement(self):
		print self.type, ",",
	def update_var(self, variableTable):
		pass
class decaf_continue_statement:
	def __init__(self):
		self.type = "Continue"
	def print_statement(self):
		print self.type, ",",
	def update_var(self, variableTable):
		pass
class decaf_expression_statement:
	def __init__(self, expression):
		self.expression = expression
	def print_statement(self):
		print "Expr(",
		self.expression.print_statement()
		print ")",
	def update_var(self, variableTable):
		self.expression.update_var(variableTable)
class decaf_block_statement:
	def __init__(self, statements=None):
		self.type = "BLOCK"
		self.statements = statements
		self.parentblock = None
		self.childblock = None
		self.variableTable = []
		self.formalParams = None
	def update_var(self, variableTable):
		if variableTable:
			for var in self.variableTable:
				variableTable.append(var)
		else:
			variableTable = self.variableTable
		if self.statements:
			for x in self.statements:
				if x:
					x.update_var(variableTable)
	def print_block(self):
		print self.type, "(["
		if self.statements:
			for index, x in enumerate(self.statements):
				if x:
					if isinstance(x, decaf_block_statement):
						x.print_block()
					elif isinstance(x,decaf_variable_list):
						continue
					else:
						x.print_statement()
				if index != len(self.statements) - 1:
					print "\n, ",
		if not self.statements:
			print "\n])"
		else:
			print "])"
		#print "Printing variables in this block"
		#for p in self.variableTable:
		#	p.print_variable()
	def update_block(self):
		#print "Update Method", self
		if self.statements:
			for x in self.statements:
				if x:
					if isinstance(x, decaf_block_statement):
						x.parentblock = self
						self.childblock = x
					elif isinstance(x,decaf_variable_list):
						self.variableTable = x.varlist
	def error_check_duplicate_var(self):
		functionVarTable = []
		for x in self.variableTable:
			functionVarTable.append(x.name)
		if len(functionVarTable) != len(set(functionVarTable)):
			print("Variables of a Block should be distinct")
			sys.exit(0)

class decaf_constant_expression:
	def __init__(self, expression_type, expression_value):
		self.expression_type = expression_type
		self.expression_value = expression_value
	def print_statement(self):
		print "Constant(",
		if self.expression_type == "int":
			print "Integer-constant(", self.expression_value, "))",
		elif self.expression_type == "float":
			print "Float-constant(", self.expression_value, "))",
		elif self.expression_type == "string":
			print "String-constant(", self.expression_value, "))",
		elif self.expression_type == "boolean":
			print self.expression_value, ")",
		else:
			print "Null)",
	def update_var(self, variableTable):
		pass
class decaf_assign_expression:
	def __init__(self, lhs, rhs):
		self.lhs = lhs
		self.rhs = rhs
	def print_statement(self):
		print "Assign(",
		self.lhs.print_statement()
		print ",",
		self.rhs.print_statement()
		print ")",
	def update_var(self, variableTable):
		self.lhs.update_var(variableTable)
		self.rhs.update_var(variableTable)
class decaf_this_expression:
	def print_statement(self):
		print "This,",
	def update_var(self, variableTable):
		pass
class decaf_super_expression:
	def print_statement(self):
		print "Super,",
	def update_var(self, variableTable):
		pass
class decaf_var_expression:
	def __init__(self, variable):
		self.expression_value = variable
	def print_statement(self):
		print self.expression_value,
	def update_var(self, variableTable):
		pass
class decaf_field_access_expression:
	def __init__(self, variable, primary = None):
		self.variable = variable
		self.primary = primary
		self.type = "Field-access"
	def print_statement(self):
		if self.type != "":
			print self.type, "(",
		if self.primary == None:
			self.variable.print_statement()
		else:
			self.primary.print_statement()
			self.variable.print_statement()
		if self.type != "":
			print ")",
	def update_field_access_expression(self, vartype = ""):
		self.type = vartype
	def update_var(self, variableTable):
		#print "Within field access expression", self.variable.expression_value, " "
		#print "Len is ", len(variableTable), " ",
		#print "Field access primary", self.primary, ",", self.variable.expression_value, " "
		if variableTable:
			found = False
			if self.primary == None:
				for x in reversed(variableTable):
					if x.name == self.variable.expression_value:
						self.update_field_access_expression("Variable(")
						self.variable = decaf_var_expression(x.id)
						found = True
						break
				if found == False:
					self.primary = decaf_this_expression()
		else:
			if self.primary == None:
				self.primary = decaf_this_expression()
		#print
class decaf_method_invocation_expression:
	def __init__(self, primary, method_arguments):
		self.primary = primary
		self.method_arguments = method_arguments
	def print_statement(self):
		print "Method-call(",
		if self.primary:
			self.primary.print_statement()
		print ", [",
		if self.method_arguments:
			for x in self.method_arguments:
				x.print_statement()
				print ",",
		print "])",
	def update_var(self, variableTable):
		#print self.primary.primary, ","
		if self.method_arguments:
			for x in self.method_arguments:
				x.update_var(variableTable)
		if self.primary.primary == None:
			self.primary.primary = decaf_this_expression()

class decaf_binary_expression:
	def __init__(self, expr1, expr2, operator):
		self.expr1 = expr1
		self.expr2 = expr2
		self.operator = operator
	def print_statement(self):
		print "Binary(",
		print self.operator,",",
		self.expr1.print_statement()
		print ",",
		self.expr2.print_statement()
		print ")",
	def update_var(self, variableTable):
		self.expr1.update_var(variableTable)
		self.expr2.update_var(variableTable)
class decaf_unary_expression:
	def __init__(self, expr1, operator):
		self.expr1 = expr1
		self.operator = operator
	def print_statement(self):
		print "Unary(",
		print self.operator,",",
		self.expr1.print_statement()
		print ")",
	def update_var(self, variableTable):
		self.expr1.update_var(variableTable)
class decaf_new_object_expression:
	def __init__(self, base_class_name, arguments_to_constructor):
		self.base_class_name = base_class_name
		self.arguments_to_constructor = arguments_to_constructor
	def print_statement(self):
		print "New-object(", self.base_class_name,
		print ",[",
		if self.arguments_to_constructor:
			for x in self.arguments_to_constructor:
				x.print_statement()
				print ",",
		print "]",
	def update_var(self, variableTable):
		pass
class decaf_if_statement:
        def __init__(self, expression, statement1, statement2 = None):
                self.expression = expression
                self.statement1 = statement1
		self.statement2 = statement2
        def print_statement(self):
                print "if",
                if self.expression:
                        print "(",
                        self.expression.print_statement()
                        print ")"
                if self.statement1:
			print "then",
                        self.statement1.print_statement()
		if self.statement2:
			print "else",
			self.statement2.print_statement()
		else:
			print "Skip"
	def update_var(self, variableTable):
		self.expression.update_var(variableTable)
		self.statement1.update_var(variableTable)
		if self.statement2:
			self.statement2.update_var(variableTable)
class decaf_while_statement:
	def __init__(self, expression, statement):
		self.expression = expression
		self.statement = statement
	def print_statement(self):
		print "While",
		if self.expression:
			print "(",
			self.expression.print_statement()
			print ")"
		if self.statement:
			self.statement.print_statement()
	def update_var(self, variableTable):
		self.expression.update_var(variableTable)
		self.statement.update_var(variableTable)

class decaf_for_statement:
	def __init__(self, statement, expression1 = None, expression2 = None, expression3 = None):
		self.expression1 = expression1
		self.expression2 = expression2
		self.expression3 = expression3
		self.statement = statement
	def print_statement(self):
		print "For",
		print "(",
		if self.expression1:
			self.expression1.print_statement()
		print ";",
		if self.expression2:
			self.expression2.print_statement()
		print ";",
		if self.expression3:
			self.expression3.print_statement()
		print ")"
		if self.statement:
			self.statement.print_statement()

	def update_var(self, variableTable):
		self.statement.update_var(variableTable)
		if self.expression1:
			self.expression1.update_var(variableTable)
		if self.expression2:
			self.expression2.update_var(variableTable)
		if self.expression3:
			self.expression3.update_var(variableTable)
class decaf_return_statement:
	def __init__(self, expression = None):
		self.expression = expression
	def print_statement(self):
		print "Return",
		if self.expression:
			print "(",
			self.expression.print_statement()
			print ")"
	def update_var(self, variableTable):
		self.expression.update_var(variableTable)
class decaf_auto_expression:
	def __init__(self, variable, inc_dec, post_pre):
		self.variable = variable
		self.inc_dec = inc_dec
		self.post_pre = post_pre
	def print_statement(self):
		print "Auto(",
		self.variable.print_statement()
		print self.inc_dec, ",", self.post_pre, ")",
	def update_var(self, variableTable):
		self.variable.update_var(variableTable)
class decaf_array_access_expression:
	def __init__(self, base_type, index):
		self.base_type = base_type
		self.index = index
	def print_statement(self):
		print "Array-access(",
		self.base_type.print_statement()
		print ",",
		self.index.print_statement()
		print ")",
	def update_var(self, variableTable):
		self.base_type.update_var(variableTable)
class decaf_new_array_expression:
	def __init__(self, type_record):
		self.type_record = type_record
	def print_statement(self):
		print "New-array(",
		self.type_record.print_type()
		print ")",
	def update_var(self, variableTable):
		pass
class decaf_variable_list:
	def __init__(self, varlist):
		self.varlist = varlist
	def update_var(self, variableTable):
		pass
