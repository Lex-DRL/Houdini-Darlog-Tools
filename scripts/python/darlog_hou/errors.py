# encoding: utf-8
"""
"""
import hou
import hou as _hou

import typing as _t
from typing import Optional as _O, Union as _U

from functools import wraps as _wraps
from itertools import chain as _chain
import errno as _errno
import os as _os
from traceback import format_exception as _format_exception

from darlog_hou.py23 import str_format as _format

# noinspection PyTypeHints,PyShadowingBuiltins
_T = _t.TypeVar('T')
_t_Exception = _t.Union[Exception, _hou.Error]
# noinspection PyTypeHints
_T_Exception = _t.TypeVar('T_Exception', bound=_t_Exception)

# noinspection PyBroadException
try:
	_unicode = unicode
	_str_types = (str, unicode)
except Exception:
	_unicode = str
	_str_types = (str, )


any_exception = (Exception, _hou.Error)
any_base_exception = (BaseException, _hou.Error)


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

	def decorator(f: _t.Callable):
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
		return _wraps(f)(new_f)  # Manually apply `@_wraps(f)` decorator to the one function chosen above

	if func is None:
		return decorator
	return decorator(func)


def raise_errors_as(
	func: _t.Callable = None, *,
	type_to: _t.Type[_T_Exception] = hou.NodeError,
	type_from: _U[_t.Type[_T_Exception], _t.Tuple[_t.Type[_T_Exception], ...]] = any_exception,
):
	"""Func-decorator which re-raises error types specified in `type_from` as another error type, `type_to`."""
	def decorator(f: _t.Callable):
		assert isinstance(type_to, type) and issubclass(type_to, any_base_exception), "Not an exception type to raise: {}".format(repr(type_to))
		caught_types: _t.Tuple[_t.Type[_T_Exception], ...] = (
			(type_from,)
			if isinstance(type_from, type) and issubclass(type_from, any_base_exception)
			else tuple(type_from)
		)
		if len(caught_types) == 1 and caught_types[0] is type_to:
			# A user has done something stupid: they try to catch and re-raise the same type.
			# Just return the original function untouched:
			return f

		# To avoid unnecessary type casts, we need to exclude type_to from caught_types.
		# We DO NOT want to consider subclasses in any direction: a user might want
		# to explicitly turn a base exception class to a child one or vice versa.
		caught_types = tuple(
			x for x in caught_types if x is not type_to
		)
		assert (
			caught_types and isinstance(caught_types, tuple) and all(
				isinstance(x, type) and issubclass(x, any_base_exception) for x in caught_types
			)
		), "Not valid original exception types: {}".format(repr(caught_types))

		@_wraps(f)
		def new_f(*args, **kwargs):
			try:
				return f(*args, **kwargs)
			except caught_types as e:
				if type(e) is type_to:
					raise e
					return
				msg = get_error_message(e, default=str(e))
				raise type_to(msg)

		return new_f

	if func is None:
		return decorator
	return decorator(func)


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

	if isinstance(error, OSError):
		msg = format_os_error(error, use_tabs=False)

	if msg is None:
		try:
			msg = error.args[0]
		except any_exception:
			pass

	if msg is None:
		msg = default

	try:
		if callable(msg):
			msg = msg()
		if not(msg is None or isinstance(msg, str)):
			msg = str(msg)
		return msg
	except any_exception:
		return default


def default_oserror(errno, *oserror_args):
	"""
	Creates an `OSError` with the default message for the given errno.
	The first optional argument is the error's path.
	"""
	all_args = [errno, _os.strerror(errno)]
	all_args.extend(oserror_args)
	oserror_args = tuple(all_args)
	return OSError(*oserror_args)


def format_os_error(
	err,  # type: OSError
	use_tabs=True
):
	if not isinstance(err, OSError):
		return get_error_message(err, '')

	code_str = (
		_os.strerror(err.errno)
		# errno.errorcode[err.errno]
		if (err.errno in _errno.errorcode.keys())
		else ''
	)
	if use_tabs:
		pre_tab = '\t'
		mid_tab = ':\t'
	else:
		pre_tab = ''
		mid_tab = ': '

	return (
		code_str + mid_tab + err.filename
		if code_str
		else pre_tab + err.filename
	)


def format_error(err, tab_level=0):
	lines = _format_exception(type(err), err, err.__traceback__)
	tab_level = max(int(tab_level), 0)
	try:
		pattern = '{}{}'.format('\t' * tab_level, '{}')
		lines = [pattern.format(x) for x in lines]
	except any_exception:
		pattern = u'{}{}'.format('\t' * tab_level, '{}')
		lines = [pattern.format(x) for x in lines]

	try:
		return ''.join(lines).rstrip('\n\r')
	except any_exception:
		return u''.join(lines).rstrip('\n\r')


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
