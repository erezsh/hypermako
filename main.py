from collections import defaultdict
import os.path

from plyplus import plyplus

def classify(l, key, value=None):
    classification = defaultdict(list)
    for i in l:
        classification[key(i)].append( value(i) if value else i )
    return dict(classification)

hypermako_dir = os.path.split(__file__)[0]
hypermako_grammar = plyplus.Grammar(file(os.path.join(hypermako_dir,'hypermako.g')), auto_filter_tokens=True)

class List(list):
    pass
class Dict(dict):
    pass

class HyperToMako(plyplus.SVisitor):
    def hyper_tagdecl(self, tagdecl):
        [tag] = tagdecl.select('tag>name>*:is-leaf') or ['div']
        ids = List(tagdecl.select('id>name>*:is-leaf'))
        classes = List(tagdecl.select('class>name>*:is-leaf'))
        tagdecl.reset('hyper_tagdecl2', [tag, ids, classes])

    def hyper_tagattr(self, tagattr):
        if tagattr.tail[0].head == 'start': # "raw" attribute, we just send it as it is
            raw_attr = tagattr.select1('name > *:is-leaf')
            tagattr.reset('hyper_tagattr2', ['*RAW*', raw_attr])
            return

        name = tagattr.select1('name name>*:is-leaf')
        value = tagattr.select1('value *:is-leaf')
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        tagattr.reset('hyper_tagattr2', [name, value])

    def hyper_expr(self, expr):
        tagdecl = expr.select1('hyper_tagdecl2')
        attrs = {}
        tag, ids, classes = tagdecl.tail
        if ids:
            if len(ids) > 1: raise ValueError('More than one id!')
            attrs['id'] = ids
        if classes:
            attrs['class'] = classes
        for attr in expr.select('hyper_tagattr2'):
            name, value = attr.tail
            if attr in attrs:
                attrs[name].append( value )
            else:
                attrs[name] = [ value ]

        expr.reset('hyper_expr2', [tag, Dict(attrs)])

    def text(self, text):
        text.reset('mako_tree', [text.tail[0].strip()[1:].strip()])   # strip spaces and left pipe
    def var(self, var):
        var.reset('mako_tree', ['${%s}' % var.tail[0].strip()[2:].strip()])   # strip spaces and left pipe
    def raw(self, raw):
        raw.reset('mako_tree', [raw.tail[0].strip()])
    def hyper_verbatim(self, tree):
        tree.reset('mako_tree', [tree.tail[0][2:-2].strip()])

    def hyper_line(self, line):
        exprs = line.select('hyper_expr2')

        assert len(line.tail) <= 2
        try:
            content = line.tail[1]
        except IndexError:
            content = None

        for expr in reversed(exprs):
            tag, attrs = expr.tail
            attrs = ' '.join(
                    ('%s="%s"'%(name,' '.join(values)) if name!='*RAW*' else ' '.join(values))
                    for name,values in attrs.iteritems()
                )
            if attrs: attrs = ' ' + attrs
            if content is not None:
                if content == '':   # TODO fix this test
                    content = ['<%s%s></%s>' % (tag, attrs, tag)]
                else:
                    content = ['<%s%s>' % (tag, attrs), content, '</%s>' % (tag,)]
            else:
                content = ['<%s%s />' % (tag,attrs)]
            content = line.__class__('mako_tree', content)

        line.reset('mako_tree', [content])

    def block(self, block):
        block.head = 'mako_tree'
    def mako_line(self, line):
        line.head = 'mako_tree'
    def mako_code_block(self, line):
        line.head = 'mako_tree'
    def mako_control_stmt(self, line):
        line.head = 'mako_tree'
    def mako_control_stmt2(self, line):
        line.head = 'mako_tree'

    def mako_meta_stmt(self, tree):
        stmt = tree.tail[0]
        assert stmt.startswith( '%!' )
        tree.reset('mako_tree', [stmt[2:].strip()])
    def mako_meta_oneliner(self, tree):
        [stmt] = tree.tail[0].tail
        tree.head, tree.tail = 'mako_tree', ['<%' + stmt + '/>']
    def mako_meta_block(self, tree):
        stmt = tree.tail[0].tail[0]
        control_word = stmt.split(None,1)[0]
        opener = '<%'+stmt + '>'
        closer = '</%'+control_word+'>'
        tree.reset('mako_tree', [opener] + tree.tail[1:] + [closer])

    def mako_control_block(self, tree):
        ctl_start = tree.tail[0].tail[0]
        assert ctl_start[0] == '%'
        ctl_word = ctl_start[1:].split(None,1)[0]
        ctl_end = '%end'+ctl_word

        tail = list(tree.tail)
        for ctl2_i in xrange(2, len(tail), 2):
            ctl2 = tail[ctl2_i]
            assert ctl2.head == 'mako_tree' and len(ctl2.tail) == 1
            tail[ctl2_i] = ctl2.tail[0]

        tree.reset('mako_tree', [ctl_start] + tail[1:] + [ctl_end])

class SimplifyMakoTree(plyplus.SVisitor):
    def mako_tree(self, tree):
        if all(plyplus.is_stree(kid) and kid.head=='mako_tree' for kid in tree.tail):
            new_tail = []
            for kid in tree.tail:
                new_tail += kid.tail
            tree.tail = new_tail

class MakoTreeToText(plyplus.STransformer):
    def mako_tree(self, tree):
        depth = tree.depth - 1
        indent_str = ' '*(depth*4)
        l = []
        for kid in tree.tail:
            if isinstance(kid, list):
                l += kid
            else:
                l.append(indent_str+kid)
        return l
    def start(self, tree):
        assert len(tree.tail) == 1
        return '\n'.join(tree.tail[0])

def convert(text):
    tree = hypermako_grammar.parse(text)
    HyperToMako().visit(tree)
    SimplifyMakoTree().visit(tree)
    #tree.to_png_with_pydot('hyper2.png')
    tree.calc_depth()
    return MakoTreeToText().transform( tree )

if __name__ == '__main__':
    import sys
    print convert(file(sys.argv[1]).read())
