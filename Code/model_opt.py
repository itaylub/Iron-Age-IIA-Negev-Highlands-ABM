"""Backwards-compatibility shim.

The canonical module is :mod:`nomad_abm.model`. This file re-exports
its public names so existing notebooks that say
``from model_opt import run_model_opt`` continue to work after the
Phase 6 package layout move.

To use the new layout directly::

    from nomad_abm.model import run_model_opt, NomadModel

This shim will be removed in a future release.
"""

import os
import sys

# Make `nomad_abm` importable from a fresh clone even without
# `pip install -e .` having been run yet.
_SRC = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"
)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from nomad_abm.model import *  # noqa: E402,F401,F403
