# encoding: utf-8
"""
Various utility functions to facilitate work with geometry attributes.
"""

import hou

from itertools import chain as _chain
from string import ascii_letters, digits

try:
	import typing as _t
	_O = _t.Optional
	_U = _t.Union

	# noinspection PyTypeHints
	_T = _t.TypeVar('T')

	_t_attr_getter = _t.Callable[[str], hou.Attrib]
	_t_at_arg = _O[_U[_t.Sequence[hou.attribType], hou.attribType]]
	_t_dt_arg = _O[_U[_t.Iterable[hou.attribData], hou.attribData]]
	_t_sz_arg = _O[_U[_t.Iterable[int], int]]
except ImportError:
	pass

# noinspection PyBroadException
try:
	_unicode = unicode
	_str_types = (str, unicode)
except Exception:
	_unicode = str
	_str_types = (str, )


def _dummy(*args, **kwargs):
	return None


def format_prefix(string):  # type: (str) -> ...
	"""'XXX' -> 'XXX '"""
	return '' if not string else '{} '.format(string)


def format_postfix(string):  # type: (str) -> ...
	"""'XXX' -> ' (XXX)'"""
	return '' if not string else ' ({})'.format(string)


def format_comma_and(items, _or=False):  # type: (_t.Iterable, bool) -> str
	last = items[-1]
	comma_separated = items[:-1]
	if not comma_separated:
		return last
	return "{w_comma} {and_or} {last}".format(
		w_comma=', '.join(comma_separated), last=last,
		and_or='or' if _or else 'and'
	)


_attr_nm_valid_chars = set(ascii_letters + digits + '_')  # type: _t.Set[str]
_attr_nm_valid_first_chars = set(ascii_letters + '_')  # type: _t.Set[str]


def _test_name_fixed_reserved_set(
	reserved_names_set,  # type: _t.Set[str]
	name,  # type: str
	error_attr_nice_nm='',  # type: str
	entity_type='attribute',  # type: str
	default_name='',  # type: str
	default_name_always_ok=False  # type: bool
):  # type: (...) -> str
	"""Test name for an entity (attribute/parm)."""
	if not isinstance(name, _str_types):
		raise hou.NodeError("Name for {nice}{entity} must be a string".format(
			nice=format_prefix(error_attr_nice_nm), entity=entity_type
		))

	names = name.split()
	name = names[0] if names else default_name
	if default_name_always_ok and name == default_name:
		return default_name

	if not name:
		raise hou.NodeError("No name given for {nice}{entity}".format(
			nice=format_prefix(error_attr_nice_nm), entity=entity_type
		))

	if name[0] not in _attr_nm_valid_first_chars:
		raise hou.NodeError("{nice}{entity} name can't start with {{{x}}} character".format(
			x=name[0], nice=format_prefix(error_attr_nice_nm), entity=entity_type
		))

	for x in name:
		if x not in _attr_nm_valid_chars:
			raise hou.NodeError("Wrong {{{x}}} character in {nice}{entity} name: {nm}".format(
				x=x, nm=repr(name), nice=format_prefix(error_attr_nice_nm), entity=entity_type
			))

	if name in reserved_names_set:
		raise hou.NodeError("Can't use reserved {a_nm} as {nice}{entity}".format(
			a_nm=repr(name), nice=format_prefix(error_attr_nice_nm), entity=entity_type
		))

	return name


def _check_reserved_name(name):  # type: (str) -> str
	assert isinstance(name, _str_types), "Reserved name must be a string. Got: {}".format(repr(name))
	name = name.strip()
	if not(
		name
		and name[0] in _attr_nm_valid_first_chars
		and all(x in _attr_nm_valid_chars for x in name)
	):
		raise ValueError("Wrong reserved name: {}".format(repr(name)))
	return name


def _reserved_names_gen(val):  # type: (...) -> _t.Generator[str, ...]
	if not val:
		return
	if isinstance(val, str):
		for v in val.split():
			try:
				yield _check_reserved_name(v)
			except ValueError as e:
				if v == val:
					raise e
				msg = '{} in {}'.format(e.args[0], val)
				e.args = tuple(_chain([msg], e.args[1:]))

				# noinspection PyBroadException
				try:
					# For Py2:
					_ = e.message
					e.message = msg
				except Exception:
					pass
				raise e
		return

	try:
		seq = iter(val)
	except Exception:
		raise hou.NodeError("{{reserved_names}} must be a string or sequence of strings. Got: {}".format(repr(val)))

	for el in seq:
		try:
			for x in _reserved_names_gen(el):
				yield x
		except hou.NodeError as e:
			raise hou.NodeError('{} in {}'.format(e.instanceMessage(), repr(val)))


def test_name_factory(
	*reserved_names  # type: _U[_t.Iterable[str], str]
):
	"""
	This factory generates a function which checks if a given string is a valid attribute/parameter name.
	The generated function does so with respect to the reserved names given to the factory.

	The factory is necessary since internally the provided `reserved_names` argument is checked and converted to a set
	of strings. Doing it in for each function call would be quite expensive, so you should just call this factory,
	cache it's result as your own func and reuse it.
	"""
	reserved_set = set(_reserved_names_gen(reserved_names))

	def _test_name(
		name,  # type: str
		error_attr_nice_nm='',  # type: str
		entity_type='attribute',  # type: str
		default_name='',  # type: str
		default_name_always_ok=False  # type: bool
	):  # type: (...) -> str
		"""Check whether a given string is a valid name for an entity (attribute/parm). """
		return _test_name_fixed_reserved_set(
			reserved_set, name,
			error_attr_nice_nm=error_attr_nice_nm, entity_type=entity_type,
			default_name=default_name, default_name_always_ok=default_name_always_ok
		)

	return _test_name


test_name_no_reserved = test_name_factory()
test_name_no_reserved.__doc__ = "Check whether a given string is a valid name for an entity (attribute/parm).\nNo names are reserved."

test_name_p_reserved = test_name_factory('P')
test_name_p_reserved.__doc__ = "Check whether a given string is a valid name for an entity (attribute/parm).\n'P' is reserved."


_all_attr_datatypes = {
	hou.attribData.Int,
	hou.attribData.Float,
	hou.attribData.String
}  # type: _t.Set[hou.attribData]
_attr_datatypes_sort_map = {
	hou.attribData.Int: 0,
	hou.attribData.Float: 1,
	hou.attribData.String: 2,
}


def _test_attr_dt(attr, data_types, error_attr_nice_nm=''):  # type: (hou.Attrib, _t_dt_arg, str) -> ...
	if not data_types:
		# The check is explicitly disabled
		return

	def check_arg(val):  # type: (...) -> _t.Set[hou.attribData]
		if val in _all_attr_datatypes:
			return {val, }

		try:
			seq = iter(val)  # type: _t.Iterator[hou.attribData]
		except Exception:
			raise hou.NodeError(
				"{{data_types}} must be hou.attribData or a sequence of them (for {nice}attribute {a}). Got: {val}".format(
					a=repr(attr.name()), val=repr(val), nice=format_prefix(error_attr_nice_nm)
				)
			)

		checked_seq = list()  # type: _t.List[hou.attribData]
		for v in seq:
			if v not in _all_attr_datatypes:
				raise hou.NodeError("Unknown expected data type for {nice}attribute {a}: {v} in {val}".format(
					a=repr(attr.name()), v=repr(v), val=repr(val), nice=format_prefix(error_attr_nice_nm)
				))
			checked_seq.append(v)
		return set(checked_seq)

	data_types_set = check_arg(data_types)

	dt = attr.dataType()  # type: hou.attribData
	if dt not in data_types_set:
		raise hou.NodeError("{a} is {dt} attribute{a_brackets}. Expected: {exp}".format(
			a=repr(attr.name()), dt=dt.name(),
			exp=format_comma_and(
				[a_dt.name() for a_dt in sorted(data_types, key=lambda x: _attr_datatypes_sort_map.get(x))],
				_or=True
			),
			a_brackets=format_postfix(error_attr_nice_nm)
		))


def _test_attr_sz(attr, sizes, error_attr_nice_nm=''):  # type: (hou.Attrib, _t_sz_arg, str) -> ...
	if not sizes and sizes != 0:
		# The check is explicitly disabled
		return

	def check_arg(val):  # type: (...) -> _t.Set[int]
		if isinstance(val, (int, float)):
			return {int(val), }

		try:
			seq = iter(val)  # type: _t.Iterator[hou.attribData]
		except Exception:
			raise hou.NodeError(
				"Expected sizes for {nice}attribute {a} must be ints: {val}".format(
					a=repr(attr.name()), val=repr(val), nice=format_prefix(error_attr_nice_nm)
				)
			)

		checked_seq = list()  # type: _t.List[int]
		for v in seq:
			if not isinstance(v, (int, float)):
				raise hou.NodeError("Expected sizes for {nice}attribute {a} must be ints. Got: {v} in {val}".format(
					a=repr(attr.name()), v=repr(v), val=repr(val), nice=format_prefix(error_attr_nice_nm)
				))
			checked_seq.append(v)
		return set(checked_seq)

	sizes_set = check_arg(sizes)

	size = attr.size()
	if size not in sizes_set:
		raise hou.NodeError("{nice}attribute {a} has wrong size ({sz}). Expected: {exp}".format(
			a=repr(attr.name()), sz=size, exp=sizes, nice=format_prefix(error_attr_nice_nm)
		))


_attr_types_default_priority = (
	hou.attribType.Vertex, hou.attribType.Prim, hou.attribType.Point, hou.attribType.Global
)  # type: _t.Tuple[hou.attribType, ...]
_attr_types_default_sort_map = {
	x: i for i, x in enumerate(_attr_types_default_priority)
}  # type: _t.Dict[hou.attribType, int]


class AttribFuncsPerGeo:
	def __init__(self, geo, attr_types=None):  # type: (hou.Geometry, _t_at_arg) -> ...
		self.__geo = None  # type: hou.Geometry
		self.__attr_types_priority = _attr_types_default_priority  # type: _t.Tuple[hou.attribType, ...]
		self.__attr_data_types = None  # type: _t.Set[hou.attribData]

		self.__attr_getters = None  # type: _t.Dict[hou.attribType, _t_attr_getter]

		self.__set_geo(geo)
		self.__set_attr_types(attr_types)
		self.__rebuild_attr_getters()

	def __repr__(self):
		args = [repr(self.geo)]  # type: _t.List[str]
		args.extend(
			'{}={}'.format(arg_name, repr(value))
			for arg_name, value, default in [
				('attr_types', self.attr_types, _attr_types_default_priority),
				('data_types', self.data_types, _all_attr_datatypes),
			] if value != default
		)
		return '{}({})'.format(self.__class__.__name__, ', '.join(args))

	def __set_geo(self, value):
		if not isinstance(value, hou.Geometry):
			raise TypeError("Not a `hou.Geometry`: {}".format(repr(value)))
		self.__geo = value

	def __set_attr_types(self, attr_tps_priority):
		if not attr_tps_priority:
			self.__attr_types_priority = _attr_types_default_priority
			return
		if attr_tps_priority in _attr_types_default_sort_map:
			self.__attr_types_priority = (attr_tps_priority, )
			return

		try:
			seq = iter(attr_tps_priority)  # type: _t.Iterator[hou.attribType]
		except Exception:
			raise TypeError("{{attr_priority}} must be hou.attribType or a sequence of them. Got: {}".format(
				repr(attr_tps_priority)
			))

		checked_seq = list()  # type: _t.List[hou.attribType]
		for a_tp in seq:
			if a_tp not in _attr_types_default_sort_map:
				raise TypeError("Unknown expected attribute type: {}; Got attr_priority={}".format(
					repr(a_tp), repr(attr_tps_priority)
				))
			checked_seq.append(a_tp)

		self.__attr_types_priority = tuple(checked_seq)

	def __rebuild_attr_getters(self):
		geo = self.__geo
		# Houdini 18.5 with py3 (rather than 17.5/py2) crashes with `Segmentation fault` error
		# if we use hou.Geometry.* methods here (rather than geo.* methods).
		# So the dict can't be changed to a geometry-independent one, we NEED to use methods on the actual instance:
		all_getters = {
			hou.attribType.Vertex: geo.findVertexAttrib,
			hou.attribType.Prim: geo.findPrimAttrib,
			hou.attribType.Point: geo.findPointAttrib,
			hou.attribType.Global: geo.findGlobalAttrib,
		}  # type: _t.Dict[hou.attribType, _t_attr_getter]
		self.__attr_getters = {
			k: all_getters[k] for k in self.__attr_types_priority
		}  # type: _t.Dict[hou.attribType, _t_attr_getter]

	@property
	def geo(self):  # type: () -> hou.Geometry
		return self.__geo

	@geo.setter
	def geo(self, value):
		self.__set_geo(value)
		self.__rebuild_attr_getters()

	@property
	def attr_types(self):  # type: () -> _t.Tuple[hou.attribType, ...]
		return self.__attr_types_priority

	@attr_types.setter
	def attr_types(self, attr_tps_priority):  # type: (_t_at_arg) -> ...
		self.__set_attr_types(attr_tps_priority)
		self.__rebuild_attr_getters()

	def attr_find(
		self,
		attr_nm,  # type: str
		ok_multi=False,  # type: bool
		ok_not_found=False,  # type: bool
		error_attr_nice_nm='',  # type: str
		default_name='',  # type: str
		test_name_f=None,    # type: _t.Callable[[...], str]
	):  # type: (...) -> _O[hou.Attrib]
		"""
		`None` is returned only if `ok_not_found` is `True`.

		In all other cases, either a `hou.NodeError` is raised or a valid `hou.Attrib` is returned.

		:param test_name_f: A function generated with `test_name_factory`.
		"""
		if not callable(test_name_f):
			test_name_f = test_name_p_reserved
		attr_nm = test_name_f(
			attr_nm, error_attr_nice_nm=error_attr_nice_nm, entity_type='attribute',
			default_name=default_name, default_name_always_ok=False
		)

		attr_tps_priority = self.attr_types

		attr_getters = self.__attr_getters
		found = [
			(tp, attr_getters.get(tp, _dummy)(attr_nm))
			for tp in attr_tps_priority
		]  # type: _t.List[_t.Tuple[hou.attribType, hou.Attrib]]
		found = [(tp, a) for tp, a in found if a]

		if not found:
			if ok_not_found:
				return None
			raise hou.NodeError("No such {{{a_tps}}} {nice}attribute: {a}".format(
				a=repr(attr_nm), nice=format_prefix(error_attr_nice_nm),
				a_tps=format_comma_and([x.name() for x in attr_tps_priority], _or=True)
			))
		if len(found) == 1:
			attr_tp, attr = found[0]
			return attr
		if len(found) > 1 and not ok_multi:
			raise hou.NodeError("Multiple instances of {nice}attribute {a} are found: {tps}".format(
				a=repr(attr_nm), nice=format_prefix(error_attr_nice_nm),
				tps=format_comma_and(tp.name() for tp, a in found)
			))

		assert len(found) > 1 and ok_multi

		# We need to sort them by priority:
		type_priorities = {tp: i for i, tp in enumerate(attr_tps_priority)}  # type: _t.Dict[hou.attribType, int]
		found = sorted(found, key=lambda tp_a: type_priorities.get(tp_a[0]))

		attr_tp, attr = found[0]
		return attr

	def attr_test(
		self,
		attr_nm,  # type: str
		data_types,  # type: _t_dt_arg
		sizes,  # type: _t_sz_arg
		ok_multi=False,  # type: bool
		ok_not_found=False,  # type: bool
		is_array=False,  # type: _O[bool]
		error_attr_nice_nm='',  # type: str
		default_name='',  # type: str
		test_name_f=None,
	):  # type: (...) -> _O[hou.Attrib]
		"""
		`None` is returned only if `ok_not_found` is `True`.

		In all other cases, either a `hou.NodeError` is raised or a valid `hou.Attrib` is returned.
		"""
		attr = self.attr_find(
			attr_nm, ok_multi=ok_multi, ok_not_found=ok_not_found,
			error_attr_nice_nm=error_attr_nice_nm, default_name=default_name,
			test_name_f=test_name_f,
		)
		if attr is None:
			return None

		assert isinstance(attr, hou.Attrib)

		if is_array is not None and bool(attr.isArrayType()) != bool(is_array):
			raise hou.NodeError("{a} is{_not} an array attribute{a_brackets}".format(
				a=repr(attr_nm), _not=' not' if is_array else '',
				a_brackets=format_postfix(error_attr_nice_nm)
			))

		_test_attr_dt(attr, data_types, error_attr_nice_nm=error_attr_nice_nm)
		_test_attr_sz(attr, sizes, error_attr_nice_nm=error_attr_nice_nm)

		return attr


def assert_arg_type(val, _class):  # type: (_t.Any, _t.Type[_T]) -> _T
	if not isinstance(val, _class):
		raise TypeError("Not a {{{}}}: {}".format(_class.__name__, repr(val)))
	return val


def assert_str(val):  # type: (...) -> str
	if not isinstance(val, _str_types):
		raise TypeError("Not a string: {}".format(repr(val)))
	return val


class NodeGeoProcessorBase(object):
	"""
	A base class to build per-asset input processors.
	Implements nothing but two properties (`node` and `geo`) which error-check
	that a valid `SopNode`/`Geometry` instances are returned.
	"""
	def __init__(
		self,
		node,  # type: hou.SopNode
	):
		self.__node = node
		self.__geo = None

	@property
	def node(self):
		return assert_arg_type(self.__node, hou.SopNode)  # type: hou.SopNode

	@property
	def geo(self):
		geo = self.__geo
		if geo is None:
			self.__geo = geo = assert_arg_type(self.node.geometry(), hou.Geometry)  # type: hou.Geometry
		return geo
