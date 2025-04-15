# encoding: utf-8
"""
Python code for `fbxMultiRead` sop node. Also used for KineFX version.
"""

__author__ = 'Lex Darlog (DRL)'

import hou

from glob import glob
from os.path import isfile
from sys import platform

from darlog_hou.errors import any_exception, catch_error_message
from darlog_hou.py23 import str_format as _format

try:
	import typing as _t

	# noinspection PyTypeHints
	_T = _t.TypeVar('T')
except ImportError:
	pass

win_slash = 'q\\q'[1]  # mindfuck to workaround Houdini bug when it sometimes can't just create a single backslash char
hip_pattern = _format('{}{}', '$', 'HIP')  # Houdini expands it to the actual path, so - this workaround

fbx_path_attr_nm = 'fbx_path'
fbx_dir_attr_nm = 'fbx_dir'
fbx_name_attr_nm = 'fbx_name'

fbx_base_path_attr_nm = 'fbx_base_path'

error_bool_attr = 'is_error'


def _assert_arg_type(val, _class):  # type: (_t.Any, _t.Type[_T]) -> _T
	assert isinstance(val, _class), _format("Not a {{{}}}: {}", _class.__name__, repr(val))
	return val


def _hip_path_with_only_one_trailing_slash(path):  # type: (str) -> str
	if not path:
		raise hou.NodeError("HIP path can't be empty")
	path_no_slash = path.rstrip('/')
	return '/' if not path_no_slash else _format('{}/', path_no_slash)


def path_to_dir_and_name( path):  # type: (str) -> _t.Tuple[str, str]
	split = path.split('/')
	name = split.pop()
	return '/'.join(split), name


class HipReplacer:
	"""
	Function-like class, which puts the actual "$HIP" at the beginning of path.

	Turned to a class only to cache values when processing multiple paths at once.
	"""
	def __init__(self, hip_path: str):
		hip_path_with_slash = _hip_path_with_only_one_trailing_slash(hip_path.replace(win_slash, '/'))
		self.hip_path_with_slash = hip_path_with_slash
		self.hip_path_with_slash_n = len(hip_path_with_slash)
		self._hip_paths = {x for x in (hip_path_with_slash, hip_path_with_slash[:-1]) if x}

	def replace_hip_path_to_pattern(self, path: str) -> str:
		if path in self._hip_paths:
			return hip_pattern
		if path.startswith(self.hip_path_with_slash):
			path = _format("{}/{}", hip_pattern, path[self.hip_path_with_slash_n:])
			return path
		return path


class InputProcessor:
	def __init__(
		self,
		pwd_python_node,  # type: hou.SopNode
		path_pattern,  # type: str
		hip_path,  # type: str
	):
		node = _assert_arg_type(pwd_python_node, hou.SopNode)  # type: hou.SopNode
		self.geo = _assert_arg_type(node.geometry(), hou.Geometry)  # type: hou.Geometry
		self.path_pattern = path_pattern.replace(win_slash, '/')
		self.hip_replacer = HipReplacer(hip_path)

	def _main(self):
		geo = self.geo
		for attr_nm in (fbx_path_attr_nm, fbx_dir_attr_nm, fbx_name_attr_nm):
			attr = geo.findPointAttrib(attr_nm)  # type: hou.Attrib
			if attr is None or not attr:
				raise hou.NodeError(
					_format("Internal point attribute not found: {}", repr(attr_nm))
				)

		path_pattern = self.path_pattern

		if not path_pattern or path_pattern == '*':
			raise hou.NodeError("Path not specified")

		file_paths = glob(path_pattern, recursive=('**/' in path_pattern))

		file_paths = filter(isfile, file_paths)
		file_paths = [x.replace(win_slash, '/').rstrip('/') for x in file_paths]
		file_paths = [self.hip_replacer.replace_hip_path_to_pattern(x) for x in file_paths]
		file_paths = [x for x in file_paths if x.strip() and x.lower().endswith('.fbx')]

		if not file_paths:
			raise hou.NodeError(_format("Files not found: {}", path_pattern))

		geo.createPoints([
			(x, 0, 0) for x in range(len(file_paths))
		])
		geo.setPointStringAttribValues(fbx_path_attr_nm, file_paths)
		fbx_dirs, fbx_names = zip(*(path_to_dir_and_name(p) for p in file_paths))
		geo.setPointStringAttribValues(fbx_dir_attr_nm, fbx_dirs)
		geo.setPointStringAttribValues(fbx_name_attr_nm, fbx_names)

		self.geo.setGlobalAttribValue(error_bool_attr, 0)

	def main(self):
		caught_error, msg = catch_error_message(self._main, '')
		if caught_error is None:
			return

		try:
			self.geo.setGlobalAttribValue(error_bool_attr, 1)
		except any_exception:
			pass
		raise caught_error


def turn_to_relative_paths(python_node: hou.SopNode, do_base_path, base_path: str, hip_path: str):
	if not(do_base_path and base_path):
		return

	raw_base_path = base_path
	base_path = base_path.replace(win_slash, '/').rstrip('/')
	base_path = HipReplacer(hip_path).replace_hip_path_to_pattern(base_path)
	if not base_path:
		raise hou.NodeError("Invalid base path: {}".format(repr(raw_base_path)))
		return
	base_path_with_slash = "{}/".format(base_path)
	base_path_with_slash_lower = base_path_with_slash.lower()
	base_path_with_slash_n = len(base_path_with_slash)

	def _starts_with_base_path(string: str):
		return string.startswith(base_path_with_slash)

	def _starts_with_base_path_ignore_case(string: str):
		return string.lower().startswith(base_path_with_slash_lower)

	starts_with_base_path = _starts_with_base_path_ignore_case if platform.lower().startswith('win') else _starts_with_base_path

	python_node = _assert_arg_type(python_node, hou.SopNode)
	geo: hou.Geometry = _assert_arg_type(python_node.geometry(), hou.Geometry)

	fbx_paths: _t.Tuple[str, ...] = tuple(
		x[base_path_with_slash_n:] if starts_with_base_path(base_path_with_slash) else x
		for x in geo.pointStringAttribValues(fbx_path_attr_nm)
	)
	geo.setPointStringAttribValues(fbx_path_attr_nm, fbx_paths)

	# Finally, set base path itself
	geo.addAttrib(hou.attribType.Global, fbx_base_path_attr_nm, "", False, False)
	geo.setGlobalAttribValue(fbx_base_path_attr_nm, base_path)
