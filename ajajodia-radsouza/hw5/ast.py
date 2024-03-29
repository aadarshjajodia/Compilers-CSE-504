classtable = {}  # initially empty dictionary of classes.
lastmethod = 0
lastconstructor = 0
staticfieldcount = 0
temporaryregisternumber = 0
argumentregisternumber = 0
amifile = None
autoexprmap = {}
autoexprmap["inc"] = "add"
autoexprmap["dec"] = "sub"
labelnumber = 0
breakstatementlabel = None
continuestatementlabel = None
newobjectexpressionregsiter = None

import sys
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

def typecheck():
    global errorflag
    errorflag = False
    # add default constructors to all classes first!
    for cid in classtable:
        c = classtable[cid]
        if not c.builtin:
            c.add_default_constructor()
    for cid in classtable:
        c = classtable[cid]
        c.typecheck()
    return not errorflag

def generate_code():
    global amifile
    amifile = open("input.ami", "w")
    amifile.write(".static_data {0}\n".format(staticfieldcount))
    for cid in classtable:
        c = classtable[cid]
        c.generate_code()

def get_new_temporary_register():
    global temporaryregisternumber
    r1 = "t" + str(temporaryregisternumber)
    temporaryregisternumber = temporaryregisternumber + 1
    return r1

def get_new_instruction_label():
    global labelnumber
    label = "L" + str(labelnumber)
    labelnumber = labelnumber + 1
    return label

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
        if self.superclass:
            self.fieldindex = self.superclass.fieldindex
        else:
            self.fieldindex = 0
    def printout(self):
        if (self.builtin):
            return     # Do not print builtin classes
        
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

    def typecheck(self):
        global current_class
        if (self.builtin):
            return     # Do not type check builtin classes

        current_class = self

        # First check if there are overlapping overloaded constructors and methods
        n = len(self.constructors)
        for i in range(0,n):
            for j in range(i+1, n):
                at1 = self.constructors[i].argtypes()
                at2 = self.constructors[j].argtypes()
                if (not subtype_or_incompatible(at1, at2)):
                    t1 = ",".join([str(t) for t in at1])
                    t2 = ",".join([str(t) for t in at2])
                    signal_type_error("Overlapping types in overloaded constructors: `{0}' (line {2}) and `{1}'".format(t1,t2, self.constructors[i].body.lines), self.constructors[j].body.lines)

        n = len(self.methods)
        for i in range(0,n):
            for j in range(i+1, n):
                if (self.methods[i].name != self.methods[j].name):
                    # Check only overloaded methods
                    break
                at1 = self.methods[i].argtypes()
                at2 = self.methods[j].argtypes()
                if (not subtype_or_incompatible(at1, at2)):
                    t1 = ",".join([str(t) for t in at1])
                    t2 = ",".join([str(t) for t in at2])
                    signal_type_error("Overlapping types in overloaded methods: `{0}' (line {2}) and `{1}'".format(t1,t2, self.methods[i].body.lines), self.methods[j].body.lines)

        for k in self.constructors:
            k.typecheck()
            # ensure it does not have a return statement
            if (k.body.has_return() > 0):
                signal_type_error("Constructor cannot have a return statement", k.body.lines)
        for m in self.methods:
            m.typecheck()
            # ensure that non-void methods have a return statement on every path
            if (m.rtype.is_subtype_of(Type('void'))): 
                if (isinstance(m.body, BlockStmt)):
                    m.body.stmtlist.append(ReturnStmt(None,m.body.lines))
                else:
                    m.body = BlockStmt([m.body, ReturnStmt(None,m.body.lines)], mbody.lines)
            else:
                if (m.body.has_return() < 2):
                    signal_type_error("Method needs a return statement on every control flow path", m.body.lines)

    def add_field(self, fname, field):
        if field.storage == "static":
            global staticfieldcount
            field.fieldindex = staticfieldcount
            staticfieldcount += 1
        else:
            field.fieldindex = self.fieldindex
            self.fieldindex += 1
        self.fields[fname] = field
    def add_constructor(self, constr):
        self.constructors.append(constr)
    def add_method(self, method):
        self.methods.append(method)

    def add_default_constructor(self):
        # check if a parameterless constructor already exists
        exists = False
        for c in self.constructors:
            if (len(c.vars.get_params()) == 0):
                exists = True
                break
        if (not exists):
            c = Constructor(self.name, 'public')
            c.update_body(SkipStmt(None))
            self.constructors.append(c)            

    def lookup_field(self, fname):
        return lookup(self.fields, fname)

    def is_subclass_of(self, other):
        if (self.name == other.name):
            return True
        elif (self.superclass != None):
             if (self.superclass == other):
                 return True
             else:
                 return self.superclass.is_subclass_of(other)
        return False
    def generate_code(self):
        for k in self.constructors:
            k.generate_code()
        for m in self.methods:
            m.generate_code()
class Type:
    """A class encoding Types in Decaf"""
    def __init__(self, basetype, params=None, literal=False):
        if ((params == None) or (params == 0)):
            if (basetype in ['int', 'boolean', 'float', 'string', 'void', 'error', 'null']):
                self.kind = 'basic'
                self.typename = basetype
            elif (not literal):
                self.kind = 'user'
                self.baseclass = basetype
            else:
                self.kind = 'class_literal'
                self.baseclass = basetype
        else:
            if (params == 1):
                bt = basetype
            else:
                bt = Type(basetype, params=params-1)
            self.kind = 'array'
            self.basetype = bt

    def __str__(self):
        if (self.kind == 'array'):
            return 'array(%s)'%(self.basetype.__str__())
        elif (self.kind == 'user'):
            return 'user(%s)'%str(self.baseclass.name)
        elif (self.kind == 'class_literal'):
            return 'class_literal(%s)'%str(self.baseclass.name)
        else:
            return self.typename

    def __repr(self):
        return self.__str__()

    def is_subtype_of(self, other):
        if (self.kind == 'basic'):
            if other.kind == 'basic':
                if (self.typename == other.typename):
                    return True
                elif (self.typename == 'int') and (other.typename == 'float'):
                    self.itof = True
                    return True
            elif (self.typename == 'null'):
                return (other.kind == 'user') or (other.kind == 'array')
        elif (self.kind == 'user'):
            if (other.kind == 'user'):
                return self.baseclass.is_subclass_of(other.baseclass)
        elif (self.kind == 'class_literal'):
            if (other.kind == 'class_literal'):
                return self.baseclass.is_subclass_of(other.baseclass)
        elif (self.kind == 'array') and (other.kind =='array'):
            return self.basetype.is_subtype_of(other.basetype)
        return False

    def isint(self):
        return self.kind == 'basic' and self.typename == 'int'
        
    def isnumeric(self):
        return self.kind == 'basic' and (self.typename == 'int'
                                         or self.typename == 'float')
    def isboolean(self):
        return self.kind == 'basic' and self.typename == 'boolean'

    def isok(self):
        return not (self.kind == 'basic' and self.typename == 'error')
        

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
        print "FIELD {0}, {1}, {2}, {3}, {4}, {5}, {6}".format(self.id, self.name, self.inclass.name, self.visibility, self.storage,self.type, self.fieldindex)

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
        self.vars = VarTable(self.storage == "static")

    def update_body(self, body):
        self.body = body

    def add_var(self, vname, vkind, vtype):
        self.vars.add_var(vname, vkind, vtype)

    def printout(self):
        print "METHOD: {0}, {1}, {2}, {3}, {4}, {5}".format(self.id, self.name, self.inclass.name, self.visibility, self.storage, self.rtype)
        print "Method Parameters:",
        print ', '.join(["%d"%v.id for v in self.vars.get_params()])
        self.vars.printout()
        print "Method Body:"
        self.body.printout()

    def argtypes(self):
        return [v.type for v in self.vars.get_params()]

    def typecheck(self):
        global current_method
        current_method = self
        self.body.typecheck()
    
    def generate_code(self):
        amifile.write("M_{0}_{1}:\n".format(self.name, str(self.id)))
        global temporaryregisternumber, argumentregisternumber
        temporaryregisternumber = self.vars.temporaryregisternumber
        argumentregisternumber = self.vars.argumentregisternumber
        self.body.generate_code()

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
        print ', '.join(["%d"%v.id for v in self.vars.get_params()])
        self.vars.printout()
        print "Constructor Body:"
        self.body.printout()

    def argtypes(self):
        return [v.type for v in self.vars.get_params()]
        
    def typecheck(self):
        self.body.typecheck()
    def generate_code(self):
        amifile.write("C_{0}_{1}:\n".format(self.name, str(self.id)))
        global temporaryregisternumber, argumentregisternumber
        temporaryregisternumber = self.vars.temporaryregisternumber
        argumentregisternumber = self.vars.argumentregisternumber
        self.body.generate_code()

class VarTable:
    """ Table of variables in each method/constructor"""
    def __init__(self, varTableForStaticMethod = False):
        self.vars = {0:{}}
        self.lastvar = 0
        self.lastblock = 0
        self.levels = [0]
        if varTableForStaticMethod == True:
            self.argumentregisternumber = 0
        else:
            self.argumentregisternumber = 1
        self.temporaryregisternumber = 0

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
        if(vkind == 'local'):
            register = "t" + str(self.temporaryregisternumber)
            self.temporaryregisternumber = self.temporaryregisternumber + 1
        else:
            register = "a" + str(self.argumentregisternumber)
            self.argumentregisternumber = self.argumentregisternumber + 1

        v = Variable(vname, self.lastvar, vkind, vtype, register)
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
        vars = [outermost[vname] for vname in outermost if outermost[vname].kind=='formal']
        vars_ids = [(v.id,v) for v in vars]  # get the ids as well, so that we can order them
        vars_ids.sort()
        return [v for (i,v) in vars_ids]   # in their order of definition!

    def printout(self):
        print "Variable Table:"
        for b in range(self.lastblock+1):
            for vname in self.vars[b]:
                v = self.vars[b][vname]
                v.printout()
        

class Variable:
    """ Record for a single variable"""
    def __init__(self, vname, id, vkind, vtype, register):
        self.name = vname
        self.id = id
        self.kind = vkind
        self.type = vtype
        self.register = register

    def printout(self):
        print "VARIABLE {0}, {1}, {2}, {3}, {4}".format(self.id, self.name, self.kind, self.type, self.register)
    
    def generate_code(self):
        return self.register

class Stmt(object): 
    """ Top-level (abstract) class representing all statements"""

class IfStmt(Stmt):
    def __init__(self, condition, thenpart, elsepart, lines):
        self.lines = lines
        self.condition = condition
        self.thenpart = thenpart
        self.elsepart = elsepart
        self.__typecorrect = None

    def printout(self):
        print "If(",
        self.condition.printout()
        print ", ",
        self.thenpart.printout()
        print ", ",
        self.elsepart.printout()
        print ")"

    def typecheck(self):
        if (self.__typecorrect == None):
            b = self.condition.typeof()
            if (not b.isboolean()):
                signal_type_error("Type error in If statement's condition: boolean expected, found {0}".format(str(b)), self.lines)
                self.__typecorrect = False
            self.__typecorrect = b.isboolean() and self.thenpart.typecheck() and self.elsepart.typecheck()
        return self.__typecorrect

    def has_return(self):
        # 0 if none, 1 if at least one path has a return, 2 if all paths have a return
        r = self.thenpart.has_return() + self.elsepart.has_return()
        if (r == 4):
            return 2
        elif (r > 0):
            return 1
        else:
            return 0

    def generate_code(self):
        global labelnumber
        elselabel = "L" + str(labelnumber)
        labelnumber = labelnumber + 1
        amifile.write("\tbz {0}, {1}\n".format(self.condition.generate_code(), elselabel))
        self.thenpart.generate_code()
        if not isinstance(self.elsepart, SkipStmt):
            thenlabel = "L" + str(labelnumber)
            labelnumber = labelnumber + 1
            amifile.write("\tjmp {0}\n".format(thenlabel))
            amifile.write("{0}:\n".format(elselabel))
            self.elsepart.generate_code()
            amifile.write("{0}:\n".format(thenlabel))
        else:
            amifile.write("{0}:\n".format(elselabel))

class WhileStmt(Stmt):
    def __init__(self, cond, body, lines):
        self.lines = lines
        self.cond = cond
        self.body = body
        self.__typecorrect = None

    def printout(self):
        print "While(",
        self.cond.printout()
        print ", ",
        self.body.printout()
        print ")"

    def typecheck(self):
        if (self.__typecorrect == None):
            b = self.cond.typeof()
            if (not b.isboolean()):
                signal_type_error("Type error in While statement's condition: boolean expected, found {0}".format(str(b)), self.lines)
                self.__typecorrect = False
            self.__typecorrect = b.isboolean() and self.body.typecheck()
        return self.__typecorrect

    def has_return(self):
        # 0 if none, 1 if at least one path has a return, 2 if all paths have a return
        if (self.body.has_return() > 0):
            return 1
        else:
            return 0
    def generate_code(self):
        global labelnumber, breakstatementlabel, continuestatementlabel
        whilestatementlabel = get_new_instruction_label()
        amifile.write("{0}:\n".format(whilestatementlabel))
        afterWhileStatementlabel = get_new_instruction_label()
        breakstatementlabel = afterWhileStatementlabel
        continuestatementlabel = whilestatementlabel
        amifile.write("\tbz {0}, {1}\n".format(self.cond.generate_code(), afterWhileStatementlabel))
        self.body.generate_code()
        amifile.write("\tjmp {0}\n".format(whilestatementlabel))
        amifile.write("{0}:\n".format(afterWhileStatementlabel))

class ForStmt(Stmt):
    def __init__(self, init, cond, update, body, lines):
        self.lines = lines
        self.init = init
        self.cond = cond
        self.update = update
        self.body = body
        self.__typecorrect = None

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

    def typecheck(self):
        if (self.__typecorrect == None):
            a = True
            if (self.init != None):
                a = a and self.init.typeof().isok()
            if (self.update != None):
                a = a and self.update.typeof().isok()
            if (self.cond != None):
                b = self.cond.typeof()
                if (not b.isboolean()):
                    signal_type_error("Type error in For statement's condition: boolean expected, found {0}".format(str(b)), self.lines)
                    a = False
            a = a and self.body.typecheck()
            self.__typecorrect = a
        return self.__typecorrect
        
    def has_return(self):
        # 0 if none, 1 if at least one path has a return, 2 if all paths have a return
        if (self.body.has_return() > 0):
            return 1
        else:
            return 0
    def generate_code(self):
        global breakstatementlabel, continuestatementlabel
        self.init.generate_code()
        forconditionlabel = get_new_instruction_label()
        amifile.write("{0}:\n".format(forconditionlabel))
        r1 = self.cond.generate_code()
        afterforlabel = get_new_instruction_label()
        continuestatementlabel = forconditionlabel
        breakstatementlabel = afterforlabel
        amifile.write("\tbz {0}, {1}\n".format(r1, afterforlabel))
        self.body.generate_code()
        self.update.generate_code()
        amifile.write("\tjmp {0}\n".format(forconditionlabel))
        amifile.write("{0}:\n".format(afterforlabel))

class ReturnStmt(Stmt):
    def __init__(self, expr, lines):
        self.lines = lines
        self.expr = expr
        self.__typecorrect = None

    def printout(self):
        print "Return(",
        if (self.expr != None):
            self.expr.printout()
        print ")"

    def typecheck(self):
        global current_method
        if (self.__typecorrect == None):
            if (self.expr == None):
                argtype = Type('void')
            else:
                argtype = self.expr.typeof()
            self.__typecorrect = argtype.is_subtype_of(current_method.rtype)
            if (argtype.isok() and (not self.__typecorrect)):
                signal_type_error("Type error in Return statement: {0} expected, found {1}".format(str(current_method.rtype), str(argtype)), self.lines)
        return self.__typecorrect

    def has_return(self):
        return 2
    
    def generate_code(self):
        if self.expr:
            argtype = self.expr.typeof()
            r1 = self.expr.generate_code()
            if hasattr(argtype, "itof"):
                amifile.write("\titof {0}, {1}\n".format(r1, r1))
            amifile.write("\tmove a0, {0}\n".format(r1))
        amifile.write("\tret\n")

class BlockStmt(Stmt):
    def __init__(self, stmtlist, lines):
        self.lines = lines
        self.stmtlist = [s for s in stmtlist if (s != None) and (not isinstance(s, SkipStmt))]
        self.__typecorrect = None

    def printout(self):
        print "Block(["
        if (len(self.stmtlist) > 0):
            self.stmtlist[0].printout()
        for s in self.stmtlist[1:]:
            print ", ",
            s.printout()
        print "])"

    def typecheck(self):
        if (self.__typecorrect == None):
            self.__typecorrect = all([s.typecheck() for s in self.stmtlist])
        return self.__typecorrect

    def has_return(self):
        rs = [s.has_return() for s in self.stmtlist]
        if (2 in rs):
            return 2
        elif (1 in rs):
            return 1
        else:
            return 0
    def generate_code(self):
        for s in self.stmtlist:
            s.generate_code()

class BreakStmt(Stmt):
    def __init__(self, lines):
        self.lines = lines
        self.__typecorrect = True

    def printout(self):
        print "Break"

    def typecheck(self):
        return self.__typecorrect

    def has_return(self):
        return 0

    def generate_code(self):
        amifile.write("\tjmp {0}\n".format(breakstatementlabel))

class ContinueStmt(Stmt):
    def __init__(self, lines):
        self.lines = lines
        self.__typecorrect = True

    def printout(self):
        print "Continue"

    def typecheck(self):
        return self.__typecorrect

    def has_return(self):
        return 0

    def generate_code(self):
        amifile.write("\tjmp {0}\n".format(continuestatementlabel))
    
class ExprStmt(Stmt):
    def __init__(self, expr, lines):
        self.lines = lines
        self.expr = expr
        self.__typecorrect = None

    def printout(self):
        print "Expr(",
        self.expr.printout()
        print ")"

    def typecheck(self):
        if (self.__typecorrect == None):
            if (self.expr.typeof().kind == 'error'):
                self.__typecorrect = False
            else:
                self.__typecorrect = True
        return self.__typecorrect

    def has_return(self):
        return 0

    def generate_code(self):
        self.expr.generate_code()
    
class SkipStmt(Stmt):
    def __init__(self, lines):
        self.lines = lines
        self.__typecorrect = True

    def printout(self):
        print "Skip"

    def typecheck(self):
        return self.__typecorrect

    def has_return(self):
        return 0
    def generate_code(self):
        pass
    
class Expr(object):
    '''Class representing all expressions in Decaf'''
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
        self.__typeof = None

            
    def __repr__(self):
        s = "Unknown"
        if (self.kind == 'int'):
            s = "Integer-constant(%d)"%self.int
        elif (self.kind == 'float'):
            s = "Float-constant(%g)"%self.float
        elif (self.kind == 'string'):
            s = "String-constant(%s)"%self.string
        elif (self.kind == 'Null'):
            s = "Null"
        elif (self.kind == 'True'):
            s = "True"
        elif (self.kind == 'False'):
            s = "False"
        return "Constant({0})".format(s)

    def typeof(self):
        if (self.__typeof == None):
            if (self.kind == 'int'):
                self.__typeof = Type('int')
            elif (self.kind == 'float'):
                self.__typeof = Type('float')
            elif (self.kind == 'string'):
                self.__typeof = Type('string')
            elif (self.kind == 'Null'):
                self.__typeof = Type('null')
            elif (self.kind == 'True'):
                self.__typeof = Type('boolean')
            elif (self.kind == 'False'):
                self.__typeof = Type('boolean')
        return self.__typeof
    
    def generate_code(self):
        global temporaryregisternumber
        self.register = "t" + str(temporaryregisternumber)
        if (self.kind == 'int'):
            amifile.write("\tmove_immed_i " + self.register + ", {0}\n".format(str(self.int)))
        elif (self.kind == 'float'):
            amifile.write("\tmove_immed_f " + self.register + ", {0}\n".format(str(self.float)))
        temporaryregisternumber = temporaryregisternumber + 1
        return self.register

class VarExpr(Expr):
    def __init__(self, var, lines):
        self.lines = lines
        self.var = var
        self.__typeof = None

    def __repr__(self):
        return "Variable(%d)"%self.var.id

    def typeof(self):
        if (self.__typeof == None):
            self.__typeof = self.var.type
        return self.__typeof

    def generate_code(self):
        return self.var.generate_code()

    def set_dimension(self, array_dimension):
        self.var.array_dimension = array_dimension

    def get_dimension(self):
        return self.var.array_dimension

class UnaryExpr(Expr):
    def __init__(self, uop, expr, lines):
        self.lines = lines
        self.uop = uop
        self.arg = expr
        self.__typeof = None
    def __repr__(self):
        return "Unary({0}, {1})".format(self.uop, self.arg)

    def typeof(self):
        if (self.__typeof == None):
            argtype = self.arg.typeof()
            self.__typeof = Type('error')
            if (self.uop == 'uminus'):
                if (argtype.isnumeric()):
                    self.__typeof = argtype
                elif (argtype.kind != 'error'):
                    # not already in error
                    signal_type_error("Type error in unary minus expression: int/float expected, found {0}".format(str(argtype)), self.arg.lines)
            elif (self.uop == 'neg'):
                if (argtype.isboolean()):
                    self.__typeof = argtype
                elif (argtype.kind != 'error'):
                    # not already in error
                    signal_type_error("Type error in unary negation expression: boolean expected, found {0}".format(str(argtype)), self.arg.lines)
        return self.__typeof

    def generate_code(self):
        binexpr = BinaryExpr('mul', self.arg, ConstantExpr('int', -1, self.lines), self.lines)
        binexpr.typeof()
        return binexpr.generate_code()

def signal_bop_error(argpos, bop, argtype, arg, possible_types, ptype_string):
    if (argtype.kind not in (['error'] + possible_types)):
        # not already in error
        signal_type_error("Type error in {0} argument of binary {1} expression: {2} expected, found {3}".format(argpos, bop, ptype_string, str(argtype)), arg.lines)
        
class BinaryExpr(Expr):
    def __init__(self, bop, arg1, arg2, lines):
        self.lines = lines
        self.bop = bop
        self.arg1 = arg1
        self.arg2 = arg2
        self.__typeof = None
    def __repr__(self):
        return "Binary({0}, {1}, {2})".format(self.bop,self.arg1,self.arg2)            

    def typeof(self):
        if (self.__typeof == None):
            arg1type = self.arg1.typeof()
            arg2type = self.arg2.typeof()
            self.__typeof = Type('error')
            if (self.bop in ['add', 'sub', 'mul', 'div']):
                if (arg1type.isint()) and (arg2type.isint()):
                    self.__typeof = arg1type
                elif (arg1type.isnumeric()) and (arg2type.isnumeric()):
                    self.__typeof = Type('float')
                else:
                    if (arg1type.isok() and arg2type.isok()):
                        signal_bop_error('first', self.bop, arg1type, self.arg1,
                                         ['int', 'float'], 'int/float')
                        signal_bop_error('second', self.bop, arg2type, self.arg2,
                                         ['int', 'float'], 'int/float')
                    
            elif (self.bop in ['lt', 'leq', 'gt', 'geq']):
                if ((arg1type.isnumeric()) and (arg2type.isnumeric())): 
                    self.__typeof = Type('boolean')
                else:
                    if (arg1type.isok() and arg2type.isok()):
                        signal_bop_error('first', self.bop, arg1type, self.arg1,
                                         ['int', 'float'], 'int/float')
                        signal_bop_error('second', self.bop, arg2type, self.arg2,
                                         ['int', 'float'], 'int/float')
                    
            elif (self.bop in ['and', 'or']):
                if ((arg1type.isboolean()) and (arg2type.isboolean())):
                    self.__typeof = Type('boolean')
                else:
                    if (arg1type.isok() and arg2type.isok()):
                        signal_bop_error('first', self.bop, arg1type, self.arg1,
                                         ['boolean'], 'boolean')
                        signal_bop_error('second', self.bop, arg2type, self.arg2,
                                         ['boolean'], 'boolean')
            else:
                # equality/disequality
                if ((arg1type.isok()) and (arg2type.isok())):
                    if ((arg1type.is_subtype_of(arg2type)) or (arg2type.is_subtype_of(arg1type))):
                        self.__typeof = Type('boolean')
                    else:
                        signal_type_error('Type error in arguments of binary {0} expression: compatible types expected, found {1} and {2}'.format(self.bop, str(arg1type), str(arg2type)), self.lines)
                       
        return self.__typeof

    def generate_code(self, callContext = None):
        r2 = self.arg1.generate_code()
        r3 = self.arg2.generate_code()
        arg1type = self.arg1.typeof()
        arg2type = self.arg2.typeof()
        if arg1type.typename == 'int' and arg2type.typename == 'float':
            amifile.write("\titof {0}, {1}\n".format(r2, r2))
        if arg2type.typename == 'int' and arg1type.typename == 'float':
            amifile.write("\titof {0}, {1}\n".format(r3, r3))
        global temporaryregisternumber
        if(isinstance(callContext,AutoExpr)):
            r1 = r2
        else:
            r1 = "t" + str(temporaryregisternumber)
            temporaryregisternumber = temporaryregisternumber + 1
        if self.bop == 'and':
            amifile.write("\timul {0}, {1}, {2}\n".format(r1, r2, r3))
        elif self.bop == 'or':
            amifile.write("\tiadd {0}, {1}, {2}\n".format(r1, r2, r3))
        elif self.bop in ['add', 'sub', 'mul', 'div']:
            if self.__typeof.isint():
                amifile.write("\ti" + self.bop + " {0}, {1}, {2}\n".format(r1, r2, r3))
            elif self.__typeof.isnumeric():
                amifile.write("\tf" + self.bop + " {0}, {1}, {2}\n".format(r1, r2, r3))
        elif self.bop in ['lt', 'leq', 'gt', 'geq']:
            if self.arg1.typeof().typename == 'int':
                amifile.write("\ti" + self.bop + " {0}, {1}, {2}\n".format(r1, r2, r3))
            elif self.arg1.typeof().typename == 'float':
                amifile.write("\tf" + self.bop + " {0}, {1}, {2}\n".format(r1, r2, r3))
        elif self.bop == 'eq':
            if self.arg1.typeof().typename == 'int':
                instruction = "i"
            else:
                instruction = "f"
            amifile.write("\t{0}geq {1}, {2}, {3}\n".format(instruction, r1, r2, r3))
            r4 = "t" + str(temporaryregisternumber)
            temporaryregisternumber = temporaryregisternumber + 1
            amifile.write("\t{0}leq {1}, {2}, {3}\n".format(instruction, r4, r2, r3))
            r5 = "t" + str(temporaryregisternumber)
            temporaryregisternumber = temporaryregisternumber + 1
            amifile.write("\timul {0}, {1}, {2}\n".format(r5, r1, r4))
            r1 = r5
        return r1

class AssignExpr(Expr):
    def __init__(self, lhs, rhs, lines):
        self.lines = lines
        self.lhs = lhs
        self.rhs = rhs
        self.__typeof = None
    def __repr__(self):
        return "Assign({0}, {1}, {2}, {3})".format(self.lhs, self.rhs, self.lhs.typeof(), self.rhs.typeof())

    def typeof(self):
        if (self.__typeof == None):
            lhstype = self.lhs.typeof()
            rhstype = self.rhs.typeof()
            if (lhstype.isok() and rhstype.isok()):
                if (rhstype.is_subtype_of(lhstype)):
                    self.__typeof = rhstype
                else:
                    self.__typeof = Type('error')
                    signal_type_error('Type error in assign expression: compatible types expected, found {0} and {1}'.format(str(lhstype), str(rhstype)), self.lines)
            else:
                self.__typeof = Type('error')
        return self.__typeof

    def generate_code(self):
        rhstype = self.rhs.typeof()
        if isinstance(self.rhs, NewArrayExpr):
            tempreg, arraydimensions = self.rhs.generate_code()
            self.lhs.set_dimension(arraydimensions)
        else:
            tempreg = self.rhs.generate_code()
        if hasattr(rhstype, "itof"):
            amifile.write("\titof {0}, {1}\n".format(tempreg, tempreg))

        if isinstance(self.lhs, ArrayAccessExpr):
            self.lhs.generate_code(False, tempreg)

        elif isinstance(self.lhs, FieldAccessExpr):
            self.lhs.generate_code(False, tempreg)
        else:
            amifile.write("\tmove {0}, {1}\n".format(self.lhs.generate_code(), tempreg))
        #if isinstance(self.rhs, NewObjectExpr):
        #    self.lhs.register = tempreg

class AutoExpr(Expr):
    def __init__(self, arg, oper, when, lines):
        self.lines = lines
        self.arg = arg
        self.oper = oper
        self.when = when
        self.__typeof = None
    def __repr__(self):
        return "Auto({0}, {1}, {2})".format(self.arg, self.oper, self.when)

    def typeof(self):
        if (self.__typeof == None):
            argtype = self.arg.typeof()
            if (argtype.isnumeric()):
                self.__typeof = argtype
            else:
                self.__typeof = Type('error')
                if (argtype.isok()):
                    signal_type_error('Type error in auto expression: int/float expected, found {0}'.format(str(argtype)), self.lines)
        return self.__typeof

    def generate_code(self):
        binexpr = BinaryExpr(autoexprmap[self.oper], self.arg, ConstantExpr('int', 1, self.lines), self.lines)
        binexpr.typeof()
        reg = self.arg.generate_code()
        if(self.when == 'post'):
            reg2 = get_new_temporary_register()
            amifile.write("\tmove {0}, {1}\n".format(reg2, reg))
            binexpr.generate_code(self)
        else:
            reg2 = binexpr.generate_code(self)
        return reg2

def find_applicable_methods(acc, baseclass, mname, argtypes):
    ms = []
    for m in baseclass.methods:
        if ((m.name == mname) and (m.storage == acc)):
            params = m.vars.get_params()
            paramtypes = [v.type for v in params]
            if ((len(paramtypes) == len(argtypes)) and
                all([(a.is_subtype_of(p)) for (a,p) in (zip(argtypes, paramtypes))])):
                # if every arg is a subtype of corresponding parameter
                ms.append((m, paramtypes))
    
    return ms

def find_applicable_constructors(baseclass, argtypes):
    cs = []
    for c in baseclass.constructors:
        #print baseclass.name
        params = c.vars.get_params()
        paramtypes = [v.type for v in params]
        #print len(params) , len(argtypes)
        if ((len(paramtypes) == len(argtypes)) and
            all([(a.is_subtype_of(p)) for (a,p) in (zip(argtypes, paramtypes))])):
            # if every arg is a subtype of corresponding parameter
            cs.append((c, paramtypes))
    
    return cs

def most_specific_method(ms):
    mst = None
    result = None
    for (m, t) in ms:
        if (mst == None):
            mst = t
            result = m
        else:
            if all([a.is_subtype_of(b) for (a,b) in zip(mst, t)]):
                # current most specific type is at least as specific as t
                continue
            elif all([b.is_subtype_of(a) for (a,b) in zip(mst, t)]):
                # current t is at least as specific as the most specific type 
                mst = t
                result = m
            else:
                # t is no more specific than mst, nor vice-versa
                return (None, (mst, result, t, m))
                break
    return (result, None)
        
def subtype_or_incompatible(tl1, tl2):
    #  True iff tl1 is a subtype of tl2 or tl2 is a subtype of tl1, or the two type lists are incompatible
    n = len(tl1)
    if (len(tl2) != n):
        return True

    # is tl1 a subtype of tl2?  return False if any incompatible types are found
    subt = True
    for i in range(0,n):
        t1 = tl1[i]
        t2 = tl2[i]
        if (not t1.is_subtype_of(t2)):
            subt = False
            if (t2.is_subtype_of(t1)):
                # tl2 may be a subtype of tl1, so we need to wait to check that
                break
            else:
                # types are incompatible
                return True
    if (subt):
        return True
    # Check the other direction
    for i in range(0,n):
        t1 = tl1[i]
        t2 = tl2[i]
        if (not t2.is_subtype_of(t1)):
            return False
    # tl2 is a subtype of tl1
    return True    

def resolve_method(acc, baseclass, mname, argtypes, current, lineno):
    original_baseclass = baseclass
    while (baseclass != None):
        ms = find_applicable_methods(acc, baseclass, mname, argtypes)
        (m, errorc) = most_specific_method(ms)
        if ((len(ms) > 0) and 
            (m != None) and ( (m.visibility == 'public') or (baseclass == current) )):
            return m
        elif (len(ms) > 0) and (m == None):
            # there were applicable methods but no unique one.
            (t1, m1, t2, m2) = errorc
            signal_type_error("Ambiguity in resolving overloaded method {0}: methods with types '{1}' and '{2}' in class {3}".format(mname, str(t1), str(t2), baseclass.name), lineno)
            return None
        else:
            baseclass = baseclass.superclass
    # search for mname failed,
    signal_type_error("No accessible method with name {0} in class {1}".format(mname, original_baseclass.name), lineno)
    return None

def resolve_constructor(baseclass, current, argtypes, lineno):
    cs = find_applicable_constructors(current, argtypes)
    (c, errorc) = most_specific_method(cs)
    #print len(cs), c
    if ((len(cs) > 0) and 
        (c != None) and ( (c.visibility == 'public') or (baseclass == current) )):
        return c
    elif (len(cs) > 0) and (c == None):
        # there were applicable constructors but no unique one.
        (t1, c1, t2, c2) = errorc
        signal_type_error("Ambiguity in resolving overloaded constructor {0}: constructors with types '{1}' and '{2}'}".format(baseclass.name, str(t1), str(t2)), lineno)
        return None
    else:
        signal_type_error("No accessible constructor for class {0}".format(current.name), lineno)
        return None
    

def resolve_field(acc, baseclass, fname, current):
    while (baseclass != None):
        f = baseclass.lookup_field(fname)
        if ((f != None) and (f.storage == acc)
            and ( (f.visibility == 'public') or (baseclass == current) )):
            return f
        else:
            baseclass = baseclass.superclass
    # search for fname failed,
    return None

class FieldAccessExpr(Expr):
    def __init__(self, base, fname, lines):
        self.lines = lines
        self.base = base
        self.fname = fname
        self.__typeof = None
        self.field = None

    def __repr__(self):
        return "Field-access({0}, {1}, {2})".format(self.base, self.fname, self.field.id)

    def typeof(self):
        if (self.__typeof == None):
            # resolve the field name first
            btype = self.base.typeof()
            if btype.isok():
                if btype.kind not in ['user', 'class_literal']:
                    signal_type_error("User-defined class/instance type expected, found {0}".format(str(btype)), self.lines)
                    self.__typeof = Type('error')
                else:
                    if btype.kind == 'user':
                        # user-defined instance type:
                        acc = 'instance'
                    else:
                        # user-defined class type
                        acc = 'static'

                    baseclass =  btype.baseclass
                    j = resolve_field(acc, baseclass, self.fname, current_class)
                    if (j == None):
                        signal_type_error("No accessible field with name {0} in class {1}".format(self.fname, baseclass.name), self.lines)
                        self.__typeof = Type('error')
                    else:
                        self.field = j
                        self.__typeof = j.type
                        
        return self.__typeof

    def generate_code(self, isrvalue = True, reg = None):
        p1 = get_new_temporary_register()
        amifile.write("\tmove_immed_i {0}, {1}\n".format(p1, self.field.fieldindex))
        p2 = get_new_temporary_register()
        if isinstance(self.base, ClassReferenceExpr):
            reg3 = "sap"
        else:
            reg3 = self.base.generate_code()
        if isrvalue == True:
            amifile.write("\thload {0}, {1}, {2}\n".format(p2, reg3, p1))
        else:
            amifile.write("\thstore {0}, {1}, {2}\n".format(reg3, p1, reg))
        return p2

    def set_dimension(self, array_dimension):
        self.field.array_dimension = array_dimension

    def get_dimension(self):
        return self.field.array_dimension

class MethodInvocationExpr(Expr):
    def __init__(self, field, args, lines):
        self.lines = lines
        self.base = field.base
        self.mname = field.fname
        self.args = args
        self.method = None
        self.__typeof = None
    def __repr__(self):
        return "Method-call({0}, {1}, {2})".format(self.base, self.mname, self.args)

    def typeof(self):
        if (self.__typeof == None):
            # resolve the method name first
            btype = self.base.typeof()
            if btype.isok():
                if btype.kind not in ['user', 'class_literal']:
                    signal_type_error("User-defined class/instance type expected, found {0}".format(str(btype)), self.lines)
                    self.__typeof = Type('error')
                else:
                    if btype.kind == 'user':
                        # user-defined instance type:
                        acc = 'instance'
                    else:
                        # user-defined class type
                        acc = 'static'

                    baseclass =  btype.baseclass
                    argtypes = [a.typeof() for a in self.args]
                    if (all([a.isok() for a in argtypes])):
                        j = resolve_method(acc, baseclass, self.mname, argtypes, current_class, self.lines)
                        
                        if (j == None):
                            self.__typeof = Type('error')
                        else:
                            self.method = j
                            self.__typeof = j.rtype
                    else:
                        self.__typeof = Type('error')
        return self.__typeof
    
    def generate_code(self):
        global argumentregisternumber, temporaryregisternumber
        count = temporaryregisternumber
        count1 = argumentregisternumber

        tempregstack = []
        argregstack = []

        tempCount = 0

        while tempCount < argumentregisternumber:
            argreg = "a" + str(tempCount);
            amifile.write("\tsave {0}\n".format(argreg))
            argregstack.append(argreg)
            tempCount = tempCount + 1

        tempCount = 0
        while tempCount < temporaryregisternumber:
            tempreg = "t" + str(tempCount)
            amifile.write("\tsave {0}\n".format(tempreg))
            tempregstack.append(tempreg)
            tempCount = tempCount + 1

        currentarg = 0

        if not isinstance(self.base, ClassReferenceExpr) \
            and not isinstance(self.base, ThisExpr) \
            and not isinstance(self.base, SuperExpr):
            amifile.write("\tmove a{0}, {1}\n".format(str(currentarg), self.base.generate_code()))
        #copy all args here
        if not isinstance(self.base, ClassReferenceExpr):
            currentarg = currentarg + 1

        for v in self.args:
            tempreg = v.generate_code()
            amifile.write("\tmove a{0}, {1}\n".format(str(currentarg), str(tempreg)))
            currentarg = currentarg + 1

        amifile.write("\tcall M_{0}_{1}\n".format(self.mname, self.method.id))

        new_tempreg = get_new_temporary_register()
        amifile.write("\tmove {0}, {1}\n".format(new_tempreg, "a0"))
        while len(tempregstack) > 0:
            amifile.write("\trestore {0}\n".format(tempregstack.pop()))

        while len(argregstack) > 0:
            amifile.write("\trestore {0}\n".format(argregstack.pop()))

        return new_tempreg

class NewObjectExpr(Expr):
    def __init__(self, cref, args, lines):
        self.lines = lines
        self.classref = cref
        self.args = args
        self.__typeof = None
    def __repr__(self):
        return "New-object({0}, {1})".format(self.classref.name, self.args)

    def typeof(self):
        if (self.__typeof == None):
            # resolve the constructor name first
            argtypes = [a.typeof() for a in self.args]
            if (all([a.isok() for a in argtypes])):
                j = resolve_constructor(current_class, self.classref, argtypes, self.lines)
                if (j == None):
                    self.__typeof = Type('error')
                else:
                    self.constructor = j
                    self.__typeof = Type(self.classref)
            else:
                # type error in some argument; already signaled before
                self.__typeof = Type('error')
        return self.__typeof
    def generate_code(self):
        global argumentregisternumber, temporaryregisternumber
        #print temporaryregisternumber
        count = temporaryregisternumber
        amifile.write("\tmove_immed_i t{0}, {1}\n".format(str(temporaryregisternumber),str(self.classref.fieldindex)))
        temporaryregisternumber = temporaryregisternumber + 1
        amifile.write("\thalloc t{0}, t{1}\n".format(str(temporaryregisternumber),str(temporaryregisternumber - 1)))
        temporaryregisternumber = temporaryregisternumber + 1
        
        count1 = argumentregisternumber - 1
        tempCount = 0

        while tempCount <= count1:
            amifile.write("\tsave a{0}\n".format(str(tempCount)))
            tempCount = tempCount + 1

        tempCount = 0

        while tempCount <= count:
            amifile.write("\tsave t{0}\n".format(str(tempCount)))
            tempCount = tempCount + 1

        r1 = "t" + str(count+1)
        amifile.write("\tmove a0, t{0}\n".format(str(count+1)))
        #copy all args here
        currentarg = 0
        for v in self.args:
            tempreg = v.generate_code()
            amifile.write("\tmove a{0}, {1}\n".format(str(currentarg+1), str(tempreg)))
            currentarg = currentarg + 1

        amifile.write("\tcall C_{0}\n".format(self.constructor.id))

        while count >= 0:
            amifile.write("\trestore t{0}\n".format(str(count)))
            count = count - 1

        while count1 >= 0:
            amifile.write("\trestore a{0}\n".format(str(count1)))
            count1 = count1 - 1
        global newobjectexpressionregsiter
        newobjectexpressionregsiter = r1
        return r1

class ThisExpr(Expr):
    global current_class
    def __init__(self, lines):
        self.lines = lines
        self.__typeof = None
    def __repr__(self):
        return "This"
    def typeof(self):
        if (self.__typeof == None):
            self.__typeof = Type(current_class)
        return self.__typeof
    def generate_code(self):
        return "a0"

class SuperExpr(Expr):
    global current_class
    def __init__(self, lines):
        self.lines = lines
        self.__typeof = None
    def __repr__(self):
        return "Super"

    def typeof(self):
        if (self.__typeof == None):
            if (current_class.superclass != None):
                self.__typeof = Type(current_class.superclass)
            else:
                self.__typeof = Type('error')
                signal_type_error("Type error in Super expression: class {0} has no superclass".format(str(current_class)), self.lines)
        return self.__typeof
    def generate_code(self):
        return "a0"
    
class ClassReferenceExpr(Expr):
    def __init__(self, cref, lines):
        self.lines = lines
        self.classref = cref
        self.__typeof = None
    def __repr__(self):
        return "ClassReference({0})".format(self.classref.name)

    def typeof(self):
        if (self.__typeof == None):
            self.__typeof = Type(self.classref, literal=True)
        return self.__typeof

    def generate_code(self):
        pass
    
class ArrayAccessExpr(Expr):
    def __init__(self, base, index, lines):
        self.lines = lines
        self.base = base
        self.index = index
        self.__typeof = None
    def __repr__(self):
        return "Array-access({0}, {1})".format(self.base, self.index)

    def typeof(self):
        if (self.__typeof == None):
            if (not self.index.typeof().isint()):
                signal_type_error("Type error in index of Array Index expression: integer expected, found {0}".format(str(self.index.typeof())), self.index.lines)
                mytype = Type('error')
            if (self.base.typeof().kind != 'array'):
                signal_type_error("Type error in base of Array Index expression: array type expected, found {0}".format(str(self.base.typeof())), self.base.lines)
                mytype = Type('error')
            else:
                mytype = self.base.typeof().basetype
            self.__typeof = mytype
        return self.__typeof

    def generate_code(self, isrvalue = True, reg1 = None):
        p = self
        l = []
        while isinstance(p, ArrayAccessExpr):
            l.append(p.index.int)
            p = p.base
        dim = p.get_dimension()
        l.reverse()
        val = 0
        for x in range(0, len(dim)):
             val = val + dim[x] * l[x]
        index = val + l[x+1]
        reg = p.generate_code()
        temp_reg = get_new_temporary_register()
        amifile.write("\tmove_immed_i {0}, {1}\n".format(temp_reg, str(index)))

        p2 = get_new_temporary_register()
        if isrvalue == False:
            amifile.write("\thstore {0}, {1}, {2}\n".format(reg, temp_reg, reg1))
        else:
            amifile.write("\thload {0}, {1}, {2}\n".format(p2, reg, temp_reg))
        return p2

class NewArrayExpr(Expr):
    def __init__(self, basetype, args, lines):
        self.lines = lines
        self.basetype = basetype
        self.args = args
        self.__typeof = None

    def __repr__(self):
        return "New-array({0}, {1})".format(self.basetype, self.args)

    def typeof(self):
        if (self.__typeof == None):
            mytype = Type(self.basetype, len(self.args))
            for a in self.args:
                if (not a.typeof().isok()):
                    # previous error, so mark and pass
                    mytype = Type('error')
                    break
                if (not a.typeof().isint()):
                    # int arg type expected
                    signal_type_error("Type error in argument to New Array expression: int expected, found {0}".format(str(a.typeof())), a.lines)
                    mytype = Type('error')
                    break
            self.__typeof = mytype
        return self.__typeof

    def generate_code(self):
            global temporaryregisternumber
            l = [] # used to return the dimnesions of NewArrayExpressions which will be used for array access expression
            firstCell = 1
            tempreg = 0
            for v in self.args:
                temp1 = v.generate_code()
                if firstCell:
                    tempreg = temp1
                    firstCell = 0
                else:
                    l.append(v.int)
                    amifile.write("\timul {0}, {1}, {2}\n".format(tempreg, tempreg, temp1))
            amifile.write("\thalloc t{0}, {1}\n".format(str(temporaryregisternumber),str(tempreg)))
            temporaryregisternumber = temporaryregisternumber + 1
            return  "t" + str(temporaryregisternumber -1), l

def signal_type_error(string, lineno):
    global errorflag
    print "{1}: {0}".format(string, lineno)
    errorflag = True
