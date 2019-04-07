"""
proof := prove-clause clause+

prove-clause := PROVE COLON formula DOT
clause := let-clause | formula-clause | therefore-clause

let-clause := LET SYMBOL BE A compound-symbol DOT | LET SYMBOL EQ term DOT
formula-clause := (BY justification)? formula where?
therefore-clause := THEREFORE formula DOT

formula := term EQ term | term IS A compound-symbol
term := SYMBOL | NUM | NUM SYMBOL | NUM LPAREN term RPAREN | LPAREN term RPAREN

justification := DEFINITION | SUBSTITUTION
where := WHERE SYMBOL IS A compound-symbol

compound-symbol := SYMBOL+
"""
import re
from collections import namedtuple


# AST nodes for clauses
ProofNode = namedtuple("ProofNode", ["statement", "clauses"])
LetNode = namedtuple("LetNode", ["symbol", "formula"])
FormulaClauseNode = namedtuple(
    "FormulaClauseNode", ["justification", "formula", "where"]
)
ThereforeNode = namedtuple("ThereforeNode", ["formula"])

# AST nodes for formulas
EqNode = namedtuple("EqNode", ["left", "right"])
IsANode = namedtuple("IsANode", ["term", "definition"])


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


_tokenize_keywords = {"PROVE", "LET", "WHERE", "BY", "BE", "IS", "A", "AN"}
_tokenize_spec = [
    ("NUMBER", r"\d+(\.\d*)?"),
    ("DOT", r"\."),
    ("SYMBOL", r"[A-Za-z][A-Za-z0-9_]*"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
    ("MISMATCH", r"."),
]
_tokenize_regex = re.compile("|".join("(?P<%s>%s)" % pair for pair in _tokenize_spec))


def tokenize(code):
    """
    Iterate over the tokens of the code.

    Based on https://docs.python.org/3.6/library/re.html#writing-a-tokenizer
    """
    line_num = 1
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
            line_num += 1
            continue
        elif kind == "SKIP":
            continue
        elif kind == "MISMATCH":
            raise RuntimeError(f"{value!r} unexpected on line {line_num}")
        yield Token(kind, value, line_num, column)
