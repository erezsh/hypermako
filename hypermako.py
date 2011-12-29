from collections import defaultdict
from itertools import chain
import os.path

from plyplus import plyplus

def classify(l, key, value=None):
    classification = defaultdict(list)
    for i in l:
        classification[key(i)].append( value(i) if value else i )
    return dict(classification)

hypermako_dir = os.path.split(__file__)[0]
hypermako_grammar = plyplus.Grammar(file(os.path.join(hypermako_dir,'hypermako.g')), auto_filter_tokens=True, expand_all_repeaters=True)

def flatten_string_tree(tree, depth=0):
    indent_str = ' '*(depth*4)
    l = []
    for i in tree:
        if isinstance(i, (list,tuple)):
            l += flatten_string_tree(i, depth+1)
        else:
            l.append(indent_str+i)
    return l

class ToMako(plyplus.Transformer):
    def mako_pythonblock(self, tree):
        return (tree[1],)
    def raw(self, tree):
        return (tree[1],)
    def hyper_tagdecl(self, tree):
        tree = tree[1]
        tag_elements = classify(tree[1:], lambda x:x[0], lambda x:x[1])
        [tag] = tag_elements.get('tag', ['div'])
        [id] = tag_elements.get('id', [None])
        classes = tag_elements.get('class', ())

        attrs = ['']
        if id:
            attrs.append( 'id="%s"' % id )
        if classes:
            attrs.append( 'class="%s"' % (' '.join(classes),) )

        return (tag, attrs)
    def hyper_expr(self, tree):
        tag,attrs = tree[1]
        if len(tree) > 2:
            attrs += tree[2]

        return (tag, attrs)

    def hyper_exprs(self, tree):
        if len(tree) == 3:
            return [tree[0], tree[1]] + tree[2][1:]
        return tree

    def hyper_line(self, tree):
        exprs = tree[1][1:]

        if len(tree) > 2:
            content = [tree[2]]
        else:
            content = None

        for tag, attrs in reversed(exprs):
            attrs = ' '.join(attrs)
            if content:
                if content == [('',)]:  # Empty tag hack
                    content = ['<%s%s></%s>' % (tag, attrs, tag)]
                else:
                    content = ['<%s%s>' % (tag, attrs)] + content + ['</%s>' % (tag,)]
            else:
                content = ['<%s %s />' % (tag,attrs)]

        return content

    def block(self, tree):
        return list(chain(*tree[1:]))
    def mako_control_stmt(self, tree):
        return tree[1]
    def mako_control_stmt2(self, tree):
        return tree[1]
    def mako_meta_stmt(self, tree):
        stmt = tree[1]
        assert stmt.startswith( '%!' )
        return stmt[2:].strip()
    def mako_meta_oneliner(self, tree):
        return ('<%' + tree[1] + '/>',)
    def mako_meta_block(self, tree):
        stmt = tree[1]
        control_word = stmt.split(None,1)[0]
        opener = '<%'+stmt + '>'
        closer = '</%'+control_word+'>'
        return (opener, tree[2], closer)

    def mako_control_block(self, tree):
        ctl_start = tree[1]
        assert ctl_start[0] == '%'
        ctl_word = ctl_start[1:].split(None,1)[0]
        ctl_end = '%end'+ctl_word

        return tree[1:] + [ctl_end]
    def mako_code_block(self, tree):
        return (tree[1],)
    def text(self, tree):
        return (tree[1].strip()[1:].strip(),)
    def name(self, tree):
        s = tree[1]
        if s[0] == 'start':
            s = ''.join(x[1] for x in s[1:])
        return s
    def value(self, tree):
        s = tree[1]
        if s[0] == 'start':
            s = ''.join(x[1] for x in s[1:])
        if not s.startswith('"'):
            s = '"%s"' % s
        return s
    def hyper_tagattr(self, tree):
        if tree[1][0] == 'start':
            return ''.join(x[1] for x in tree[1][1:])
        return '%s=%s' % (tree[1], tree[2])
    def hyper_tagattrs(self, tree):
        return tree[1:]
    def hyper_verbatim(self, tree):
        return (tree[1][2:-2].strip(),)


    def start(self, tree):
        return tree



def convert(text):
    tree = hypermako_grammar.parse(text)
    str_tree = ToMako().transform(tree)
    return '\n'.join(flatten_string_tree( str_tree[1] ))

