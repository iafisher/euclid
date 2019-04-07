#!/usr/bin/env python3

import sys

from euclid.euclid import check_proof


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: {} <proof-file>\n".format(sys.argv[0]))
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        check_proof(f.read())
