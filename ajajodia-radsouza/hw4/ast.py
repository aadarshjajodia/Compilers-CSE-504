classtable = {}  # initially empty dictionary of classes.
lastmethod = 0
lastconstructor = 0
current_class = None
from itertools import groupby
# Class table.  Only user-defined classes are placed in the class table.
def lookup(table, key):
    if key in table:
        return table[key]
    else:
        return None

def addtotable(table, key, value):
    table[key] = value


def print_ast():
    for cid in classtable:
        c = classtable[cid]
        c.printout()
    print "-----------------------------------------------------------------------------"
    
def type_check():
    flag = True
    for cid in classtable:
        c = classtable[cid]
        global current_class
        current_class = c
        if c.type_check() == False:
            flag = False
    return flag

def initialize_ast():
    # define In class:
    cin = Class("In", None)
    cin.builtin = True     # this is a builtin class
    cout = Class("Out", None)
    cout.builtin = True     # this, too, is a builtin class

    scanint = Method('scan_int', cin, 'public', 'static', Type('int'))
    scanint.update_body(SkipStmt(None))    # No line number information for the empty body
    cin.add_method(scanint)
    
    scanfloat = Method('scan_float', cin, 'public', 'static', Type('float'))
    scanfloat.update_body(SkipStmt(None))    # No line number information for the empty body
    cin.add_method(scanfloat)

    printint = Method('print', cout, 'public', 'static', Type('void'))
    printint.update_body(SkipStmt(None))    # No line number information for the empty body
    printint.add_var('i', 'formal', Type('int'))   # single integer formal parameter
    cout.add_method(printint)
    
    printfloat = Method('print', cout, 'public', 'static', Type('void'))
    printfloat.update_body(SkipStmt(None))    # No line number information for the empty body
    printfloat.add_var('f', 'formal', Type('float'))   # single float formal parameter
    cout.add_method(printfloat)
    
    printboolean = Method('print', cout, 'public', 'static', Type('void'))
    printboolean.update_body(SkipStmt(None))    # No line number information for the empty body
    printboolean.add_var('b', 'formal', Type('boolean'))   # single boolean formal parameter
    cout.add_method(printboolean)
    
    printstring = Method('print', cout, 'public', 'static', Type('void'))
    printstring.update_body(SkipStmt(None))    # No line number information for the empty body
    printstring.add_var('b', 'formal', Type('string'))   # single string formal parameter
    cout.add_method(printstring)

    addtotable(classtable, "In", cin)
    addtotable(classtable, "Out", cout)


class Class:
    """A class encoding Classes in Decaf"""
    def __init__(self, classname, superclass):
        self.name = classname
        self.superclass = superclass
        self.fields = {}  # dictionary, keyed by field name
        self.constructors = []
        self.methods = []
        self.builtin = False

    def printout(self):
        if (self.builtin):
            return     # Do not print builtin methods
        
        print "-----------------------------------------------------------------------------"
        print "Class Name: {0}".format(self.name)
        sc = self.superclass
        if (sc == None):
            scname = ""
        else:
            scname = sc.name
        print "Superclass Name: {0}".format(scname)
        print "Fields:"
        for f in self.fields:
            (self.fields[f]).printout()
        print "Constructors:"
        for k in self.constructors:
            k.printout()
        print "Methods:"
        for m in self.methods:
            m.printout()
    def type_check(self):
        flag = True
        for m in self.methods:
            if m.type_check() == False:
                flag = False
        for m in self.constructors:
            if m.type_check() == False:
                flag = False
        return flag
    def add_field(self, fname, field):
        self.fields[fname] = field
    def add_constructor(self, constr):
        self.constructors.append(constr)
    def add_method(self, method):
        self.methods.append(method)

    def lookup_field(self, fname):
        return lookup(self.fields, fname)

    def lookup_method(self, mname, passedArguments, base):
        resolved_method = []
        for method in self.methods:
            formal_params = method.vars.formal_params
            if mname == method.name and len(passedArguments) == len(formal_params):
                is_method_candidate_resolved = True
                count = 0
                for x in range(0,len(passedArguments)):
                    if (passedArguments[x].type.is_subtype(formal_params[x].type) == False):
                        is_method_candidate_resolved = False
                    if (passedArguments[x].type.is_strict_type(formal_params[x].type) == True):
                        count = count + 1
                if is_method_candidate_resolved == True:
                    methodTuple = (method, count)
                    if (isinstance(base, ClassReferenceExpr)):
                        if method.storage == 'instance':
                            continue
                    elif(base.type.typename != method.inclass.name):
                        if method.storage == 'static':
                            continue
                    if(current_class.name != method.inclass.name and method.visibility == 'private'):
                        continue
                    else:
                        resolved_method.append(methodTuple)

        resolved_method.sort(key=lambda x: x[1], reverse=True)
        groups = []
        for k, v in groupby(resolved_method, lambda x: x[1]):
            groups.append(list(v))
        if groups:
            if len(groups[0]) == 1:
                return groups[0]
        return resolved_method

    def lookup_constructor(self, passedArguments):
        resolved_constructor = []
        for constructor in self.constructors:
            formal_params = constructor.vars.formal_params
            if len(passedArguments) == len(formal_params):
                is_constructor_candidate_resolved = True
                count = 0
                for x in range(0,len(passedArguments)):
                    if (passedArguments[x].type.is_subtype(formal_params[x].type) == False):
                        is_constructor_candidate_resolved = False
                    if (passedArguments[x].type.is_strict_type(formal_params[x].type) == True):
                        count = count + 1
                if is_constructor_candidate_resolved == True:
                    constructorTuple = (constructor, count)
                    if current_class.name != constructor.name:
                        if constructor.visibility == 'public':
                            resolved_constructor.append(constructorTuple)
                    else:
                        resolved_constructor.append(constructorTuple)
        resolved_constructor.sort(key=lambda x: x[1], reverse=True)
        groups = []
        for k, v in groupby(resolved_constructor, lambda x: x[1]):
            groups.append(list(v))
        if groups:
            if len(groups[0]) == 1:
                return groups[0]
        return resolved_constructor
class Type:
    """A class encoding Types in Decaf"""
    def __init__(self, basetype, params=None, classReferenceExpr=False):
        if ((params == None) or (params == 0)):
            if (basetype in ['int', 'boolean', 'float', 'string', 'void', 'null', 'error']):
                self.kind = 'basic'
                self.typename = basetype
            elif (isinstance(basetype, Type)):
                self.kind = basetype.kind
                self.typename = basetype.typename
            elif classReferenceExpr == True:
                self.kind = 'class-literal'
                self.typename = basetype
            else:
                self.kind = 'user'
                self.typename = basetype
        else:
            bt = Type(basetype, params-1)
            self.kind = 'array'
            self.basetype = bt
            self.typename = self.kind

    def __str__(self):
        if (self.kind == 'array'):
            return 'array(%s)'%(self.basetype.__str__())
        elif (self.kind == 'class-literal' or self.kind == 'user'):
            return self.kind + '(%s)'%(self.typename)
        else:
            return self.typename

    def __repr(self):
        return self.__str__()

    def is_subtype(self, lhs):
	if self.typename == 'null':
            if lhs.kind == 'user' or lhs.kind == 'array':
                return True
        if self.kind == 'array':
	    if lhs.typename == 'null':
		return True		
            if lhs.kind is not self.kind:
                return False
            if self.basetype and lhs.basetype:
                return self.basetype.is_subtype(lhs.basetype)
        if self.typename == lhs.typename:
            return True
        if lhs.typename == 'float' and self.typename == 'int':
            return True
        if (lhs.kind == 'user' and self.kind == 'user') or (lhs.kind == 'class-literal' and self.kind == 'class-literal'):
            temp_class = lhs.typename
            resolved_class = lookup(classtable, temp_class)
            while resolved_class != None and resolved_class.superclass:
                if resolved_class.superclass.name == self.typename:
                    return True
                else:
                    resolved_class = lookup(classtable, resolved_class.superclass.name)
            return False
        if self.typename == 'null':
            if lhs.kind == 'user':
                return True
        return False
    def is_strict_type(self, lhs):
        if self.typename == lhs.typename:
            return True
class Field:
    """A class encoding fields and their attributes in Decaf"""
    lastfield = 0
    def __init__(self, fname, fclass, visibility, storage, ftype):
        Field.lastfield += 1
        self.name = fname
        self.id = Field.lastfield
        self.inclass = fclass
        self.visibility = visibility
        self.storage = storage
        self.type = ftype

    def printout(self):
        print "FIELD {0}, {1}, {2}, {3}, {4}, {5}".format(self.id, self.name, self.inclass.name, self.visibility, self.storage, self.type)

class Method:
    """A class encoding methods and their attributes in Decaf"""
    def __init__(self, mname, mclass, visibility, storage, rtype):
        global lastmethod
        self.name = mname
        lastmethod += 1
        self.id = lastmethod
        self.inclass = mclass
        self.visibility = visibility
        self.storage = storage
        self.rtype = rtype
        self.vars = VarTable()
        
    def update_body(self, body):
        self.body = body

    def add_var(self, vname, vkind, vtype):
        self.vars.add_var(vname, vkind, vtype)

    def printout(self):
        print "METHOD: {0}, {1}, {2}, {3}, {4}, {5}".format(self.id, self.name, self.inclass.name, self.visibility, self.storage, self.rtype)
        print "Method Parameters:",
        print ', '.join(["%d"%i for i in self.vars.get_params()])
        self.vars.printout()
        print "Method Body:"
        self.body.printout()

    def type_check(self):
        return self.body.type_check()

class Constructor:
    """A class encoding constructors and their attributes in Decaf"""
    def __init__(self, cname, visibility):
        global lastconstructor
        self.name = cname
        lastconstructor += 1
        self.id = lastconstructor
        self.visibility = visibility
        self.vars = VarTable()
        
    def update_body(self, body):
        self.body = body

    def add_var(self, vname, vkind, vtype):
        self.vars.add_var(vname, vkind, vtype)

    def printout(self):
        print "CONSTRUCTOR: {0}, {1}".format(self.id, self.visibility)
        print "Constructor Parameters:",
        print ', '.join(["%d"%i for i in self.vars.get_params()])
        self.vars.printout()
        print "Constructor Body:"
        self.body.printout()
        
    def type_check(self):
        return self.body.type_check()

class VarTable:
    """ Table of variables in each method/constructor"""
    def __init__(self):
        self.vars = {0:{}}
        self.lastvar = 0
        self.lastblock = 0
        self.levels = [0]
        self.formal_params = []
    def enter_block(self):
        self.lastblock += 1
        self.levels.insert(0, self.lastblock)
        self.vars[self.lastblock] = {}

    def leave_block(self):
        self.levels = self.levels[1:]
        # where should we check if we can indeed leave the block?

    def add_var(self, vname, vkind, vtype):
        self.lastvar += 1
        c = self.levels[0]   # current block number
        v = Variable(vname, self.lastvar, vkind, vtype)
        if vkind == 'formal':
            self.formal_params.append(v)
        vbl = self.vars[c]  # list of variables in current block
        vbl[vname] = v
    
    def _find_in_block(self, vname, b):
        if (b in self.vars):
            # block exists
            if (vname in self.vars[b]):
                return self.vars[b][vname]
        # Otherwise, either block b does not exist, or vname is not in block b
        return None

    def find_in_current_block(self, vname):
        return self._find_in_block(vname, self.levels[0])

    def find_in_scope(self, vname):
        for b in self.levels:
            v = self._find_in_block(vname, b)
            if (v != None):
                return v
            # otherwise, locate in enclosing block until we run out
        return None

    def get_params(self):
        outermost = self.vars[0]  # 0 is the outermost block
        ids = [outermost[vname].id for vname in outermost if outermost[vname].kind=='formal']
        return ids

    def printout(self):
        print "Variable Table:"
        for b in range(self.lastblock+1):
            for vname in self.vars[b]:
                v = self.vars[b][vname]
                v.printout()
        

class Variable:
    """ Record for a single variable"""
    def __init__(self, vname, id, vkind, vtype):
        self.name = vname
        self.id = id
        self.kind = vkind
        self.type = vtype

    def printout(self):
        print "VARIABLE {0}, {1}, {2}, {3}".format(self.id, self.name, self.kind, self.type)
    

class Stmt(object): 
    """ Top-level (abstract) class representing all statements"""

class IfStmt(Stmt):
    def __init__(self, condition, thenpart, elsepart, lines):
        self.lines = lines
        self.condition = condition
        self.thenpart = thenpart
        self.elsepart = elsepart
    def printout(self):
        print "If(",
        self.condition.printout()
        print ", ",
        self.thenpart.printout()
        print ", ",
        self.elsepart.printout()
        print ")"
    def type_check(self):
        if self.condition.type_check() == True:
            if self.condition.type.typename == "boolean":
                if self.thenpart.type_check() == True:
                    if self.elsepart.type_check() == True:
                            return True
                    else:
                        print "Type error at line", self.lines, "Else Part of If statement is not type correct"
                else:
                    print "Type error at line", self.lines, "Then Part of If statement is not type correct"
            else:
                print "Type error at line", self.lines, "Condition Part of If statement should be of type boolean"
        return False

class WhileStmt(Stmt):
    def __init__(self, cond, body, lines):
        self.lines = lines
        self.cond = cond
        self.body = body
    def printout(self):
        print "While(",
        self.cond.printout()
        print ", ",
        self.body.printout()
        print ")"
    def type_check(self):
        if self.cond.type_check() == True:
            if self.cond.type.typename == "boolean":
                if self.body.type_check() == True:
                    return True
                else:
                    print "Type error at line", self.lines, "While Statement Body is not Type Correct"
            else:
                print "Type error at line", self.lines, "Condition Part of While statement should be of type boolean"
        return False
class ForStmt(Stmt):
    def __init__(self, init, cond, update, body, lines):
        self.lines = lines
        self.init = init
        self.cond = cond
        self.update = update
        self.body = body
    def printout(self):
        print "For(",
        if (self.init != None):
            self.init.printout()
        print ", ",
        if (self.cond != None):
            self.cond.printout()
        print ", ",
        if (self.update != None):
            self.update.printout()
        print ", ",
        self.body.printout()
        print ")"
    def type_check(self):
        if self.cond:
            if self.cond.type_check() == True:
                if self.cond.type.typename == "boolean":
                    if self.init.type_check() == True and self.update.type_check() and self.body.type_check() == True:
                        return True
                else:
                    print "Type error at line", self.lines, "Condition Part of For statement should be of type boolean"
        else:
            if self.init.type_check() == True and self.update.type_check() and self.body.type_check() == True:
                return True
        return False

class ReturnStmt(Stmt):
    def __init__(self, expr, lines):
        self.lines = lines
        self.expr = expr

    def printout(self):
        print "Return(",
        if (self.expr != None):
            self.expr.printout()
        print ")"
    def populate_current_method_return_type(self, current_method_return_type):
        self.current_method_return_type = current_method_return_type
    def type_check(self):
        if self.expr == None:
            if self.current_method_return_type.typename == 'void':
                return True
            else:
                print "Type error at line", self.lines, "{0} return type is not compatible".format(self.current_method_return_type)
                return False
        elif self.expr.type_check() == True:
            if self.expr.type.is_subtype(self.current_method_return_type):
                return True
            else:
                print "Type error at line", self.lines, "{0} return type is not compatible with {1}".format(self.current_method_return_type, self.expr.type)
                return False
        return False
class BlockStmt(Stmt):
    def __init__(self, stmtlist, lines):
        self.lines = lines
        self.stmtlist = [s for s in stmtlist if (s != None) and (not isinstance(s, SkipStmt))]

    def printout(self):
        print "Block(["
        if (len(self.stmtlist) > 0):
            self.stmtlist[0].printout()
        for s in self.stmtlist[1:]:
            print ", ",
            s.printout()
        print "])"
    def type_check(self):
        flag = True
        for p in self.stmtlist:
            if p.type_check() == False:
                flag = False
        return flag
class BreakStmt(Stmt):
    def __init__(self, lines):
        self.lines = lines

    def printout(self):
        print "Break"

    def type_check(self):
        return True

class ContinueStmt(Stmt):
    def __init__(self, lines):
        self.lines = lines

    def printout(self):
        print "Continue"

    def type_check(self):
        return True

class ExprStmt(Stmt):
    def __init__(self, expr, lines):
        self.lines = lines
        self.expr = expr
    def printout(self):
        print "Expr(",
        self.expr.printout()
        print ")"
    def type_check(self):
        return self.expr.type_check()

class SkipStmt(Stmt):
    def __init__(self, lines):
        self.lines = lines

    def printout(self):
        print "Skip"

    def type_check(self):
        return True

class Expr(object):
    def __repr__(self):
        return "Unknown expression"
    def printout(self):
        print self, 


class ConstantExpr(Expr):
    def __init__(self, kind, arg=None, lines=None):
        self.lines = lines
        self.kind = kind
        if (kind=='int'):
            self.int = arg
        elif (kind == 'float'):
            self.float = arg
        elif (kind == 'string'):
            self.string = arg
 
    def __repr__(self):
        s = "Unknown"
        if (self.kind == 'int'):
            s = "Integer-constant(%d)"%self.int
        elif (self.kind == 'float'):
            s = "Float-constant(%g)"%self.float
        elif (self.kind == 'string'):
            s = "String-constant(%s)"%self.string
        elif (self.kind == 'null'):
            s = "null"
        elif (self.kind == 'True'):
            s = "True"
        elif (self.kind == 'False'):
            s = "False"
        return "Constant({0})".format(s)

    def populate_type(self):
        if (self.kind=='int'):
            self.type = Type('int')
        elif (self.kind == 'float'):
            self.type = Type('float')
        elif (self.kind == 'string'):
            self.type = Type('string')
        elif (self.kind == 'True' or self.kind == 'False'):
            self.type = Type('boolean')
        elif (self.kind == 'null'):
            self.type = Type('null')
        else:
            self.type = Type('error')
    def type_check(self):
        self.populate_type()
        if self.type.typename == "error":
            return False
        else:
            return True
class VarExpr(Expr):
    def __init__(self, var, lines):
        self.lines = lines
        self.var = var
        self.populate_type()
    def __repr__(self):
        return "Variable(%d)"%self.var.id
    def populate_type(self):
        self.type = self.var.type
    def type_check(self):
        self.populate_type()
        if self.type.typename == "error":
            return False
        else:
            return True
class UnaryExpr(Expr):
    def __init__(self, uop, expr, lines):
        self.lines = lines
        self.uop = uop
        self.arg = expr
        #self.type = self.populate_type()
    def __repr__(self):
        return "Unary({0}, {1})".format(self.uop, self.arg)
    def populate_type(self):
        if self.uop == 'uminus':
            if self.arg.type == 'int' or self.arg.type == 'float':
                self.type = self.arg.type
            else:
                print "Type error at line", self.lines, "Unexpected type {0} in unary expression, expected int or float".format(self.arg.type)
                self.type = Type('error')
        elif self.uop == 'neg':
            if self.arg.type == 'boolean':
                self.type = self.arg.type
            else:
                print "Type error at line", self.lines, "Unexpected type {0} in unary expression, expected boolean".format(self.arg.type)
                self.type = Type('error')
        else:
            self.type = Type('error')
    def type_check(self):
        self.populate_type()
        if self.type.typename == "error":
            return False
        else:
            return True
class BinaryExpr(Expr):
    def __init__(self, bop, arg1, arg2, lines):
        self.lines = lines
        self.bop = bop
        self.arg1 = arg1
        self.arg2 = arg2
    def __repr__(self):
        return "Binary({0}, {1}, {2})".format(self.bop,self.arg1,self.arg2)
    def populate_type(self):
        self.arg1.type_check()
        self.arg2.type_check()
        if self.bop in ['add', 'sub', 'div', 'mul']:
            if self.arg1.type.typename == 'int' and self.arg2.type.typename == 'int':
                self.type = Type('int')
            elif self.arg1.type.typename == 'int' and self.arg2.type.typename == 'float':
                self.type = Type('float')
            elif self.arg1.type.typename == 'float' and self.arg2.type.typename == 'int':
                self.type = Type('float')
            elif self.arg1.type.typename == 'float' and self.arg2.type.typename == 'float':
                self.type = Type('float')
            else:
                print "Type error at line", self.lines, "Type mismatch in binary expression"
                self.type = Type('error')
        elif self.bop in ['and', 'or']:
            if self.arg1.type.typename == 'boolean' and self.arg2.type.typename == 'boolean':
                self.type = Type('boolean')
            else:
                print "Type error at line", self.lines, "Type mismatch in binary expression"
                self.type = Type('error')
        elif self.bop in ['lt', 'leq', 'gt', 'geq']:
            if self.arg1.type.typename == 'int' and self.arg2.type.typename == 'int':
                self.type = Type('boolean')
            elif self.arg1.type.typename == 'float' and self.arg2.type.typename == 'float':
                self.type = Type('boolean')
            else:
                print "Type error at line", self.lines, "Type mismatch in binary expression"
                self.type = Type('error')
        elif self.bop in ['eq', 'neq']:
            if self.arg1.type.is_subtype(self.arg2.type) or self.arg2.type.is_subtype(self.arg1.type):
                self.type = Type('boolean')
            else:
                print "Type error at line", self.lines, "Type mismatch in binary expression"
                self.type = Type('error')
        else:
            self.type = Type('error')
    def type_check(self):
        self.populate_type()
        if self.type.typename == "error":
            print "Type error at line", self.lines, "{0} operation on {1} and {2} is not compatible".format(self.bop, self.arg1.type, self.arg2.type)
            return False
        else:
            return True
class AssignExpr(Expr):
    def __init__(self, lhs, rhs, lines):
        self.lines = lines
        self.lhs = lhs
        self.rhs = rhs
        self.type = None
    def __repr__(self):
        return "Assign({0}, {1}, {2}, {3})".format(self.lhs, self.rhs, self.type_lhs, self.type_rhs)
    def type_check(self):
        self.lhs.type_check();
        self.type_lhs = self.lhs.type
        self.rhs.type_check();
        self.type_rhs = self.rhs.type
        if self.type_lhs.typename == "error":
            print "Type error at line", self.lines, "lhs is not type correct"
            self.type = Type('error')
            return False
        elif self.type_rhs.typename == "error":
            print "Type error at line", self.lines, "rhs is not type correct"
            self.type = Type('error')
            return False
        elif self.type_rhs.is_subtype(self.type_lhs) == False:
            print "Type error at line", self.lines, self.type_rhs.typename, "expression found when", \
                                self.type_lhs.typename, "is expected"
            self.type = Type('error')
            return False
        else:
            self.type = self.type_rhs
            return True

class AutoExpr(Expr):
    def __init__(self, arg, oper, when, lines):
        self.lines = lines
        self.arg = arg
        self.oper = oper
        self.when = when
        self.type = None
    def __repr__(self):
        return "Auto({0}, {1}, {2})".format(self.arg, self.oper, self.when)
    def populate_type(self):
        self.arg.populate_type()
        if self.arg.type.typename == 'int' or self.arg.type.typename == 'float':
            self.type = self.arg.type
        else:
            print 'Type error at line', self.lines, '{0} is not an auto expression, should be either int/float'.format(self.arg.type)
            self.type = Type('error')
    def type_check(self):
        self.populate_type();
        if self.type.typename == "error":
            return False
        else:
            return True
class FieldAccessExpr(Expr):
    def __init__(self, base, fname, lines):
        self.lines = lines
        self.base = base
        self.fname = fname
        self.resolvedId = None
        self.type = None
    def __repr__(self):
        return "Field-access({0}, {1}, {2})".format(self.base, self.fname, self.resolvedId)
    def populate_type(self):
        if self.base.type_check() == False:
            self.type = Type('error')
            return
        resolved_class = lookup(classtable, self.base.type.typename)

        field = resolved_class.lookup_field(self.fname)
        while(field == None and resolved_class.superclass != None):
            resolved_class = resolved_class.superclass
            field = resolved_class.lookup_field(self.fname)

        if field == None:
            print 'Type error at line', self.lines, 'Field "{0}" is not defined'.format(self.fname)
            self.type = Type('error')
            return
        elif (isinstance(self.base, ClassReferenceExpr)):
            if field.storage == 'instance':
                print 'Type error at line', self.lines, 'Field "{0}" is non-static'.format(self.fname)
                self.type = Type('error')
                return
        elif(self.base.type.typename != resolved_class.name):
            if field.storage == 'static':
                print 'Type error at line', self.lines, 'Field "{0}" is static'.format(self.fname)
                self.type = Type('error')
                return

        if(current_class.name != resolved_class.name and field.visibility == 'private'):
            print 'Type error at line', self.lines, 'Field "{0}" is declared private, unable to access'.format(self.fname)
            self.type = Type('error')
            return
        if (self.type == None):
            self.type = field.type
            self.resolvedId = field.id
    def type_check(self):
        self.populate_type()
        if self.type.typename == "error":
            return False
        else:
            return True
class MethodInvocationExpr(Expr):
    def __init__(self, field, args, lines):
        self.lines = lines
        self.base = field.base
        self.mname = field.fname
        self.args = args
    def __repr__(self):
        return "Method-call({0}, {1}, {2}, {3})".format(self.base, self.mname, self.args, self.resolvedId)
    def populate_type(self):
        if self.base.type_check() == False:
            self.type = Type('error')
            return
        for x in self.args:
            if (x.type_check() == False):
                print "Type error at line", self.lines, "argument {0} of method is not type compatible".format(x)
                self.type = Type('error')
                return

        resolved_class = lookup(classtable, self.base.type.typename)
        resolved_method = resolved_class.lookup_method(self.mname, self.args, self.base)
        if(len(resolved_method) > 1):
            print "Type error at line", self.lines, "Unable to resolve the method call, more than one method declarations match this call"
            self.type = Type('error')
            return
        if(len(resolved_method) == 1):
            #print self.base.base.type
            resolved_method = resolved_method[0][0]
            self.type = resolved_method.rtype
            self.resolvedId = resolved_method.id
            return

        while(len(resolved_method) == 0 and resolved_class.superclass != None):
            resolved_class = resolved_class.superclass
            resolved_method = resolved_class.lookup_method(self.mname, self.args, self.base)
            if(len(resolved_method) > 1):
                print "Type error at line", self.lines, "Unable to resolve the method call, more than one method declarations match this call in the superclass"
                self.type = Type('error')
                return
            elif(len(resolved_method) == 1):
                resolved_method = resolved_method[0][0]
                self.type = resolved_method.rtype
                self.resolvedId = resolved_method.id
                return
        print "Type error at line", self.lines, "Unable to resolve the method call, either the function is private or calling a static method from a user() object or calling a non-static method from a class-literal()"
        self.type = Type('error')
    def type_check(self):
        self.populate_type()
        if self.type.typename == "error":
            return False
        else:
            return True
class NewObjectExpr(Expr):
    def __init__(self, cref, args, lines):
        self.lines = lines
        self.classref = cref
        self.args = args
    def __repr__(self):
        return "New-object({0}, {1}, {2})".format(self.classref.name, self.args, self.resolvedId)
    def populate_type(self):
        for x in self.args:
            if (x.type_check() == False):
                print "Type error at line", self.lines, "argument {0} of constructor is not type compatible".format(x)
                self.type = Type('error')
                return

        resolved_class = self.classref
        resolved_constructor = resolved_class.lookup_constructor(self.args)
        if(len(resolved_constructor) > 1):
            print "Type error at line", self.lines, "Unable to resolve the constructor call, more than one constructor match found"
            self.type = Type('error')
            return
        if(len(resolved_constructor) == 1):
            #print self.base.base.type
            resolved_constructor = resolved_constructor[0][0]
            self.type = Type(self.classref.name)
            self.resolvedId = resolved_constructor.id
            return
        print "Type error at line", self.lines, "No matching constructor for new object creation, or the constructor is private"
        self.type = Type('error')
    def type_check(self):
        self.populate_type()
        if self.type.typename == "error":
            return False
        else:
            return True
class ThisExpr(Expr):
    def __init__(self, lines):
        self.lines = lines
    def __repr__(self):
        return "This"
    def populate_type(self):
        self.type = Type(current_class.name)
    def type_check(self):
        self.populate_type();
        return True
class SuperExpr(Expr):
    def __init__(self, lines):
        self.lines = lines
    def __repr__(self):
        return "Super"
    def populate_type(self):
        if current_class.superclass != None:
            self.type = Type(current_class.superclass.name)
        else:
            print "Type error at line", self.lines, "class {0} has no superclass".format(current_class.name)
            self.type = Type('error')
    def type_check(self):
        self.populate_type()
        if self.type.typename == "error":
            return False
        else:
            return True
class ClassReferenceExpr(Expr):
    def __init__(self, cref, lines):
        self.lines = lines
        self.classref = cref
    def __repr__(self):
        return "ClassReference({0})".format(self.classref.name)
    def populate_type(self):
        self.type = Type(self.classref.name, 0, True)
    def type_check(self):
        self.populate_type();
        return True
class ArrayAccessExpr(Expr):
    def __init__(self, base, index, lines):
        self.lines = lines
        self.base = base
        self.index = index
    def __repr__(self):
        return "Array-access({0}, {1})".format(self.base, self.index)
    def populate_type(self):
        basetype_temp = self
        count = 0
        while(isinstance(basetype_temp, ArrayAccessExpr)):
            basetype_temp.index.type_check()
            if basetype_temp.index.type.typename != 'int':
                print "Type error at line", self.lines, "array indexes must be an integer"
                self.type = Type('error')
                return
            basetype_temp = basetype_temp.base
            count += 1
        basetype_temp.type_check()
        basetype_array = basetype_temp.type
        while basetype_array.kind == 'array':
            basetype_array = basetype_array.basetype
            count -= 1
        if count:
            print "Type error at line", self.lines, "array dimensions don't match, array access should have same dimensions"
            self.type = Type('error')
            return
        self.type = Type(basetype_array)
    def type_check(self):
        self.populate_type()
        if self.type.typename == "error":
            return False
        else:
            return True
class NewArrayExpr(Expr):
    def __init__(self, basetype, args, lines):
        self.lines = lines
        self.basetype = basetype
        self.args = args
    def __repr__(self):
        return "New-array({0}, {1})".format(self.basetype, self.args)
    def populate_type(self):
        count = 0
        basetype_temp = self.basetype
        while(isinstance(basetype_temp, Type)):
            if hasattr(basetype_temp, "basetype"):
                count = count + 1;
                basetype_temp = basetype_temp.basetype
            else:
                break
        if self.args:
            for x in self.args:
                x.type_check()
                if x.type.typename != 'int':
                    print "Type error at line", self.lines, "array dimensions must be an integer"
                    self.type = Type('error')
                    return
        self.type = Type(basetype_temp, count + len(self.args))

    def type_check(self):
        self.populate_type()
        if self.type.typename == "error":
            return False
        else:
            return True 