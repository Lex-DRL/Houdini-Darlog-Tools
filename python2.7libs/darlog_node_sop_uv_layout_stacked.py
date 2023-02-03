# encoding: utf-8
"""
Python code for `uvLayoutStacked` sop node.
"""

__author__ = 'Lex Darlog (DRL)'

import hou

from darlog_hou.attributes import AttribFuncsPerGeo, test_name_p_reserved
from darlog_hou.errors import catch_and_return_error_message, sop_input_geo
from darlog_hou.py23 import str_format as _format


_sizes = (2, 3, 4)


@catch_and_return_error_message(format=':{}')
def test_in_out_uv_attrs(
	node_with_input,  # type: hou.SopNode
	uv_attr_nm,  # type: str
	out_uv_attr_nm,  # type: str
):
	uv_attr_nm = test_name_p_reserved(uv_attr_nm, 'input UV', split_by_spaces=True)
	out_uv_attr_nm = test_name_p_reserved(out_uv_attr_nm, 'output UV', split_by_spaces=True)

	in_geo = sop_input_geo(node_with_input, 0)
	uv_attr = AttribFuncsPerGeo(in_geo, hou.attribType.Vertex).attr_test(
		uv_attr_nm, data_types=hou.attribData.Float, sizes=_sizes,
		error_attr_nice_nm='input UV'
	)

	return _format('{}/{}/{}', uv_attr.name(), uv_attr.size(), out_uv_attr_nm)
