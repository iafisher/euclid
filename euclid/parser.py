"""
Parse a proof into an abstract syntax tree.

The concrete grammar of the proof language is given below. It is intended to be similar
in format to regular, English-language proofs.


    proof := prove-clause clause*

    prove-clause := PROVE COLON formula DOT
    clause := let-clause | formula-clause | therefore-clause

    let-clause := LET SYMBOL BE A compound-symbol DOT | LET SYMBOL EQ term DOT
    formula-clause := (BY justification)? formula where? DOT
    therefore-clause := THEREFORE formula DOT

    formula := term OP term
             | term IS A compound-symbol
             | IF formula THEN formula

    term := SYMBOL
          | NUMBER
          | NUMBER SYMBOL
          | NUMBER LPAREN term RPAREN
          | LPAREN term RPAREN

    justification := DEFINITION | SUBSTITUTION
    where := WHERE SYMBOL IS A compound-symbol

    compound-symbol := SYMBOL+


Author:  Ian Fisher (iafisher@protonmail.com)
Version: April 2019
"""
import re
from collections import namedtuple


def parse(code):
    """Parse the code into an abstract syntax tree."""
    # We inefficiently load the entire token list into memory (instead of tokenizing
    # incrementally), reverse it, and then pop tokens off the back as we consume them.
    tokens = list(tokenize(code))
    tokens.reverse()
    return match_proof(tokens)


def match_proof(tokens):
    statement = match_proof_statement(tokens)
    clauses = []
    while tokens:
        clauses.append(match_clause(tokens))
    return ProofNode(statement, clauses)


def match_proof_statement(tokens):
    check_token_and_pop(tokens, "PROVE")
    check_token_and_pop(tokens, "COLON")
    formula = match_formula(tokens)
    check_token_and_pop(tokens, "DOT")
    return formula


def match_clause(tokens):
    if check_token(tokens, "LET"):
        return match_let_clause(tokens)
    elif check_token(tokens, "THEREFORE"):
        return match_therefore_clause(tokens)
    else:
        return match_formula_clause(tokens)


def match_let_clause(tokens):
    check_token_and_pop(tokens, "LET")
    symbol = check_token_and_pop(tokens, "SYMBOL")
    if check_token(tokens, "EQ"):
        tokens.pop()
        term = match_term(tokens)
        check_token_and_pop(tokens, "DOT")
        return LetNode(symbol, term)
    else:
        check_token_and_pop(tokens, "BE")
        check_token_and_pop(tokens, "A")
        compound_symbol = match_compound_symbol(tokens)
        check_token_and_pop(tokens, "DOT")
        return LetNode(symbol, CompoundSymbolNode(compound_symbol))


def match_therefore_clause(tokens):
    check_token_and_pop(tokens, "THEREFORE")
    formula = match_formula(tokens)
    check_token_and_pop(tokens, "DOT")
    return ThereforeNode(formula)


def match_formula_clause(tokens):
    if check_token(tokens, "BY"):
        tokens.pop()
        justification = match_justification(tokens)
    else:
        justification = None

    formula = match_formula(tokens)

    if check_token(tokens, "WHERE"):
        where = match_where_clause(tokens)
    else:
        where = None

    check_token_and_pop(tokens, "DOT")
    return FormulaClauseNode(justification, formula, where)


def match_justification(tokens):
    if check_token(tokens, "DEFINITION"):
        return tokens.pop()
    else:
        return check_token_and_pop(tokens, "SUBSTITUTION")


def match_where_clause(tokens):
    check_token_and_pop(tokens, "WHERE")
    symbol = check_token_and_pop(tokens, "SYMBOL")
    check_token_and_pop(tokens, "BE")
    check_token_and_pop(tokens, "A")
    compound_symbol = match_compound_symbol(tokens)
    return WhereNode(symbol, compound_symbol)


def match_compound_symbol(tokens):
    first = check_token_and_pop(tokens, "SYMBOL")
    compound_symbol = [first]
    while check_token(tokens, "SYMBOL"):
        compound_symbol.append(tokens.pop())
    return CompoundSymbolNode(compound_symbol)


def match_formula(tokens):
    if check_token(tokens, "IF"):
        tokens.pop()
        hypothesis = match_formula(tokens)
        check_token_and_pop(tokens, "THEN")
        consequent = match_formula(tokens)
        return IfNode(hypothesis, consequent)
    else:
        term = match_term(tokens)
        if check_token(tokens, "EQ"):
            tokens.pop()
            right = match_term(tokens)
            return OpNode("=", term, right)
        else:
            check_token_and_pop(tokens, "BE")
            check_token_and_pop(tokens, "A")
            compound_symbol = match_compound_symbol(tokens)
            return IsANode(term, compound_symbol)


def match_term(tokens):
    if check_token(tokens, "SYMBOL"):
        return SymbolNode(tokens.pop())
    elif check_token(tokens, "NUMBER"):
        left = NumberNode(tokens.pop())
        if check_token(tokens, "SYMBOL"):
            right = SymbolNode(tokens.pop())
            return OpNode("*", left, right)
        elif check_token(tokens, "LPAREN"):
            tokens.pop()
            right = match_term(tokens)
            check_token_and_pop(tokens, "RPAREN")
            return OpNode("*", left, right)
        else:
            return left
    else:
        check_token_and_pop(tokens, "LPAREN")
        term = match_term(tokens)
        check_token_and_pop(tokens, "RPAREN")
        return term


def check_token(tokens, expected_type):
    """
    Return a boolean indicating whether the next token in the token list matches the
    expected type.
    """
    return tokens and tokens[-1].type == expected_type


def check_token_and_pop(tokens, expected_type):
    """
    If the next token in the token list does not match the expected type, raise an
    error. Otherwise, pop it and return it.
    """
    if not tokens:
        raise SyntaxError("premature end of input")

    if tokens[-1].type != expected_type:
        raise SyntaxError(
            "got {0.type}, expected {1}, line {0.line} col {0.column}".format(
                tokens[-1], expected_type
            )
        )

    return tokens.pop()


# AST nodes for clauses
ProofNode = namedtuple("ProofNode", ["statement", "clauses"])
LetNode = namedtuple("LetNode", ["symbol", "formula"])
FormulaClauseNode = namedtuple(
    "FormulaClauseNode", ["justification", "formula", "where"]
)
ThereforeNode = namedtuple("ThereforeNode", ["formula"])
WhereNode = namedtuple("WhereNode", ["symbol", "formula"])

# AST nodes for formulas
IfNode = namedtuple("IfNode", ["hypothesis", "consequent"])
OpNode = namedtuple("OpNode", ["op", "left", "right"])
IsANode = namedtuple("IsANode", ["term", "definition"])
CompoundSymbolNode = namedtuple("CompoundSymbolNode", ["components"])
NumberNode = namedtuple("NumberNode", ["number"])
SymbolNode = namedtuple("SymbolNode", ["symbol"])


class Token(namedtuple("Token", ["type", "value", "line", "column"])):
    def __new__(cls, type, value, line=None, column=None):
        return super(Token, cls).__new__(cls, type, value, line, column)

    def __eq__(self, other):
        # Do not check line and column for equality.
        return (
            isinstance(other, Token)
            and self.type == other.type
            and self.value == other.value
        )


_tokenize_keywords = {
    "PROVE",
    "LET",
    "WHERE",
    "BY",
    "BE",
    "IS",
    "A",
    "AN",
    "DEFINITION",
    "SUBSTITUTION",
    "IF",
    "THEN",
    "THEREFORE",
}
_tokenize_spec = [
    ("NUMBER", r"\d+(\.\d*)?"),
    ("EQ", r"="),
    ("COLON", r":"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("DOT", r"\."),
    ("SYMBOL", r"[A-Za-z][A-Za-z0-9_]*"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ ,\t]+"),
    ("MISMATCH", r"."),
]
_tokenize_regex = re.compile("|".join("(?P<%s>%s)" % pair for pair in _tokenize_spec))


def tokenize(code):
    """
    Iterate over the tokens of the code.

    Based on https://docs.python.org/3.6/library/re.html#writing-a-tokenizer
    """
    lineno = 1
    line_start = 0
    for mo in _tokenize_regex.finditer(code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        if kind == "NUMBER":
            value = float(value) if "." in value else int(value)
        elif kind == "SYMBOL" and value.upper() in _tokenize_keywords:
            kind = value.upper()
            if kind == "IS":
                kind = "BE"
            elif kind == "AN":
                kind = "A"
        elif kind == "NEWLINE":
            line_start = mo.end()
            lineno += 1
            continue
        elif kind == "SKIP":
            continue
        elif kind == "MISMATCH":
            raise SyntaxError(f"{value!r} unexpected on line {lineno}, col {column}")
        yield Token(kind, value, lineno, column)


def line(node):
    """Return the line number of the node."""
    if isinstance(node, LetNode):
        return line(node.symbol)
    elif isinstance(node, FormulaClauseNode):
        return line(node.formula)
    elif isinstance(node, ThereforeNode):
        return line(node.formula)
    elif isinstance(node, WhereNode):
        return line(node.symbol)
    elif isinstance(node, IfNode):
        return line(node.hypothesis)
    elif isinstance(node, OpNode):
        return line(node.left)
    elif isinstance(node, IsANode):
        return line(node.term)
    elif isinstance(node, CompoundSymbolNode):
        return line(node.components[0])
    elif isinstance(node, NumberNode):
        return node.number.line
    elif isinstance(node, SymbolNode):
        return node.symbol.line
    else:
        raise RuntimeError(f"unknown node type {node.__class__.__name__}")
