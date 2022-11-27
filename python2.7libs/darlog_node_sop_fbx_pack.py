# encoding: utf-8
"""
Python code for `fbxPack` sop node.
"""

__author__ = 'Lex Darlog (DRL)'

import hou

from collections import OrderedDict
from itertools import chain as _chain
from json import dumps, loads

from darlog_hou.attributes import (
	NodeGeoProcessorBase,
	AttribFuncsPerGeo,
	test_name_no_reserved,
	test_name_factory
)
from darlog_hou.errors import assert_str, catch_error_message

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


class InputProcessorParm(NodeGeoProcessorBase):
	def __init__(
		self,
		node,  # type: hou.SopNode
		pos_vectors_pattern,  # type: str
		dir_vectors_pattern,  # type: str
		nrm_vectors_pattern,  # type: str
	):
		super(InputProcessorParm, self).__init__(node)
		self.vector_patterns = (pos_vectors_pattern, dir_vectors_pattern, nrm_vectors_pattern)

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
			(assert_str(x) for x in self.vector_patterns)
		):
			out_dict.update(
				('{}_{}'.format(attr_tp, vector_tp), attrs)
				for attr_tp, attrs in zip(_attr_types, self._matching_vector_attribs(attr_pattern))
			)

	def json_str(self):
		out_dict = _data_dict_init()
		caught_error, msg = catch_error_message(
			lambda: self._data_dict_populate(out_dict),
			''
		)
		if caught_error is not None:
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
			json_dict.get("{at}_{vt}".format(at=attr_type, vt=vector_tp), [])
		) for vector_tp, pattern, in zip(
			_vector_types,
			(vex_format_pos, vex_format_dir, vex_format_nrm)
		)
	]  # type: _t.List[str]
	attr_set_lines = _vex_section_separator.join(filter(None, lines_by_vector_type))
	if not attr_set_lines:
		return ''
	return _vex_section_separator.join([vex_common, attr_set_lines])


_required_fbx_pt_attribs = (
	"P",
	"fbx_translation",
	"fbx_rotation",
	"fbx_scale",
)
_test_obj_name = test_name_factory(*_required_fbx_pt_attribs)


class InputProcessorPythonNode(NodeGeoProcessorBase):
	def __init__(
		self,
		node,  # type: hou.SopNode
		name_attr,  # type: str
		json_str,  # type: str
	):
		super(InputProcessorPythonNode, self).__init__(node)
		self.name_attr = name_attr
		self.json_str = json_str

	def main(self):
		json_dict = loads(assert_str(self.json_str))  # type: dict
		if json_dict.get('is_error', False):
			raise hou.NodeError(json_dict.get('error', ''))

		geo = self.geo
		pt_attr_checker = AttribFuncsPerGeo(geo, hou.attribType.Point)
		for required_pt_attr in _required_fbx_pt_attribs:
			pt_attr_checker.attr_test(required_pt_attr, hou.attribData.Float, 3, test_name_f=test_name_no_reserved)

		AttribFuncsPerGeo(geo, hou.attribType.Prim).attr_test(
			self.name_attr, hou.attribData.String, 1,
			error_attr_nice_nm='FBX-object-name', test_name_f=_test_obj_name
		)
