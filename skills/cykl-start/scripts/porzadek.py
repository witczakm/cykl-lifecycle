#!/usr/bin/env python3
"""Retired v2 compatibility entry point: deliberately incapable of writing."""
import sys

if __name__ == '__main__':
    print('porzadek.py is retired. Use lifecycle.py check or migrate (dry-run default).', file=sys.stderr)
    sys.exit(2)
