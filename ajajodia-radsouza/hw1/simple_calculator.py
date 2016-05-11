import fileinput
import re
import sys
ssm = []
labeldict = {}

variable = r'^[a-zA-Z][\w]*$'
digits = r'^[~]?[\d]+$'
operator = r'[*-+\/]'

#regular expresson to validate a statement of the form v = E;
regexForStatement = r'([a-zA-Z][\w]*)[\s]+(=)[\s]+([^=.]*)'
def validateStatement(line):
    p = line.split()
    index = len(p) - 1;
    if(len(p) == 0):
        return 0;
    elif(len(p) == 1):
        if(re.match(variable, p[0]) or re.match(digits, p[0])):
            return 1
        else:
            return 0
    flag = 0
    p = p[::-1]
    stack = []
    for x in p:
        if re.match(r'[+-\/*]', x):
            if len(stack) < 2:
                return 0
            else:
                stack.pop()
                stack.pop()
                stack.append("a")
        else:
            if re.match(variable, x) or re.match(digits, x):
                stack.append(x)
    if len(stack) > 1:
        return 0
    return 1


# concatenating all of the inputs into a single line by replacing \n with an ;
# also remove comments wherever they appear
def separateMutipleStatements():
    s = ""
    for line in fileinput.input():
        s = s + line + " "
    low = 0;
    high = 0;
    t = []
    while not re.match(r'^\s+$',s) and s != "" and s != '\n' and len(s):
        high = s.find(";")
        if high == -1:
            print "\nError: Statement without a semicolon", s
            sys.exit()
        t.append(s[0:high])
        if high + 1 > len(s):
            break
        s = s[high+1:]
    t = filter(None, t)
    return t

# Function which returns the single state machine instructions from the infix expressions.
def buildSimpleStateMachine(statements):
    count = 0
    for statement in statements:
        index = 0
        stack = []
        if statement != '\n' and statement != "" and not re.match(r'^\s*$', statement):
            m = re.search(regexForStatement, statement)
            if not m:
                print "\nError: Invalid Statement", statement
                sys.exit()
            if validateStatement(m.group(3)) == 1:
                token = statement.split()
                lvalue = token[0]
                if not re.match(variable, lvalue):
                    print "\nError: Invalid variable name", lvalue
                    sys.exit()
                index = index + 2
                if lvalue in labeldict:
                    ssm.append("ildc " + str(labeldict[lvalue]))
                else:
                    ssm.append("ildc " + str(count))
                while index < len(token):
                    if re.match(digits,token[index]):
                        token[index] = token[index].replace('~', '-')
                        ssm.append("ildc " + str(token[index]))
                    elif token[index] == '+':
                        stack.append("iadd")
                    elif token[index] == '-':
                        stack.append("isub")
                    elif token[index] == '*':
                        stack.append("imul")
                    elif token[index] == '/':
                        stack.append("idiv")
                    elif token[index] == '%':
                        stack.append("imod")
                    else:
                        if token[index] in labeldict:
                            ssm.append("ildc " + str(labeldict[token[index]]))
                            ssm.append("load")
                        else:
                            print "\nError: Invalid variable usage", token[index]
                            sys.exit()
                    index = index + 1
                while stack:
                    ssm.append(stack.pop())
                ssm.append("store")
                if lvalue not in labeldict:
                    labeldict[lvalue] = count;
                    count = count + 1
            else:
                print "\nError: Invalid Statement", statement
                sys.exit()
    return ssm

# The main function which separates the individual instructions and generates the ssm instructions.
def simple_calculator():
    statements = separateMutipleStatements()
    ssm = buildSimpleStateMachine(statements)
    print "\n\nOutput:"
    for instruction in ssm:
        print instruction

simple_calculator()
