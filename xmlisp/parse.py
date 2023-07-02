import ast
from lark import Lark
from lark.visitors import Transformer


grammar = r"""
%import common.WS
%import common.SIGNED_NUMBER
%import common.ESCAPED_STRING
%import common.CNAME

%ignore WS
%ignore COMMENT

COMMENT : /<!--[^\n]*-->/

ignored : expr
?expr   : SIGNED_NUMBER -> number
        | ESCAPED_STRING -> string
        | CNAME -> atom
        | expr "=" expr -> pair
        | "<" expr+ "/>" -> list
        | "<" expr* ">" document "</" ignored? ">" -> tag

document: expr*
"""


class Atom:
    def __init__(self, identifier):
        self.identifier = identifier

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.identifier == other.identifier)

    def __repr__(self):
        return self.identifier


class List(list):
    @classmethod
    def is_children(cls, object):
        return (
            isinstance(object, cls) and
            len(object) == 2 and
            object[0] == ...)

    def __init__(self, iterable):
        items = list(iterable)
        if self.__class__.is_children(items[-1]):
            self.children = items[-1][1]
            items.pop(-1)
        else:
            self.children = []
        super().__init__(items)

    def __repr__(self):
        if len(self) == 0 and len(self.children) == 0:
            return "<></>"

        if self.children != []:
            return (
                "<" + " ".join(map(repr, self)) + ">" +
                "\n".join(map(repr, self.children)) +
                "</" + (repr(self[0]) if len(self) > 0 else "") + ">")

        return "<" + " ".join(map(repr, self)) + " />"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return super().__eq__(other) and self.children == other.children
        return super().__eq__(other)


class SyntaxTransformer(Transformer):
    def number(self, args):
        return float(args[0])

    def string(self, args):
        return ast.literal_eval(args[0])

    def atom(self, args):
        return Atom(args[0])

    def pair(self, args):
        return self.list([Atom("pair")] + args)

    def list(self, args):
        return List(args)

    def ignored(self, args):
        return None

    def tag(self, args):
        if len(args) == 0:
            return self.list(args)
        if args[-1] is None:
            args.pop(-1)
        children = args.pop(-1)
        return self.list(args + [List([..., children])])

    def document(self, args):
        return args


parser = Lark(
    grammar,
    parser="lalr",
    start="document",
    transformer=SyntaxTransformer())
