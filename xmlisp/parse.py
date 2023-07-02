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
CLOSE   : /<\/[^>]*>/

ignored : expr
?expr   : SIGNED_NUMBER -> number
        | ESCAPED_STRING -> string
        | CNAME -> atom
        | expr "=" expr -> pair
        | "<" expr+ "/>" -> list
        | "<" expr* ">" document CLOSE -> tag

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


def indent(text, indentation=" " * 4):
    return indentation + text.replace("\n", "\n" + indentation)


class Tag:
    def __init__(self, props, children):
        self.props = props
        self.children = children

    def __repr__(self):
        if len(self.props) == 0 and len(self.children) == 0:
            return "<></>"

        if self.children:
            if len(self.props) > 0 and isinstance(self.props[0], Atom):
                closing = repr(self.props[0])
            else:
                closing = ""
            return "\n".join([
                "<" + " ".join(map(repr, self.props)) + ">",
                *[indent(repr(child)) for child in self.children],
                "</" + closing + ">"])

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
