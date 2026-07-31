"""Make `build_i18n` importable however pytest is invoked.

conftest is loaded before any test module, so the package resolves whether the
suite is started as `pytest`, `pytest tests/test_render.py`, or from another
directory entirely.  `support` itself is found by pytest, which puts this
directory on the path when it collects the tests beside it.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
