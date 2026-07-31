"""Make the repository root importable however pytest is invoked.

conftest is loaded before any test module, so `build_i18n` resolves whether the
suite is started as `pytest`, `pytest tests/test_render.py`, or from another
directory entirely.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
