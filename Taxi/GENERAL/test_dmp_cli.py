from dmp_suite.cli.__main__ import *

import os, sys

if __name__ == '__main__':
    environ = list(sorted(os.environ.items()))

    print('Environ:', file=sys.stderr)
    for key, value in environ:
        print(f'{key} = {value}', file=sys.stderr)

    cli()
