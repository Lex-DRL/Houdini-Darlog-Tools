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
	"""Set detail flag-attrib, which identifies if we need to restore (extract) base-dir attr."""
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


def _get_fbx_path_strings(asset_node: hou.SopNode, in_geo: hou.Geometry) -> _t.Tuple[str, ...]:
	path_attr = find_verify(
		fbx_path_attr_nm, SPECIFIER_PRIM_STR, node=asset_node, geo=in_geo, geo_from_input=0, node_in_error=False
	)
	fbx_paths: _t.Tuple[str, ...] = path_attr.strings()
	return tuple(sorted(list(set(fbx_paths))))


def _is_fbx_sub_path_invalid(fbx_path: str) -> bool:
	return (not fbx_path) or fbx_path.startswith(hip_pattern_slash) or fbx_path.startswith(hip_pattern_braces)


def detect_base_dir_path_and_renames(asset_node: hou.SopNode, in_geo: hou.Geometry, out_geo: hou.Geometry):
	"""When extracting base-dir, detect it (in meta-network) + plan renames of the actual fbx-path attr."""
	fbx_paths = _get_fbx_path_strings(asset_node, in_geo)
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
		if _is_fbx_sub_path_invalid(ren_to)
	]
	if invalid_renames:
		wrong_rename_strings = [
			" {} (from {})".format(repr(ren_to), repr(ren_from))
			for ren_from, ren_to in invalid_renames
		]
		msg = "Invalid output sub-path{s}:\n{_list}".format(
			s="" if len(invalid_renames) < 2 else "s",
			_list="\n".join(wrong_rename_strings)
		)
		raise hou.NodeError(msg)
		return

	out_geo.setGlobalAttribValue(fbx_dir_attr_nm, base_dir_no_slash)
	out_geo.setGlobalAttribValue(renames_dict_attr_nm, renames)


def verify_relative_fbx_paths(asset_node: hou.SopNode, in_geo: hou.Geometry):
	"""Check if fbx paths are ready to be used by the actual asset's network."""
	fbx_paths = _get_fbx_path_strings(asset_node, in_geo)
	invalid_paths = [x for x in fbx_paths if _is_fbx_sub_path_invalid(x)]
	if not invalid_paths:
		return

	msg = "Invalid output sub-path{s}:\n{_list}".format(
		s="" if len(invalid_paths) < 2 else "s",
		_list="\n".join(" {}".format(repr(x)) for x in invalid_paths)
	)
	raise hou.NodeError(msg)
	return
