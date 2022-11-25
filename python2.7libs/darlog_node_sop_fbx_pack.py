# encoding: utf-8
"""
Python code for `fbxPack` sop node.
"""

__author__ = 'Lex Darlog (DRL)'

import hou

from collections import OrderedDict
from itertools import chain as _chain
from json import dumps, loads

try:
	import typing as _t

	# noinspection PyTypeHints
	_T = _t.TypeVar('T')
except ImportError:
	pass

# noinspection PyBroadException
try:
	_unicode = unicode
	_str_types = (str, unicode)
except Exception:
	_unicode = str
	_str_types = (str, )


_attr_types = tuple('pt prim vtx'.split())
_vector_types = tuple('pos dir nrm'.split())

_data_dict_template = OrderedDict(_chain(
	[
		('{}_{}'.format(at, vt), list())
		for at in _attr_types for vt in _vector_types
	],
	[
		('is_error', False),
		('error', '')
	]
))


def _data_dict_init():
	return OrderedDict(_data_dict_template)


def _error(out_dict, message):  # type: (dict, str) -> ...
	out_dict['is_error'] = True
	out_dict['error'] = message


def _is_attr_matching_vector(attr_pattern_str, attr):  # type: (str, hou.Attrib) -> bool
	return bool(
		attr
		and hou.patternMatch(attr_pattern_str, attr.name())
		and not attr.isArrayType()
		and attr.dataType() == hou.attribData.Float
		and attr.size() == 3
	)


def _assert_arg_type(val, _class):  # type: (_t.Any, _t.Type[_T]) -> _T
	if not isinstance(val, _class):
		raise TypeError("Not a {{{}}}: {}".format(_class.__name__, repr(val)))
	return val


def _assert_str(val):  # type: (...) -> str
	if not isinstance(val, _str_types):
		raise TypeError("Not a string: {}".format(repr(val)))
	return val


class InputProcessorParm:
	def __init__(
		self,
		node,  # type: hou.SopNode
		pos_vectors_pattern,  # type: str
		dir_vectors_pattern,  # type: str
		nrm_vectors_pattern,  # type: str
	):
		self.__node = node
		self.__geo = None
		self.vector_patterns = (pos_vectors_pattern, dir_vectors_pattern, nrm_vectors_pattern)

	@property
	def node(self):
		return _assert_arg_type(self.__node, hou.SopNode)  # type: hou.SopNode

	@property
	def geo(self):
		geo = self.__geo
		if geo is None:
			self.__geo = geo = _assert_arg_type(self.node.geometry(), hou.Geometry)  # type: hou.Geometry
		return geo

	def _matching_vector_attribs(self, attr_pattern_str):
		def filter_attrs(attrs):  # type: (_t.Iterable[hou.Attrib]) -> _t.List[str]
			return [
				a.name() for a in attrs
				if _is_attr_matching_vector(attr_pattern_str, a)
			]

		geo = self.geo
		point, prim, vertex = (
			filter_attrs(aaa) for aaa in (
				geo.pointAttribs(),
				geo.primAttribs(),
				geo.vertexAttribs(),
				# self.geo.globalAttribs(),
			)
		)  # type: _t.List[str]
		return point, prim, vertex  # , detail

	def _data_dict_populate(self, out_dict):  # type: (dict) -> ...
		for vector_tp, attr_pattern in zip(
			_vector_types,
			(_assert_str(x) for x in self.vector_patterns)
		):
			out_dict.update(
				('{}_{}'.format(attr_tp, vector_tp), attrs)
				for attr_tp, attrs in zip(_attr_types, self._matching_vector_attribs(attr_pattern))
			)

	def json_str(self):
		out_dict = _data_dict_init()
		try:
			self._data_dict_populate(out_dict)
		except Exception as e:
			# noinspection PyBroadException
			try:
				msg = e.message
			except Exception:
				msg = e.args[0]
			_error(out_dict, msg)
		return dumps(out_dict, indent=1)


_vex_line_separator = '\n'


def vector_class_lines(pattern, attribs):  # type: (str, _t.List[str]) -> str
	return _vex_line_separator.join(
		pattern.format(vec=a) for a in attribs
	)


_vex_section_separator = '\n\n'


def vex_xform_for_attr_type(
	attr_type,  # type: str
	json_str,  # type: str
	vex_common,  # type: str
	vex_format_pos,  # type: str
	vex_format_dir,  # type: str
	vex_format_nrm,  # type: str
):
	json_dict = loads(json_str)  # type: dict

	lines_by_vector_type = [
		vector_class_lines(
			pattern,
			json_dict["{at}_{vt}".format(at=attr_type, vt=vector_tp)]
		) for vector_tp, pattern, in zip(
			_vector_types,
			(vex_format_pos, vex_format_dir, vex_format_nrm)
		)
	]  # type: _t.List[str]
	attr_set_lines = _vex_section_separator.join(filter(None, lines_by_vector_type))
	if not attr_set_lines:
		return ''
	return _vex_section_separator.join([vex_common, attr_set_lines])
