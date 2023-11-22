# encoding: utf-8
"""
"""

import hou as _hou

from itertools import chain as _chain

from darlog_hou.py23 import str_format as _format

try:
	import typing as _t

	# noinspection PyTypeHints,PyShadowingBuiltins
	_T = _t.TypeVar('T')
	_t_Exception = _t.Union[Exception, _hou.Error]
	# noinspection PyTypeHints
	_T_Exception = _t.TypeVar('T_Exception', bound=_t_Exception)
except ImportError:
	pass

# noinspection PyBroadException
try:
	_unicode = unicode
	_str_types = (str, unicode)
except Exception:
	_unicode = str
	_str_types = (str, )


any_exception = (Exception, _hou.Error)


def assert_arg_type(val, _class):  # type: (_t.Any, _t.Type[_T]) -> _T
	if not isinstance(val, _class):
		raise TypeError(_format("Not a {{{}}}: {}", _class.__name__, repr(val)))
	return val


def assert_str(val):  # type: (...) -> str
	if not isinstance(val, _str_types):
		raise TypeError(_format("Not a string: {}", repr(val)))
	return val


def assert_sop_node(node, error_name=''):  # type: (...) -> _hou.SopNode
	if node is None:
		raise TypeError(_format("No SOP node provided as {}", error_name) if error_name else 'No SOP node provided')
	if not isinstance(node, _hou.SopNode):
		raise TypeError(
			_format("Not a SOP node ({}): {}", error_name, repr(node))
			if error_name else
			_format("Not a SOP node: {}", repr(node))
		)
	return node


def _assert_sop_node_geo(node, error_name=''):  # type: (_hou.SopNode, str) -> _hou.Geometry
	geo = node.geometry()  # type: _hou.Geometry
	if not geo:
		raise ValueError(
			_format("SOP node ({}) has no geometry: {}", error_name, repr(node))
			if error_name else
			_format("SOP node has no geometry: {}", repr(node))
		)
	return geo


def sop_node_geo(node, error_name=''):  # type: (...) -> _hou.Geometry
	return _assert_sop_node_geo(assert_sop_node(node, error_name), error_name)


def sop_input_geo(node, index=0, error_name=''):  # type: (...) -> _hou.Geometry
	node = assert_sop_node(node, error_name)
	geo = node.inputGeometry(index)  # type: _hou.Geometry
	if not geo:
		raise ValueError(
			_format("SOP node ({}) has no geometry at input {}: {}", error_name, index, repr(node))
			if error_name else
			_format("SOP node has no geometry at input {}: {}", index, repr(node))
		)
	return geo


def catch_error_message(
	func,  # type: _t.Callable
	default=None,  # type: _T
	error_types=any_exception  # type: _t.Tuple[_t.Type[_T_Exception], ...]
):  # type: (...) -> _t.Tuple[_t.Optional[_T_Exception], _t.Union[_T, _t.AnyStr]]
	"""
	Run the function, catch exception if raised and return two values:

	* The error object itself if there was one, `None` otherwise.
	* Error message or the default value (if no error or if it's we couldn't detect it's error message).
	"""
	try:
		func()
		return None, default
	except error_types as e:
		return e, get_error_message(e, default=default)


def catch(
	func=None,  # type: _t.Callable
	with_message=None,  # type: _t.Optional[_t.Callable[[str, ...], _T]]
	with_error=None,  # type: _t.Optional[_t.Callable[[_T_Exception, ...], _T]]
	message_default='',  # type: _t.Any
	error_types=any_exception  # type: _t.Tuple[_t.Type[_T_Exception], ...]
):
	"""
	Convenient decorator catching any of the provided exception types and calling an alternative function instead,
	passing either error message or error itself to it.
	"""

	def wrap(
		f  # type: _t.Callable
	):
		def catch_and_do_nothing(*args, **kwargs):
			try:
				return f(*args, **kwargs)
			except error_types:
				return None

		def catch_error(*args, **kwargs):
			try:
				return f(*args, **kwargs)
			except error_types as e:
				return with_error(e, *args, **kwargs)

		def catch_message(*args, **kwargs):
			try:
				return f(*args, **kwargs)
			except error_types as e:
				return with_message(get_error_message(e, default=message_default), *args, **kwargs)

		new_f = catch_message if callable(with_message) else (
			catch_error if callable(with_error) else catch_and_do_nothing
		)
		try:
			new_f.__name__ = f.__name__
		except any_exception:
			pass
		return new_f

	if func is None:
		return wrap
	return wrap(func)


def catch_and_return_error_message(
	func=None,  # type: _t.Callable
	format=':{}',
):
	"""
	A shorthand decorator for:

	`catch(with_message=lambda m, *a, **kw: _format(format, m))`
	"""
	if not format:
		format = ''

	def error_formatter(
		m,  # type: str
		*a, **kw
	):
		return _format(format, m)

	return catch(func, with_message=error_formatter)


def get_error_message(error, default=None):  # type: (_t_Exception, _T) -> _t.Union[_T, _t.AnyStr]
	"""Get a message from an error regardless of it's type."""
	if isinstance(error, _hou.Error):
		return error.instanceMessage()

	msg = None
	try:
		msg = error.message
	except any_exception:
		pass

	if msg is None:
		try:
			msg = error.args[0]
		except any_exception:
			pass

	if msg is None:
		msg = default

	try:
		return msg() if callable(msg) else msg
	except any_exception:
		return default


def _update_builtin_error_message(
	error, format_str, **kwargs
):  # type: (_T_Exception, _t.AnyStr, ...) -> _T_Exception
	assert isinstance(error, Exception)
	msg = ''
	has_message = False

	try:
		msg = error.message
		has_message = True
	except any_exception:
		try:
			msg = error.args[0]
		except any_exception:
			# There's nothing to update (or at least we don't know how to).
			# Return the error unchanged:
			return error

	if callable(msg):
		msg = msg()
		has_message = False  # We shouldn't override `message` function on the instance with a string attribute.

	msg = _format(format_str, old=msg, **kwargs)
	if has_message:
		error.message = msg

	try:
		error.args = tuple(_chain([msg], error.args[1:]))
	except any_exception:
		# Nah... The (custom?) exception doesn't have `args` attribute
		pass

	return error


def update_error_message(
	error, format_str, **kwargs
):  # type: (_T_Exception, _t.AnyStr, ...) -> _T_Exception
	"""
	Replace the message in given exception according to the given format-string
	('{old}' pattern in place of original message).

	For Houdini error types, a new exception instance is returned,
	while for the built-in ones an in-place modification is attempted.
	If the attempt fails, exception is returned unchanged.
	"""
	if isinstance(error, _hou.Error):
		# For houdini errors, we kinda have to recreate it:
		hou_error_type = type(error)
		return hou_error_type(_format(format_str, old=error.instanceMessage(), **kwargs))

	try:
		return _update_builtin_error_message(error, format_str, **kwargs)
	except any_exception:
		# The last thing we might want is raising a new exception while handling a caught one.
		# So, return it as is:
		return error
