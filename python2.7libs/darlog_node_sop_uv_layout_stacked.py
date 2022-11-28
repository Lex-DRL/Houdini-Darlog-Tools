# encoding: utf-8
"""
Python code for `uvLayoutStacked` sop node.
"""

__author__ = 'Lex Darlog (DRL)'

import hou

from collections import OrderedDict
from json import dumps

from darlog_hou.attributes import CommonAttribsValidator, test_name_p_reserved
from darlog_hou.errors import catch_error_message


_sizes = (2, 3, 4)


def json_str(
	node,  # type: hou.SopNode
	uv_attr,  # type: str
	out_uv_attr,  # type: str
):
	def _main():
		CommonAttribsValidator(
			node
		).test_uv(
			uv_attr,
			sizes=_sizes, allow_pt=False
		)
		test_name_p_reserved(out_uv_attr, 'out-UV')

	caught_error, msg = catch_error_message(_main, '')

	return dumps(
		OrderedDict([
			('is_error', caught_error is not None),
			('error', msg),
		]),
		# indent=2,
	)
