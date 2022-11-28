# encoding: utf-8
"""
Service module for installing pip itself and other dependencies.
"""

# This module __MUST__ rely only on builtins, no external dependencies, and also must work under Py2/3.

from .__main_class import Pip
from .__versions import flat_version_gen, verify_version
