import fileinput
import re
import sys
stack = []
labeldict = {}
loadStore = {}

oneArgInstructions = ["ildc" , "jz", "jnz", "jmp"]
jumpInstructions = ["jz", "jmp", "jnz"]
zeroarginstructions = ["iadd", "isub", "imul", "imod", "idiv", "pop", "dup", "load", "store", "swap"]
listofinstructions = oneArgInstructions + zeroarginstructions
regexForLabel = r'^[a-zA-Z][\w]*$'
regexForNumber = r'^[-|+]?([0-9])+$'

# concatenating all of the inputs into a single line by replacing \n with an extra space
# also remove comments whereever they appear
def parseInputToRemoveCommentsAndHandleInstructionsOnSameLine():
    s = ""
    for line in fileinput.input():
        indexOfHash = line.find("#") # find '#' and remove everything on its right
        if indexOfHash != -1:
            line = line[0:indexOfHash]
        s = s + line + " "
    return s

def handleExtraSpacesForLabels(s):
    # adding a space after : so that the string.split splits labels separately with operands
    s = re.sub(':',': ', s)
    s = re.sub(r'\s*:', ':',s)
    token = s.split()
    return token

def parseLabelsAndEnsureAnArgumentExistsForTwoArgInstructions(token):
    index = 0
    count = 0
    tokenlist = []
    # extract labels,tokenize the instructions as per expected number of arguments
    while index < len(token):
        if token[index].find(":") != -1: # if token is a label, add to label dictionary
            labelName = token[index][:-1]
            if not re.match(regexForLabel, labelName) or labelName in labeldict or labelName in listofinstructions:
                print "\nError:Label is Invalid", labelName
                sys.exit()
            labeldict[labelName]= count
            index = index + 1
            continue
        elif token[index] not in oneArgInstructions: # instructions without arguments
            tokenlist.append(token[index].split())
            count = count + 1
            index = index + 1
        else: # check to make sure that instructions with 1 argument are valid
            l = []
            if index < len(token) and index+1 < len(token):
                l.append(token[index])
                l.append(token[index+1])
                tokenlist.append(l)
                count = count + 1
                index = index + 2
            else:
                print "\nError: Invalid argument specified or argument missing"
                sys.exit()
    return tokenlist

def validateTwoArgumentInstuctions(tokenlist):
    iter1 = 0
    while iter1 < len(tokenlist):
        if tokenlist[iter1][0] == 'ildc': # check to make sure that a number is second argument for ildc
            val = tokenlist[iter1][1]
            if not re.match(regexForNumber, val, 0):
                print "\nError: Argument for ildc is invalid", val
                sys.exit()
        elif tokenlist[iter1][0] in jumpInstructions: # check for a jmp instructon having a valid label specified.
            if tokenlist[iter1][1] not in labeldict:
                print "\nError: Unknown Label Specified", tokenlist[iter1][1]
                sys.exit()
        elif tokenlist[iter1][0] not in zeroarginstructions:
            print "\nError: Unknown/Invalid Instruction Specified", tokenlist[iter1][0]
            sys.exit()
        iter1 = iter1 + 1

def executeSSMInstructions(tokenlist):
    iter1 = 0
    while iter1 < len(tokenlist):
        try:
            if tokenlist[iter1][0] == 'ildc': # expects a number as second argument
                val = tokenlist[iter1][1]
                stack.append(int(val))
            elif tokenlist[iter1][0] == 'iadd':
                x = stack.pop()
                y = stack.pop()
                stack.append(x+y)
            elif tokenlist[iter1][0] == 'isub':
                x = stack.pop()
                y = stack.pop()
                stack.append(y-x)
            elif tokenlist[iter1][0] == 'imul':
                x = stack.pop()
                y = stack.pop()
                stack.append(x*y)
            elif tokenlist[iter1][0] == 'idiv':
                x = stack.pop()
                y = stack.pop()
                stack.append(int(y/x))
            elif tokenlist[iter1][0] == 'imod':
                x = stack.pop()
                y = stack.pop()
                stack.append(y%x)
            elif tokenlist[iter1][0] == 'pop':
                stack.pop()
            elif tokenlist[iter1][0] == 'dup':
                x = stack.pop()
                stack.append(x)
                stack.append(x)
            elif tokenlist[iter1][0] == 'jz': # expects a label from label dictionary
                x = stack.pop()
                if x == 0:
                    iter1 = labeldict[tokenlist[iter1][1]]
                    continue
            elif tokenlist[iter1][0] == 'jnz': # expects a label from label dictionary
                x = stack.pop()
                if x != 0:
                    iter1 = labeldict[tokenlist[iter1][1]]
                    continue
            elif tokenlist[iter1][0] == 'jmp': # expects a label from label dictionary
                iter1 = labeldict[tokenlist[iter1][1]]
                continue
            elif tokenlist[iter1][0] == 'swap':
                x = stack.pop()
                y = stack.pop()
                stack.append(x)
                stack.append(y)
            elif tokenlist[iter1][0] == 'store':
                x = stack.pop()
                y = stack.pop()
                loadStore[y] = x
            elif tokenlist[iter1][0] == 'load':
                x=stack.pop()
                if x in loadStore:
                    y = loadStore[x];
                    stack.append(y);
                else:
                    print "\nError: Unitialized Memory Location", x
                    sys.exit()
            else:
                print "\nError: Unknown/Invalid Instruction Specified", tokenlist[iter1][0]
                sys.exit()

        except IndexError:
                print "\nError: Stack is Empty. Invalid Pop"
                sys.exit()

        iter1 = iter1 + 1

instructions = parseInputToRemoveCommentsAndHandleInstructionsOnSameLine()
token = handleExtraSpacesForLabels(instructions)
tokenList = parseLabelsAndEnsureAnArgumentExistsForTwoArgInstructions(token)
validateTwoArgumentInstuctions(tokenList)
executeSSMInstructions(tokenList)
print '\n\nOutput:'
if len(stack) > 0:
    print stack.pop()
else:
    print "Stack is Empty!"
