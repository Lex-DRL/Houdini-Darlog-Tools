# encoding: utf-8
"""
Python code for various `multiKineFX*` SOP nodes.
"""

__author__ = 'Lex Darlog (DRL)'

import typing as _t

import hou

from darlog_hou.attributes_2 import find_verify, SPECIFIER_PRIM_STR
from darlog_hou.errors import get_error_message, any_exception

char_type_attr_nm = "character_type"
fbx_path_attr_nm = "fbx_path"

required_prim_str_attribs = (char_type_attr_nm, fbx_path_attr_nm)


def _get_prim_str_attr(attr_nm: str, asset_node: hou.SopNode, geo: hou.Geometry) -> hou.Attrib:
	return find_verify(attr_nm, SPECIFIER_PRIM_STR, node=asset_node, geo=geo, geo_from_input=0, node_in_error=False)


def verify_input(asset_node: hou.SopNode, python_node_geo: hou.Geometry):
	"""Ensure that input has primitive attributes essential for all `multiKineFX*` nodes."""
	raised = False
	for attr_nm in required_prim_str_attribs:
		try:
			_get_prim_str_attr(attr_nm, asset_node, python_node_geo)
		except any_exception as e:
			msg = get_error_message(e, default=str(e))
			raised = True
			raise hou.NodeError(msg)
	if raised:
		return
	path_attr = _get_prim_str_attr(fbx_path_attr_nm, asset_node, python_node_geo)
	fbx_paths: _t.Tuple[str, ...] = tuple(path_attr.strings())
	if not fbx_paths:
		raise hou.NodeError(
			"No paths found in {} prim-attribute (no primitives in geo)".format(repr(fbx_path_attr_nm))
		)
