"""
The Euclid proof checker.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: April 2019
"""
import sys
from collections import namedtuple

from . import parser


Knowledge = namedtuple("Knowledge", ["expressions"])
Expression = namedtuple("Expression", ["properties", "equivalent"])


def check_proof(proof):
    """Check the proof for errors, emitting a message if one is found."""
    try:
        ast = parser.parse(proof)
    except SyntaxError as e:
        error(str(e))

    if not ast.clauses:
        error("the body of the proof is empty")

    if isinstance(ast.statement, parser.IfNode):
        # TODO [2019-04-07]: This doesn't work, consult double_even.prf to see why.
        if not formula_equals(ast.statement.hypothesis, ast.clauses[0].formula):
            error(
                "the first statement of the proof does not match the hypothesis of the "
                "if statement to be proven"
            )

        if not formula_equals(ast.statements.consequent, ast.clauses[-1].formula):
            error(
                "the final statement of the proof does not match the consequent to be "
                "proven"
            )
    else:
        if not formula_equals(ast.statement, ast.clauses[0].formula):
            error(
                "the final statement of the proof does not match the statement to be "
                "proven"
            )

    knowledge = Knowledge([])
    for clause in proof.clauses:
        check_clause(knowledge, clause)

    print("No errors were detected in the proof.")


def check_clause(knowledge, clause):
    if isinstance(clause, parser.FormulaClauseNode):
        if not follows(knowledge, clause.formula, clause.justification):
            error(f"{clause} does not follow, line {parser.line(clause)})")
    else:
        error(f"unknown node type {clause.__class__.__name__}", prefix="Internal error")

    update_knowledge(knowledge, clause)


def update_knowledge(knowledge, clause):
    pass


def follows(knowledge, formula, justification=None):
    """Return True if the truth of the formula follows from the given knowledge."""
    return False


def formula_equals(left, right):
    """Check if the two formulas are semantically identical."""
    return left == right


def error(msg, prefix="Error"):
    """Emit an error message and exit the entire program."""
    sys.stderr.write(f"{prefix}: {msg}\n")
    sys.exit(2)
