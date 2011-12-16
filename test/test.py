import sys
sys.path.append('..')

import hypermako

#for x in hypermako.hypermako_grammar.lex(file('test.mako').read()):
#    print x

print hypermako.convert(file('test.mako').read())

