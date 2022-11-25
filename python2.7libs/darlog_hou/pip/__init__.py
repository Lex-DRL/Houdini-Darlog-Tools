# encoding: utf-8
"""
Service module for installing pip itself and other dependencies.
"""

# This module __MUST__ rely only on builtins, no external dependencies, and also must work under Py2/3.
# Therefore, some cumbersome and hacky jumping through the hoops is in place.

import sys as __sys

if __sys.version_info.major == 2:
	from .__py2 import Pip
else:
	from .__py3 import Pip
