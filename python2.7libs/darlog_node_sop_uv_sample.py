# encoding: utf-8
"""
Python code for `uvLayoutStacked` sop node.
"""

__author__ = 'Lex Darlog (DRL)'

import hou

from darlog_hou.attributes import (
	AttribFuncsPerGeo,
	test_name_no_reserved, test_name_p_reserved,
	attr_vex_literal,
	is_safe_promote
)
from darlog_hou.errors import catch_and_return_error_message, sop_input_geo
from darlog_hou.py23 import str_format as _format


def _get_uv_attr(
	node_with_inputs,  # type: hou.SopNode
	attr_name,  # type: str
	index,  # type: int
	input_name,  # type: str
):
	in_geo = sop_input_geo(node_with_inputs, index)
	attr_funcs = AttribFuncsPerGeo(in_geo)
	attr = attr_funcs.attr_test(
		attr_name, data_types=hou.attribData.Float, sizes=3,
		error_attr_nice_nm=_format('Matched UV (on {})', input_name),
		test_name_f=test_name_no_reserved
	)
	return attr, attr_funcs


_attr_class_enum = (
	hou.attribType.Global,
	hou.attribType.Prim,
	hou.attribType.Point,
	hou.attribType.Vertex
)
_attr_class_int = {
	v: i for i, v in enumerate(_attr_class_enum)
}


_catch_error = catch_and_return_error_message(format=':{}')


@_catch_error
def test_uv_and_out_attrs(
	node_with_inputs,  # type: hou.SopNode
	uv_attr_name,  # type: str
	out_attr_name,  # type: str
):
	"""
	No errors:
		- 'uv_attr/(int)in_passed_class/(int)out_class/out_attr/out_attr_type_literal'
		- 'uv/2/3/Cd/v' = transfer point (2) v@Cd from source-geo - to vertex (3), because target-UVs are per-vertex.

	On error:
		- ':...', where '...' is an error message (might be empty).
	"""
	uv_trg_attr, _ = _get_uv_attr(node_with_inputs, uv_attr_name, 0, 'target')
	uv_attr_name = uv_trg_attr.name()
	uv_src_attr, src_geo_funcs = _get_uv_attr(node_with_inputs, uv_attr_name, 1, 'source')

	passed_attr = src_geo_funcs.attr_test(
		out_attr_name, data_types=None, sizes=None, is_array=None,
		error_attr_nice_nm='Passed', test_name_f=test_name_no_reserved
	)
	out_attr_name = passed_attr.name()
	if out_attr_name == uv_attr_name:
		raise ValueError(_format(
			"'{}' can't be both a matching UV and a passed attribute",
			out_attr_name
		))

	in_class = passed_attr.type()
	out_class = uv_trg_attr.type()

	# Technically, we might have a class mismatch between source/target geo.
	# But let's assume a user knows what they do to make the node less picky/restrictive.

	# if not is_safe_promote(uv_src_attr.type(), out_class):
	# 	raise ValueError(_format(
	# 		"Matched UV attribute '{}' is {{{}}} on source geo, but {{{}}} on target geo",
	# 		uv_attr_name, uv_src_attr.type(), out_class
	# 	))
	# if not is_safe_promote(in_class, out_class):
	# 	raise ValueError(_format(
	# 		"Transferred attribute '{}' is {{{}}}, while matched UV attribute '{}' is {{{}}} on target geo",
	# 		out_attr_name, in_class, uv_attr_name, out_class
	# 	))

	return _format(
		'{}/{}/{}/{}/{}',
		uv_attr_name, _attr_class_int[in_class], _attr_class_int[out_class], out_attr_name, attr_vex_literal(passed_attr)
	)


def _get_piece_attr(
	node_with_inputs,  # type: hou.SopNode
	attr_name,  # type: str
	attr_types,
	index,  # type: int
	input_name,  # type: str
):
	in_geo = sop_input_geo(node_with_inputs, index)
	attr_funcs = AttribFuncsPerGeo(in_geo, attr_types=attr_types)
	attr = attr_funcs.attr_test(
		attr_name, data_types=(hou.attribData.Int, hou.attribData.String), sizes=1,
		error_attr_nice_nm=_format('Piece (on {})', input_name),
		test_name_f=test_name_no_reserved
	)
	return attr


def _piece_attr_class_int(
	piece_attr,  # type: hou.Attrib
):  # type: (...) -> int
	piece_class = piece_attr.type()
	# Technically, we might perform unsafe promote from prim to point or vice versa...
	# But in such a case, let's assume the user knows what they do.
	# Because otherwise, we'll have an error when trying to sample by point UVs on target, with prim piece.
	return _attr_class_int[piece_class]


@_catch_error
def test_piece_attr(
	node_with_inputs,  # type: hou.SopNode
	piece_do,  # type: bool
	piece_attr_name,  # type: str
	main_attrs_str,  # type: str
):
	"""
	No errors:
		- 'piece_attr(can be empty)/(int)src_class/type_literal'

	On error:
		- ':...', where '...' is an error message (might be empty).
	"""
	if not piece_do or main_attrs_str.startswith(':'):
		return '/0/i'

	uv_attr_name, in_class_str, out_class_str, out_attr_name, out_type = main_attrs_str.split('/')
	# out_class = _attr_class_enum[int(out_class_str)]

	piece_attr_name = test_name_p_reserved(piece_attr_name, 'Piece', split_by_spaces=True)

	for used_nm, used_label in [
		(uv_attr_name, 'matched-UV'),
		(out_attr_name, 'transferred'),
	]:
		if piece_attr_name == used_nm:
			raise ValueError(_format(
				"Can't use '{}' as piece attribute: it's a {} attribute",
				piece_attr_name, used_label
			))

	src_piece_attr = _get_piece_attr(node_with_inputs, piece_attr_name, hou.attribType.Prim, 1, 'source')
	trg_piece_attr = _get_piece_attr(node_with_inputs, piece_attr_name, None, 0, 'target')
	trg_piece_class_i = _piece_attr_class_int(trg_piece_attr)

	piece_dt = trg_piece_attr.dataType()
	if src_piece_attr.dataType() != piece_dt:
		raise ValueError(_format(
			"'{}' piece attribute is {{{}}} on source mesh, but {{{}}} on target",
			piece_attr_name, src_piece_attr.dataType(), piece_dt
		))

	return _format('{}/{}/{}', piece_attr_name, trg_piece_class_i, attr_vex_literal(trg_piece_attr))
