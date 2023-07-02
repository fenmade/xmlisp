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


class Tag:
    def __init__(self, props, children):
        self.props = props
        self.children = children

    def __repr__(self):
        if len(self.props) == 0 and len(self.children) == 0:
            return "<></>"

        if self.children:
            closing = repr(self.props[0]) if len(self.props) > 0 else ""
            return (
                "<" + " ".join(map(repr, self.props)) + ">" +
                "\n".join(map(repr, self.children)) +
                "</" + closing + ">")

        return "<" + " ".join(map(repr, self.props)) + " />"

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.props == other.props and
            self.children == other.children)


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
        return Tag(args, [])

    def ignored(self, args):
        return None

    def tag(self, args):
        if args[-1] is None:
            args.pop(-1)
        children = args.pop(-1)
        return Tag(args, children)

    def document(self, args):
        return args


parser = Lark(
    grammar,
    parser="lalr",
    start="document",
    transformer=SyntaxTransformer())
