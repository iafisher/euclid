#!/usr/bin/env python3

import sys


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: {} <proof-file>\n".format(sys.argv[0]))
