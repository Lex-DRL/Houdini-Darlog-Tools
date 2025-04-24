# encoding: utf-8
"""
Code, specific for exporting multi-KineFX.
"""

__author__ = 'Lex Darlog (DRL)'

import typing as _t

from os.path import commonpath, abspath
from sys import platform

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
meta_do_attr_nm = "_do"
meta_old_dir_attr_nm = "old_dir"
meta_new_dir_attr_nm = "new_dir"


hou_expand_string = hou.text.expandString  # type: _t.Callable[[_t.AnyStr], _t.AnyStr]


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
	assert isinstance(fbx_path, str), "Internal error: fbx-path isn't a string: {}".format(repr(fbx_path))
	return (
		(not fbx_path) or fbx_path.lower() == '.fbx'
		or fbx_path.startswith(hip_pattern_slash) or fbx_path.startswith(hip_pattern_braces)
	)


def _clean_fbx_path(fbx_path: str) -> str:
	assert isinstance(fbx_path, str), "Internal error: fbx-path isn't a string: {}".format(repr(fbx_path))
	clean = fbx_path.replace(win_slash, '/').lstrip('/')
	return clean if clean.lower().endswith('.fbx') else '{}.fbx'.format(clean)


class CleanPathDetectorAwareOfWindows:
	"""
	Callable (function-like) class, which does the same as ``_clean_fbx_path()``,
	but also caches previous clean paths, and for subsequent calls with the same paths with different case,
	returns the same case as before.

	Thus, on Windows filesystems, the same ACTUAL file paths would be turned into the same STRINGS, too.
	"""

	def __init__(self):
		self.lowercase_to_cached_case: _t.Dict[str, str] = dict()

	def __call__(self, fbx_path: str) -> str:
		clean = _clean_fbx_path(fbx_path)
		clean_lowercase = clean.lower()
		_cached = self.lowercase_to_cached_case
		if clean_lowercase in _cached:
			return _cached[clean_lowercase]
		_cached[clean_lowercase] = clean
		return clean

	@classmethod
	def get_platform_specific_func(cls):
		"""Get either the class instance or ``_clean_fbx_path()`` function, depending on platform."""
		if platform.lower().startswith('win'):
			return cls()
		return _clean_fbx_path


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

	clean_path_func = CleanPathDetectorAwareOfWindows.get_platform_specific_func()
	renames: _t.Dict[str, str] = {
		pth: clean_path_func(pth[shared_prefix_n:])
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


def detect_fbx_path_cleanup_renames(asset_node: hou.SopNode, in_geo: hou.Geometry, out_geo: hou.Geometry):
	"""
	If we don't extract base-dir path, we still need to enforce:
	- fbx paths to have unix slashes
	- they don't have any leading slashes

	This function does that, by detecting and planning such renames.
	"""
	fbx_paths = _get_fbx_path_strings(asset_node, in_geo)

	clean_path_func = CleanPathDetectorAwareOfWindows.get_platform_specific_func()
	renames: _t.Dict[str, str] = dict()
	for fbx in fbx_paths:
		clean = clean_path_func(fbx)
		if fbx != clean:
			renames[fbx] = clean

	out_geo.setGlobalAttribValue(meta_do_attr_nm, 1 if renames else 0)
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


def _make_dir_with_trailing_slash(raw_path: str) -> str:
	"""Might return '' if raw path also was empty. Otherwise, any non-empty string ends with '/'."""
	raw_path = hou_expand_string(raw_path).replace(win_slash, '/')
	if not raw_path:
		return ""
	dir_no_slash = raw_path.rstrip('/')
	if not dir_no_slash:
		# The only way this could be is if raw path is made purely of '/' chars
		return '/'
	assert bool(dir_no_slash)

	dir_no_slash = abspath(dir_no_slash).replace(win_slash, '/').rstrip('/')
	if not dir_no_slash:
		# something REALLY weird happened: we got an empty string after generating an absolute path
		raise ValueError("Invalid path: {}".format(repr(raw_path)))
		return ""
	return "{}/".format(dir_no_slash)


def prepare_old_and_new_base_dir_attrs(in_geo: hou.Geometry, out_geo: hou.Geometry, new_dir: str):
	try:
		old_dir: str = in_geo.stringAttribValue(fbx_dir_attr_nm)
		old_dir = _make_dir_with_trailing_slash(old_dir)
		new_dir = _make_dir_with_trailing_slash(new_dir)
		out_geo.setGlobalAttribValue(meta_old_dir_attr_nm, old_dir)
		out_geo.setGlobalAttribValue(meta_new_dir_attr_nm, new_dir)
	except any_exception as e:
		msg = get_error_message(e, default=str(e))
		raise hou.NodeError(msg)
		return


def verify_out_dir_path(in_geo: hou.Geometry, error_if_same_out_dir):
	new_dir: str = in_geo.stringAttribValue(meta_new_dir_attr_nm)
	if not new_dir:
		raise hou.NodeError("Export directory must be specified")
		return
	if error_if_same_out_dir and in_geo.stringAttribValue(meta_old_dir_attr_nm) == new_dir:
		raise hou.NodeError("Trying to export into the same directory FBX files are loaded from:\n{}\n".format(new_dir))
