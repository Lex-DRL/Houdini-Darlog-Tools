# encoding: utf-8
"""
Python code for `mobileVAT` rop node.
"""

__author__ = 'Lex Darlog (DRL)'

import hou

import typing as _t

from enum import IntEnum
from json import load

from darlog_hou.attributes_2 import AttributeTypeSpecifier, find_verify as _find_verify
from darlog_hou.attributes_meta import catch_error_to_attr


class PosMode(IntEnum):
	HDR = 0
	LDR = 1
	LDR2 = 2


@catch_error_to_attr
def load_json_config_to_detail_attribs(node: hou.SopNode, geo: hou.Geometry, json_file_path: str,) -> None:
	with open(json_file_path, 'r') as f:
		data = load(f)
	pos_unpack = data['pos_unpack']
	p_min, p_size = [
		tuple(float(x) for x in p[:3])
		for p in (
			pos_unpack['min'], pos_unpack['size']
		)
	]
	geo.setGlobalAttribValue('p_min', p_min)
	geo.setGlobalAttribValue('p_size', p_size)


@catch_error_to_attr
def verify_images_exist(
	node: hou.SopNode, geo: hou.Geometry,
	pos_mode: PosMode, path_pos_hdr: str, path_pos: str, path_pos2: str, path_rot: str,
	try_read_bytes: int = 4,
) -> None:
	@catch_error_to_attr
	def read_single_file_or_error(_node: hou.SopNode, _geo: hou.Geometry, file_path: str):
		with open(file_path, 'rb') as f:
			return f.read(try_read_bytes)

	if not isinstance(pos_mode, PosMode):
		pos_mode = PosMode(pos_mode)

	pos_main_tex = path_pos_hdr if pos_mode == PosMode.HDR else path_pos

	used_files = [pos_main_tex, path_pos2] if pos_mode == PosMode.LDR2 else [pos_main_tex, ]
	used_files.append(path_rot)

	for path in used_files:
		# Do nothing, just try reading the file:
		_ = read_single_file_or_error(node, geo, path)

	geo.setGlobalAttribValue('p_main_tex', pos_main_tex)


@catch_error_to_attr(skip_if_pre_error=True)
def detect_vat_size(
	node: hou.SopNode, geo: hou.Geometry,
	cop_tex: hou.CopNode,
):
	n_pieces = int(cop_tex.xRes())
	n_frames = int(cop_tex.yRes())

	for n, what in [
		(n_pieces, 'pieces'),
		(n_frames, 'frames'),
	]:
		if n < 2:
			raise ValueError("Incorrect number of {} in pos-VAT: {} (min: 2)".format(what, n))

	geo.setGlobalAttribValue('n_pieces', n_pieces)
	geo.setGlobalAttribValue('n_frames', n_frames)


_attr_promote_mode = {
	hou.attribType.Point: 0,
	hou.attribType.Prim: 1,
	hou.attribType.Global: 2,
}
_attr_cls_priority = (hou.attribType.Point, hou.attribType.Prim, hou.attribType.Global)


@catch_error_to_attr
def _verify_attr(
	node: hou.SopNode, geo: hou.Geometry, asset: hou.SopNode, in_geo: hou.Geometry,
	name: str, specifier: AttributeTypeSpecifier, meta_attr_name: str, meta_attr_class: str, error_multi: bool = False,
):
	attr = _find_verify(
		name=name, specifier=specifier, node=asset, geo=in_geo, geo_from_input=1,
		error_multi=error_multi, node_in_error=False
	)
	geo.setGlobalAttribValue(meta_attr_name, attr.name())
	geo.setGlobalAttribValue(meta_attr_class, _attr_promote_mode.get(attr.type(), 3))


_piece_specifier = AttributeTypeSpecifier.from_unsafe_args(_attr_cls_priority, hou.attribData.Int, 1, is_array=False)
_pivot_specifier = AttributeTypeSpecifier.from_unsafe_args(_attr_cls_priority, hou.attribData.Float, 3, is_array=False)


def verify_piece_attr(
	node: hou.SopNode, geo: hou.Geometry,  # META branch
	asset: hou.SopNode, in_geo: hou.Geometry,  # actual input SOPs
	name: str, meta_attr_name: str = 'attr_piece', meta_attr_class: str = 'attr_piece_cls',
):
	return _verify_attr(node, geo, asset, in_geo, name, _piece_specifier, meta_attr_name, meta_attr_class)


def verify_pivot_attr(
	node: hou.SopNode, geo: hou.Geometry,  # META branch
	asset: hou.SopNode, in_geo: hou.Geometry,  # actual input SOPs
	name: str, meta_attr_name: str = 'attr_pivot', meta_attr_class: str = 'attr_pivot_cls',
):
	return _verify_attr(node, geo, asset, in_geo, name, _pivot_specifier, meta_attr_name, meta_attr_class)
