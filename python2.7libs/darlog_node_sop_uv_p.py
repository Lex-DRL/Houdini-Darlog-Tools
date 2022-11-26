# encoding: utf-8
"""
Python code for `uvP` sop node.
"""

__author__ = 'Lex Darlog (DRL)'

import hou
from darlog_hou.attributes import CommonAttribsValidator


_sizes = (2, 3, 4)


# Just to keep dependencies from the rest of codebase here (and not in the node itself):
def main(
	node,  # type: hou.SopNode
	attr_name,  # type: str
):
	CommonAttribsValidator(
		node
	).test_uv(
		attr_name,
		sizes=_sizes, allow_pt=False
	)
