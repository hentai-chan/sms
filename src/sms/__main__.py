#!/usr/bin/env python3

from .cli import cli

if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        pass