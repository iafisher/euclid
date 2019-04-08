"""
The Euclid proof checker.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: April 2019
"""
import sys

from . import parser


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

    print("No errors were detected in the proof.")


def formula_equals(left, right):
    """Check if the two formulas are semantically identical."""
    return left == right


def error(msg):
    """Emit an error message and exit the entire program."""
    sys.stderr.write("Error: " + msg + "\n")
    sys.exit(2)
