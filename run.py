#!/usr/bin/env python3
"""
Run the Euclid proof-checker from the command line.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: April 2019
"""
import sys

from euclid.euclid import check_proof


if __name__ == "__main__":
    if len(sys.argv) > 2:
        sys.stderr.write("Usage:\n")
        sys.stderr.write(f"  {sys.argv[0]}\n")
        sys.stderr.write(f"  {sys.argv[0]} <proof-file>\n")
        sys.exit(1)

    if len(sys.argv) == 1 or sys.argv[1] == "-":
        proof = sys.stdin.read()
        # Print an extra newline so that the program output is visually separate from
        # the user input.
        print()
    else:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            proof = f.read()

    check_proof(proof)
