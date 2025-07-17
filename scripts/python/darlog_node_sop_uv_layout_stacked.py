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


_catch_error = catch_and_return_error_message(format=':{}')


@_catch_error
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


@_catch_error
def test_out_group_attribs(
	main_meta,  # type: str
	cell_do,  # type: bool
	cell_attr_nm,  # type: str
	island_do,  # type: bool
	island_attr_nm,  # type: str
):
	if main_meta.startswith(':'):
		return '/'
	in_uv, in_uv_size, out_uv = main_meta.split('/')

	if cell_do:
		cell_attr_nm = test_name_p_reserved(cell_attr_nm, 'UV-cell', split_by_spaces=True)
		if cell_attr_nm == out_uv:
			raise ValueError(_format("Can't use '{}' as UV-cell attribute: it's the name of output UVs", cell_attr_nm))
	else:
		cell_attr_nm = ''

	if island_do:
		island_attr_nm = test_name_p_reserved(island_attr_nm, 'UV-island', split_by_spaces=True)
		for existing_val, existing_label in [
			(out_uv, 'output UVs'),
			(cell_attr_nm, 'UV-cell attribute'),
		]:
			if island_attr_nm == existing_val:
				raise ValueError(_format(
					"Can't use '{}' as UV-island attribute: it's the name of {}",
					island_attr_nm, existing_label
				))
	else:
		island_attr_nm = ''

	return _format('{}/{}', cell_attr_nm, island_attr_nm)
