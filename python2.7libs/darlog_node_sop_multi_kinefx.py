# encoding: utf-8
"""
Python code for various `multiKineFX*` SOP nodes.
"""

__author__ = 'Lex Darlog (DRL)'

import hou

from darlog_hou.attributes_2 import find_verify, SPECIFIER_PRIM_STR
from darlog_hou.errors import get_error_message, any_exception

char_type_attr_nm = "character_type"
fbx_path_attr_nm = "fbx_path"

required_prim_str_attribs = (char_type_attr_nm, fbx_path_attr_nm)


def verify_input(asset_node: hou.SopNode, python_node_geo: hou.Geometry):
	"""Ensure that input has primitive attributes essential for all `multiKineFX*` nodes."""
	for attr_nm in required_prim_str_attribs:
		try:
			find_verify(attr_nm, SPECIFIER_PRIM_STR, node=asset_node, geo=python_node_geo, geo_from_input=0, node_in_error=False)
		except any_exception as e:
			msg = get_error_message(e, default=str(e))
			raise hou.NodeError(msg)
