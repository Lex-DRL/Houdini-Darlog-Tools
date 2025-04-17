# encoding: utf-8
"""
Code, specific for exporting multi-KineFX.
"""

__author__ = 'Lex Darlog (DRL)'

import typing as _t

from os.path import commonpath

import hou

from darlog_hou.attributes_2 import find_verify, SPECIFIER_DET_STR, SPECIFIER_PRIM_STR, AttributeNotFoundError
from darlog_hou.errors import get_error_message, any_exception

win_slash = 'q\\q'[1]  # mindfuck to workaround Houdini bug when it sometimes can't just create a single backslash char
hip_pattern = "".join(['$', 'HIP'])  # Houdini expands it to the actual path, so - this workaround
hip_pattern_braces = "".join(['$', '{', 'HIP', '}'])
hip_pattern_slash = "{}/".format(hip_pattern)
hip_pattern_braces_slash = "{}/".format(hip_pattern_braces)

fbx_path_attr_nm = "fbx_path"
fbx_dir_attr_nm = "fbx_base_path"
do_dir_attr_nm = "do_extract_base_path"
renames_dict_attr_nm = "renames"


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


def detect_base_dir_path_and_renames(asset_node: hou.SopNode, in_geo: hou.Geometry, out_geo: hou.Geometry):
	path_attr = find_verify(fbx_path_attr_nm, SPECIFIER_PRIM_STR, node=asset_node, geo=in_geo, geo_from_input=0, node_in_error=False)
	fbx_paths: _t.Tuple[str, ...] = path_attr.strings()
	fbx_paths = tuple(sorted(list(set(fbx_paths))))
	try:
		base_dir_raw = str(commonpath(fbx_paths))
	except any_exception as e:
		msg = "Can't extract shared part from 'fbx_path' per-prim attribute ({}):\n{}".format(
			repr(type(e)),
			get_error_message(e, default=str(e))
		)
		raise hou.NodeError(msg)
		return

	base_dir_raw = base_dir_raw.replace(win_slash, '/')
	base_dir_no_slash = base_dir_raw.rstrip('/')
	base_dir_with_slash = "{}/".format(base_dir_no_slash) if base_dir_no_slash else ""
	if base_dir_raw and not base_dir_no_slash:
		base_dir_with_slash = base_dir_raw
	if base_dir_with_slash and not base_dir_with_slash.endswith('/'):
		base_dir_with_slash = "{}/".format(base_dir_with_slash)
	shared_prefix_n = len(base_dir_with_slash)

	renames: _t.Dict[str, str] = {
		pth: pth[shared_prefix_n:].replace(win_slash, '/').lstrip('/')
		for pth in fbx_paths
	}

	invalid_renames: _t.List[_t.Tuple[str, str]] = [
		(ren_from, ren_to)
		for ren_from, ren_to in renames.items()
		if not ren_to or ren_to.startswith(hip_pattern_slash) or ren_to.startswith(hip_pattern_braces)
	]
	if invalid_renames:
		if len(invalid_renames) == 1:
			r_from, r_to = invalid_renames[0]
			raise hou.NodeError(
				"Invalid output sub-path:\n{} (from {})".format(repr(r_to), repr(r_from))
			)
			return
		wrong_rename_strings = [
			" {} (from {})".format(repr(ren_to), repr(ren_from))
			for ren_from, ren_to in invalid_renames
		]
		msg = "Invalid output sub-paths:\n{}".format("\n".join(wrong_rename_strings))
		raise hou.NodeError(msg)
		return

	out_geo.setGlobalAttribValue(fbx_dir_attr_nm, base_dir_no_slash)
	out_geo.setGlobalAttribValue(renames_dict_attr_nm, renames)

