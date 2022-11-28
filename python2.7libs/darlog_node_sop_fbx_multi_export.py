# encoding: utf-8
"""
Python code for `fbxMultiExport` sop node.
"""

__author__ = 'Lex Darlog (DRL)'

import hou

from itertools import chain as _chain

from darlog_hou.attributes import NodeGeoProcessorBase, CommonAttribsValidator
from darlog_hou.errors import any_exception, assert_str, update_error_message
from darlog_hou.py23 import str_format as _format

try:
	import typing as _t

	# noinspection PyTypeHints,PyShadowingBuiltins
	_T = _t.TypeVar('T')
except ImportError:
	pass


_win_slash = 'z\\z'[1]

fbx_path_attr = 'fbx_path'
fbx_name_attr = 'fbx_name'

required_prim_str_attribs = (fbx_path_attr, fbx_name_attr)

# noinspection PyUnresolvedReferences
hou_expand_string = hou.expandString  # type: _t.Callable[[_t.AnyStr], _t.AnyStr]


def actual_dir_path_with_trailing_slash(path_with_hou_variables, dir_name='Export dir'):  # type: (str, str) -> str
	try:
		assert_str(path_with_hou_variables)
	except any_exception as e:
		raise update_error_message(
			e, _format("{} is not a string: {}", dir_name, repr(path_with_hou_variables))
		)

	path = hou_expand_string(path_with_hou_variables).replace(_win_slash, '/')
	if not path:
		raise hou.NodeError(_format("{} is empty", dir_name))

	path = path.rstrip('/')
	if not path:
		return '/'

	# Remove any repeating slashes in the middle of path:
	dir_segs_iter = iter(path.split('/'))
	first_dir_seg = next(dir_segs_iter)
	path = '/'.join(_chain(
		[first_dir_seg],
		(x for x in dir_segs_iter if x)
	))
	# Finally, append a trailing slash:
	return _format('{}/', path)


def _enforce_lowercase_fbx_extension(path):  # type: (str) -> str
	split_by_dot = path.split('.')
	if len(split_by_dot) < 2:
		split_by_dot.append('fbx')
	else:
		split_by_dot[-1] = 'fbx'
	return '.'.join(split_by_dot)


def actual_fbx_path(path_with_hou_variables, attr_name='fbx_path'):  # type: (str, str) -> str
	"""
	Turns a string which might contain houdini variables and turns it to an actual fbx file path.

	It's enforced to use unix-style slashes and to always have the lowercase 'fbx' extension.

	The provided string must represent a file path (not a dir path).
	"""
	try:
		assert_str(path_with_hou_variables)
	except any_exception as e:
		raise update_error_message(
			e, _format("{} value is not a string: {}", attr_name, repr(path_with_hou_variables))
		)

	path = hou_expand_string(path_with_hou_variables)
	path = path.replace(_win_slash, '/').rstrip('/')

	path_segs = path.split('/')
	if not path_segs:
		raise hou.NodeError(_format("{attr} attribute is empty", attr=repr(attr_name)))

	file_name = path_segs.pop()
	maybe_dir_with_slash = '' if not path_segs else actual_dir_path_with_trailing_slash(
		'/'.join(path_segs), dir_name=_format("{} attribute parent dir", repr(attr_name))
	)
	return _format('{}{}', maybe_dir_with_slash, _enforce_lowercase_fbx_extension(file_name))


class InputValidator(CommonAttribsValidator):

	def main(self, out_fbx_dir):  # type: (str) -> ...
		actual_dir_path_with_trailing_slash(out_fbx_dir)
		self.test_string(required_prim_str_attribs)


class PerFbxAttribsValidator(NodeGeoProcessorBase):

	def _read_expanded_fbx_path_attr(self, attr_name):  # type: (str) -> str
		val = self.geo.stringAttribValue(attr_name)  # type: str
		return actual_fbx_path(val, attr_name)

	def main(self, out_fbx_dir, error_if_export_to_same_path):  # type: (str, bool) -> ...
		geo = self.geo

		orig_path = actual_fbx_path(geo.stringAttribValue(fbx_path_attr))
		fbx_name = actual_fbx_path(geo.stringAttribValue(fbx_name_attr))

		new_path = _format('{}{}', actual_dir_path_with_trailing_slash(out_fbx_dir), fbx_name)

		if error_if_export_to_same_path and orig_path.lower() == new_path.lower():
			msg = _format("Can't export fbx over the same file that Houdini took geo from:\n{}", new_path)
			print(_format('\n{}', msg))
			raise hou.NodeError(msg)

		geo.setGlobalAttribValue(fbx_path_attr, new_path)
