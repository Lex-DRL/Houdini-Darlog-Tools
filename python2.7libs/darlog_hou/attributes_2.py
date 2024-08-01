# encoding: utf-8
"""
Various utility functions to facilitate work with geometry attributes.
v2
"""

__author__ = 'Lex Darlog (DRL)'

import typing as _t

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, fields
from itertools import chain
from re import compile as _re_compile

import hou

_T = _t.TypeVar('T')
_t_dt = _t.Union[hou.attribData, type(hou.attribData.Float)]
_t_cls = _t.Union[hou.attribType, type(hou.attribType.Point)]

ALL_ATTR_CLASSES: _t.Tuple[_t_cls, ...] = (
	hou.attribType.Point,
	hou.attribType.Prim,
	hou.attribType.Vertex,
	hou.attribType.Global,
)
ALL_ATTR_CLASSES_SET: _t.FrozenSet[_t_cls] = frozenset(ALL_ATTR_CLASSES)

ATTR_CLASS_TO_ID: _t.Dict[_t_cls, int] = {
	c: i for i, c in enumerate(ALL_ATTR_CLASSES)
}

ALL_ATTR_DATA_TYPES: _t.Tuple[_t_dt, ...] = (
	hou.attribData.Int,
	hou.attribData.Float,
	hou.attribData.String,
	hou.attribData.Dict,
)
ALL_ATTR_DATA_TYPES_SET: _t.FrozenSet[_t_dt] = frozenset(ALL_ATTR_DATA_TYPES)

ATTR_DATA_TYPE_TO_ID: _t.Dict[_t_dt, int] = {
	dt: i for i, dt in enumerate(ALL_ATTR_DATA_TYPES)
}

VECTOR_DATA_TYPES_SET = frozenset([hou.attribData.Int, hou.attribData.Float])


@dataclass
class AttributeTypeSpecifier:
	"""
	A dataclass defining a detailed attribute class/type/size specifier.
	Each field is either a `None` or a tuple of valid options.
	Main purpose is nice (human-readable) formatting of such specifier.
	"""
	attr_class: _t.Optional[_t.Tuple[_t_cls, ...]] = None
	data_type: _t.Optional[_t.Tuple[_t_dt, ...]] = None
	size: _t.Optional[_t.Tuple[int, ...]] = None
	is_array: _t.Optional[bool] = None

	@classmethod
	def from_unsafe_args(
		cls,
		attr_class: _t.Union[_t_cls, _t.Iterable[_t_cls]] = None,
		data_type: _t.Union[_t_dt, _t.Iterable[_t_dt]] = None,
		size: _t.Union[int, _t.Iterable[int]] = None,
		is_array: bool = None,
	) -> 'AttributeTypeSpecifier':
		"""A factory method, dealing with less restrictive input arguments"""
		return cls(
			attr_class=cls.__arg_options_tuple(attr_class),
			data_type=cls.__arg_options_tuple(data_type),
			size=cls.__arg_options_tuple(size),
			is_array=is_array if is_array is None else bool(is_array)
		)

	@staticmethod
	def __arg_options_tuple(value: _t.Union[_T, _t.Iterable[_T], None]) -> _t.Optional[_t.Tuple[_T, ...]]:
		if value is None:
			return None
		try:
			return tuple(value)
		except TypeError:
			return (value, )

	def as_tuple(self):
		return tuple(getattr(self, field.name) for field in fields(self))

	def formatted(self, uppercase_first_char=True) -> str:
		if all(x is None for x in self.as_tuple()):
			return 'Attribute' if uppercase_first_char else 'attribute'

		specifiers: _t.List[str] = list()
		if self.is_array is not None:
			specifiers.append('[ARRAY]' if self.is_array else '[NON-array]')
		if self.attr_class is not None:
			specifiers.append(
				'/'.join(x.name() for x in self.attr_class)
			)
		specifiers.extend(self.__data_type_specifier())
		specifiers.append('attribute')

		res = ' '.join(specifiers)
		if not uppercase_first_char:
			return res
		return '{}{}'.format(res[:1].upper(), res[1:])

	def __data_type_specifier(self) -> _t.List[str]:
		data_type = self.data_type
		size = self.size

		_data_types = '/'.join(x.name().lower() for x in data_type)
		_sizes = '/'.join(str(x) for x in size)

		if (
			data_type and all(x in VECTOR_DATA_TYPES_SET for x in data_type) and
			size and any(x > 1 for x in size) and all(x > 0 for x in size) and
			not self.is_array
		):
			# The attribute is a vector
			if len(data_type) > 1:
				_data_types = '[{}]'.format(_data_types)
			return ['{}-vector-{}'.format(_data_types, _sizes), ]

		# In one way or another, not a vector
		specifiers: _t.List[str] = list()
		if data_type:
			specifiers.append(_data_types if not size else '{}({})'.format(_data_types, _sizes))
		elif size:
			specifiers.append('(size-{})'.format(_sizes))
		return specifiers


class AttributeErrorABC(ValueError, metaclass=ABCMeta):
	"""Abstract base for various errors related to attribute-check (by Darlog's custom asset-nodes)."""
	def __init__(
		self,
		name: str = None,
		specifier: AttributeTypeSpecifier = None,
		node: hou.Node = None,
		msg: str = None,
		msg_details: str = None
	):
		msg = self._format_message(name, specifier, node, msg, msg_details, self._formatter_cls_extra())
		super(AttributeErrorABC, self).__init__(msg)
		self.name = name
		self.specifier = specifier
		self.node = node

	@classmethod
	def _format_message(
		cls,
		name: str = None,
		specifier: AttributeTypeSpecifier = None,
		node: hou.Node = None,
		msg: str = None,
		msg_details: str = None,
		cls_extra: str = '',
	) -> _t.Optional[str]:
		if msg is not None:
			return msg if not msg_details else '{}\n{}'.format(msg, msg_details)
		assert msg is None

		if specifier is None:
			specifier = AttributeTypeSpecifier()
		has_msg_specs = any(x is not None for x in chain(specifier.as_tuple(), [name, node]))
		if not has_msg_specs:
			return msg_details if msg_details else None
		assert has_msg_specs

		res = cls._formatter().format(
			attr=specifier.formatted(uppercase_first_char=False),
			nm='' if not name else ' {}'.format(repr(name)),
			whats_wrong=cls._formatter_whats_wrong_with_attr(),
			on_node='' if not node else ' on node: {}'.format(repr(node)),
			details='' if not msg_details else '\n{}'.format(msg_details),
			cls_extra=cls_extra
		)
		return '{}{}'.format(res[:1].upper(), res[1:])

	@classmethod
	def _formatter(cls) -> str:
		"""Main formatting pattern for the exception message"""
		return '{attr}{nm}{whats_wrong}{on_node}{details}{cls_extra}'

	@classmethod
	def _formatter_cls_extra(cls) -> str:
		"""If a child class needs to add something to the error message, this is the method to do so with."""
		return ''

	@classmethod
	@abstractmethod
	def _formatter_whats_wrong_with_attr(cls) -> str:
		"""This class method defines the main part of error message: what's wrong with an attribute."""
		...


class AttributeNotFoundError(AttributeErrorABC):
	"""An attribute of a given class/type/size isn't found in specific SOP node."""

	@classmethod
	def _formatter_whats_wrong_with_attr(cls) -> str:
		return ' not found'


class _MultiAttributeErrorABC(AttributeErrorABC, metaclass=ABCMeta):
	"""Intermediate base exception class also containing a field with multiple attributes and adding it to output."""

	def __init__(
		self,
		*attributes: hou.Attrib,
		name: str = None,
		specifier: AttributeTypeSpecifier = None,
		node: hou.Node = None,
		msg: str = None,
		msg_details: str = None,
	):
		self.attributes = attributes  # needs to be done BEFORE calling superclass-init
		super(_MultiAttributeErrorABC, self).__init__(name, specifier, node, msg, msg_details)
		self.attributes = attributes  # just to make sure

	def _formatter_cls_extra(self) -> str:
		attributes = self.attributes
		if not attributes:
			return ''
		lines: _t.List[str] = [repr(x).strip() for x in attributes]
		if len(lines) == 1:
			return ' {}'.format(lines[0])
		lines_bullet_points = ('- {}'.format(x) for x in lines)
		lines_bullet_points = chain([''], lines_bullet_points)  # to start on a new line
		return '\n'.join(lines_bullet_points)


class AttributeDataMismatchError(_MultiAttributeErrorABC):
	"""Geometry does have attribute(s) with the given name, but the attr has a wrong data type/size."""
	
	@classmethod
	def _formatter_whats_wrong_with_attr(cls) -> str:
		return " doesn't match specifier"

	@classmethod
	def _formatter(cls) -> str:
		"""Main formatting pattern for the exception message"""
		return 'Attribute{nm} is found, but it{whats_wrong}{on_node}\nExpected: {attr}{details}\nGot:{cls_extra}'


class AttributeClassMismatchError(_MultiAttributeErrorABC):
	"""Geometry does have attribute(s) with the given name, but it has a wrong class (point/prim/vertex/detail)."""

	@classmethod
	def _formatter_whats_wrong_with_attr(cls) -> str:
		return " has a wrong class"

	@classmethod
	def _formatter(cls) -> str:
		"""Main formatting pattern for the exception message"""
		return 'Attribute{nm} is found, but it{whats_wrong}{on_node}\nExpected: {attr}{details}\nGot:{cls_extra}'


class MultipleMatchingAttributesError(_MultiAttributeErrorABC):
	"""Found multiple attributes of a given class/type/size."""

	@classmethod
	def _formatter_whats_wrong_with_attr(cls) -> str:
		return 'found multiple'

	@classmethod
	def _formatter(cls) -> str:
		return '{whats_wrong}{nm} {attr}s{on_node}{details}{cls_extra}'


def find_verify(
	name: str,
	specifier: AttributeTypeSpecifier = None,
	include_private=False,
	node: hou.SopNode = None,
	geo: hou.Geometry = None,
	geo_from_input: int = None,
	error_multi: bool = True,
) -> hou.Attrib:
	if geo is None:
		assert isinstance(node, hou.SopNode), "Not a SOP node: {}".format(repr(node))
		geo = node.geometry() if geo_from_input is None else node.inputGeometry(geo_from_input)
	assert isinstance(geo, hou.Geometry), "Not a geometry: {}".format(repr(geo))
	if node is None:
		node = geo.sopNode()
	valid_specifier = AttributeTypeSpecifier() if specifier is None else specifier
	assert isinstance(valid_specifier, AttributeTypeSpecifier), "Not an attribute specifier: {}".format(repr(valid_specifier))
	assert isinstance(name, str), "Attribute name isn't a string: {}".format(repr(name))
	clean_name = clean_attr_name(name)
	if not clean_name:
		raise ValueError("Not a valid attribute name: {}".format(repr(name)))

	attr_classes = valid_specifier.attr_class
	if not attr_classes:
		attr_classes = ALL_ATTR_CLASSES

	potential_matches: _t.List[hou.Attrib] = list()
	all_attr_getters: _t.Dict[_t_cls, _t.Callable] = {
		hou.attribType.Vertex: geo.vertexAttribs,
		hou.attribType.Prim: geo.primAttribs,
		hou.attribType.Point: geo.pointAttribs,
		hou.attribType.Global: geo.globalAttribs,
	}
	for attr_cls in attr_classes:
		getter = all_attr_getters.get(attr_cls)
		if not callable(getter):
			continue
		potential_matches.extend(getter(include_private=include_private))
	# All the attribs matching by class are listed. Now, filter them by other specifiers

	filtered: _t.List[hou.Attrib] = [a for a in potential_matches if a.name() == clean_name]

	data_types = valid_specifier.data_type
	if data_types:
		_set = set(data_types)
		filtered = [a for a in filtered if a.dataType() in _set]

	sizes = valid_specifier.size
	if sizes:
		_set = set(sizes)
		filtered = [a for a in filtered if a.size() in _set]

	is_array = valid_specifier.is_array
	if is_array is not None:
		is_array = bool(is_array)
		filtered = [a for a in filtered if bool(a.isArrayType()) == is_array]

	matches = list(filtered)
	if not matches:
		raise AttributeNotFoundError(name=name, specifier=specifier, node=node)
	if error_multi and len(matches) > 1:
		raise MultipleMatchingAttributesError(*matches, name=name, specifier=specifier, node=node)
	return matches[0]


_re_valid_attr_name = _re_compile('[a-zA-Z_]+[a-zA-Z_0-9]*')


def clean_attr_name(name: str) -> str:
	"""
	Valid attribute name extracted from an arbitrary string.
	The first satisfying character substring is returned,
	any non-valid characters before/after it are simply stripped.

	Might return an empty string, but always a string anyway.
	"""
	match = _re_valid_attr_name.search(name)
	return '' if not match else match.group(0)
