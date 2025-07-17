# encoding: utf-8
"""
Python code for `inlinePtDel` sop node.
"""

__author__ = 'Lex Darlog (DRL)'

import hou

from darlog_hou.attributes import AttribFuncsPerGeo
from darlog_hou.errors import catch_and_return_error_message, sop_input_geo


@catch_and_return_error_message(format='___drl_tmp_inline')
def inline_attr_name(
	node_with_input,  # type: hou.SopNode
):
	in_geo = sop_input_geo(node_with_input, 0)
	return AttribFuncsPerGeo(in_geo).next_free_name('inline', 'internal inline')
