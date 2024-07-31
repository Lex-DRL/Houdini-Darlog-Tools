# encoding: utf-8
"""
Various utility functions to facilitate work with geometry attributes.
v2
"""

__author__ = 'Lex Darlog (DRL)'

import typing as _t

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
			return ['{}-vector{}'.format(_data_types, _sizes), ]

		# In one way or another, not a vector
		specifiers: _t.List[str] = list()
		if data_type:
			specifiers.append(_data_types)
		if size:
			specifiers.append('(size-{})'.format(_sizes) if not specifiers else '- {}'.format(_sizes))
		return specifiers


class AttributeNotFoundError(ValueError):
	"""An attribute of a given class/type/size isn't found in specific SOP node."""
	def __init__(
		self,
		msg: str = None, node: hou.Node = None,
		attr_name: str = None,
		attr_specifier: AttributeTypeSpecifier = None,
		msg_details: str = None
	):
		msg = self.__format_message(msg, node, attr_name, attr_specifier, msg_details)
		super(AttributeNotFoundError, self).__init__(msg)
		self.attr_name = attr_name
		self.attr_specifier = attr_specifier
		self.node = node

	@staticmethod
	def __format_message(
		msg: str = None, node: hou.Node = None,
		attr_name: str = None,
		attr_specifier: AttributeTypeSpecifier = None,
		msg_details: str = None
	) -> _t.Optional[str]:
		if msg is not None:
			return msg if not msg_details else '{}\n{}'.format(msg, msg_details)
		assert msg is None

		if attr_specifier is None:
			attr_specifier = AttributeTypeSpecifier()
		has_msg_specs = any(x is not None for x in chain(attr_specifier.as_tuple(), [attr_name, node]))
		if not has_msg_specs:
			return msg_details if msg_details else None
		assert has_msg_specs

		return '{what}{attr} not found{on_node}{clarif}'.format(
			what=attr_specifier.formatted(),
			attr='' if not attr_name else ' "{}"'.format(attr_name),
			on_node='' if not node else ' on node: {}'.format(repr(node)),
			clarif='' if not msg_details else '\n{}'.format(msg_details)
		)


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
