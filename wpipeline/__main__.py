"""Entry point for `python3 -m wpipeline`.

No installation step. The package is used from the repo, which is the same
mechanism Houdini will use to find it: a PYTHONPATH pointing here. One
mechanism instead of two.
"""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
