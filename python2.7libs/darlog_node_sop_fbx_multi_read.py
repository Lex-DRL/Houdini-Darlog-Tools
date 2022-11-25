# encoding: utf-8
"""
Python code for `fbxMultiRead` sop node.
"""

__author__ = 'Lex Darlog (DRL)'

import hou

from os.path import isfile
from glob import glob

try:
	import typing as _t

	# noinspection PyTypeHints
	_T = _t.TypeVar('T')
except ImportError:
	pass

win_slash = 'z\\z'[1]  # mindfuck to workaround Houdini bug when it sometimes can't just create a single backslash char
hip_pattern = '{}{}'.format('$', 'HIP')  # Houdini expands it to the actual path, so - this workaround

fbx_path_attr_nm = 'fbx_path'
fbx_dir_attr_nm = 'fbx_dir'
fbx_name_attr_nm = 'fbx_name'

error_bool_attr = 'is_error'


def _assert_arg_type(val, _class):  # type: (_t.Any, _t.Type[_T]) -> _T
	assert isinstance(val, _class), "Not a {{{}}}: {}".format(_class.__name__, repr(val))
	return val


def _hip_path_with_only_one_trailing_slash(path):  # type: (str) -> str
	if not path:
		raise hou.NodeError("HIP path can't be empty")
	path_no_slash = path.rstrip('/')
	return '/' if not path_no_slash else '{}/'.format(path_no_slash)


def path_to_dir_and_name( path):  # type: (str) -> _t.Tuple[str, str]
	split = path.split('/')
	name = split.pop()
	return '/'.join(split), name


class InputProcessor:
	def __init__(
		self,
		pwd_python_node,  # type: hou.SopNode
		path_pattern,  # type: str
		hip_path,  # type: str
	):
		node = _assert_arg_type(pwd_python_node, hou.SopNode)  # type: hou.SopNode
		self.geo = _assert_arg_type(node.geometry(), hou.Geometry)  # type: hou.Geometry

		self.path_pattern = path_pattern

		hip_path_with_slash = _hip_path_with_only_one_trailing_slash(hip_path.replace(win_slash, '/'))
		self.hip_path_with_slash = hip_path_with_slash
		self.hip_path_with_slash_n = len(hip_path_with_slash)
		self._hip_paths = {x for x in (hip_path_with_slash, hip_path_with_slash[:-1]) if x}

	def _replace_hip_path_to_pattern(self, path):  # type: (str) -> str
		if path in self._hip_paths:
			return hip_pattern
		if path.startswith(self.hip_path_with_slash):
			path = "{}/{}".format(hip_pattern, path[self.hip_path_with_slash_n:])
			return path
		return path

	def _main(self):
		geo = self.geo
		for attr_nm in (fbx_path_attr_nm, fbx_dir_attr_nm, fbx_name_attr_nm):
			attr = geo.findPointAttrib(attr_nm)  # type: hou.Attrib
			if attr is None or not attr:
				raise hou.NodeError(
					"Internal point attribute not found: {}".format(repr(attr_nm))
				)

		path_pattern = self.path_pattern

		if not path_pattern or path_pattern == '*':
			raise hou.NodeError("Path not specified")

		file_paths = glob(path_pattern)

		file_paths = filter(isfile, file_paths)
		file_paths = [x.replace(win_slash, '/').rstrip('/') for x in file_paths]
		file_paths = [self._replace_hip_path_to_pattern(x) for x in file_paths]
		file_paths = [x for x in file_paths if x.strip() and x.lower().endswith('.fbx')]

		if not file_paths:
			raise hou.NodeError("Files not found: {}".format(path_pattern))

		geo.createPoints([
			(x, 0, 0) for x in range(len(file_paths))
		])
		geo.setPointStringAttribValues(fbx_path_attr_nm, file_paths)
		fbx_dirs, fbx_names = zip(*(path_to_dir_and_name(p) for p in file_paths))
		geo.setPointStringAttribValues(fbx_dir_attr_nm, fbx_dirs)
		geo.setPointStringAttribValues(fbx_name_attr_nm, fbx_names)

		self.geo.setGlobalAttribValue(error_bool_attr, 0)

	def main(self):
		try:
			return self._main()
		except Exception as e:
			try:
				self.geo.setGlobalAttribValue(error_bool_attr, 1)
			except Exception:
				pass
			raise e
