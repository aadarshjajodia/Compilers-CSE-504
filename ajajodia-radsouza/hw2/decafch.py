import sys
import decaflexer
import decafparser

filename = sys.argv[-1]

f = open(filename, 'r')

contents = f.read()
f.close()

mylexer = decaflexer.make_lexer()

myparser = decafparser.make_parser()

result = myparser.parse(contents, lexer=mylexer)

if not decafparser.error and not result : print "Yes"
print 
