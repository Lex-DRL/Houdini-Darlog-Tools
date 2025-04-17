# encoding: utf-8
"""
Code, specific for exporting multi-KineFX.
"""

__author__ = 'Lex Darlog (DRL)'

import hou

from darlog_hou.attributes_2 import find_verify, SPECIFIER_DET_STR, AttributeNotFoundError
from darlog_hou.errors import get_error_message, any_exception


fbx_dir_attr_nm = "fbx_base_path"
do_dir_attr_nm = "do_extract_base_path"


def detect_if_do_extract_dir_attr(asset_node: hou.SopNode, in_geo: hou.Geometry, out_geo: hou.Geometry):
	do_restore = 0
	try:
		find_verify(fbx_dir_attr_nm, SPECIFIER_DET_STR, node=asset_node, geo=in_geo, geo_from_input=0, node_in_error=False)
	except AttributeNotFoundError:
		do_restore = 1
	except any_exception as e:
		msg = get_error_message(e, default=str(e))
		raise hou.NodeError(msg)
		return
	out_geo.setGlobalAttribValue(do_dir_attr_nm, do_restore)
