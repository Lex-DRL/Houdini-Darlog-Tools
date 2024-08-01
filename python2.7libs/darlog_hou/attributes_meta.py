# encoding: utf-8
"""
Module containing common tools to work with "META" sub-network.
I.e., a special chain of nodes in custom asset dedicated to input pre-validation and cleanup.
"""

__author__ = 'Lex Darlog (DRL)'

import typing as _t

from traceback import format_exception_only as _format_exception_only

import hou

from .attributes_2 import (
	clean_attr_name as _clean_attr_name,
	find_or_create as _find_or_create,
	AttributeTypeSpecifier as _Specifier
)
from .errors import any_exception as _any_exception


_T = _t.TypeVar('T')

_t_catch_error_internal_f = _t.Callable[[hou.SopNode, hou.Geometry], _t.Any]


# noinspection PyBroadException
try:
	from typing import Protocol

	class _CaughtFunction(Protocol):
		def __call__(self, node: hou.SopNode, geo: hou.Geometry, *args, **kwargs) -> _t.Any: ...
except Exception:
	_CaughtFunction = _t.Callable


def _dummy(main_arg: _T, *args, **kwargs) -> _T:
	return main_arg


def _always_false(*args, **kwargs) -> bool:
	return False


def _swallow_error_namespace(error_lines: _t.List[str]):
	if not error_lines:
		return error_lines
	first_line: str = error_lines[0]
	split = first_line.split(':')
	if not split or not split[0]:
		return error_lines
	namespace = split[0].split('.')
	split[0] = namespace[-1] if namespace else ''
	error_lines[0] = ':'.join(split)
	return error_lines


_error_str_specifier = _Specifier.from_unsafe_args(hou.attribType.Global, hou.attribData.String, 1, False)
_error_flag_specifier = _Specifier.from_unsafe_args(hou.attribType.Global, hou.attribData.Int, 1, False)


def catch_error_to_attr(
	func: _CaughtFunction = None, *_,
	skip_if_pre_error=False, swallow_namespace=True, sep: str = '\n\n', join_format: str = '{prev_msg}{sep}{err}',
	error_types: _t.Union[type, _t.Tuple[type, ...]] = None,
	error_attr: str = 'error',
	error_flag_attr: _t.Optional[str] = 'errorDo',
):
	"""
	A function decorator: catches any errors (of given types) and redirects their messages
	to a global 'error' attribute.
	"""
	error_types = error_types if error_types else _any_exception
	_any_base_exception = (BaseException, hou.Error)
	assert (
		(isinstance(error_types, type) and issubclass(error_types, _any_base_exception)) or
		(isinstance(error_types, tuple) and error_types and all(
			isinstance(x, type) and issubclass(x, _any_base_exception) for x in error_types
		))
	), 'Invalid error types: {}'.format(repr(error_types))

	# Main 'error' attr - MUST have a valid name:
	error_attr = error_attr if error_attr else ''
	assert isinstance(error_attr, str), 'Invalid error-attribute name: {}'.format(repr(error_attr))
	error_attr = _clean_attr_name(error_attr)
	error_attr = error_attr if error_attr else 'error'

	# Optional 'errorDo' - might be not set. In such case, it's ignored.
	error_flag_attr = error_flag_attr if error_flag_attr else ''
	assert isinstance(error_flag_attr, str), 'Invalid error-flag-attribute name: {}'.format(repr(error_flag_attr))
	error_flag_attr = _clean_attr_name(error_flag_attr)
	error_flag_attr = error_flag_attr if error_flag_attr else None

	if not sep:
		sep = ''
	if not isinstance(sep, str):
		sep = str(sep)
	assert isinstance(sep, str)

	if not isinstance(join_format, str):
		join_format = '{prev_msg}{sep}{err}'
	assert isinstance(join_format, str)

	# To make the main func unconditional - construct it's conditional segments and pre-choose between them:

	do_flag = error_flag_attr is not None

	def get_flag_attr(node: hou.SopNode, geo: hou.Geometry) -> hou.Attrib:
		return _find_or_create(error_flag_attr, _error_flag_specifier, node=node, geo=geo, override=True, default=0)

	def is_early_exit_by_flag(node: hou.SopNode, geo: hou.Geometry) -> int:
		return geo.attribValue(get_flag_attr(node, geo))

	def is_early_exit_by_message(node: hou.SopNode, geo: hou.Geometry) -> str:
		attr = _find_or_create(error_attr, _error_str_specifier, node=node, geo=geo, override=True, default='')
		return geo.attribValue(attr)

	is_early_exit_by_pre_error_f: _t_catch_error_internal_f = _always_false if not skip_if_pre_error else (
		is_early_exit_by_flag if do_flag else is_early_exit_by_message
	)

	def set_error_flag(node: hou.SopNode, geo: hou.Geometry):
		geo.setGlobalAttribValue(get_flag_attr(node, geo), 1)

	post_set_flag_f: _t_catch_error_internal_f = set_error_flag if do_flag else _dummy

	swallow_namespace_f = _swallow_error_namespace if swallow_namespace else _dummy

	def wrap(old_f: _CaughtFunction):
		def new_f(node: hou.SopNode, geo: hou.Geometry, *args, **kwargs):
			if is_early_exit_by_pre_error_f(node, geo):
				return

			e = None
			try:
				return old_f(node, geo, *args, **kwargs)
			except error_types as _e:
				e = _e
			msg: str = geo.attribValue(error_attr)
			msg = msg.strip()
			err_lines = [x.strip() for x in _format_exception_only(type(e), e)]
			err_lines = swallow_namespace_f(err_lines)
			err_str = '\n'.join(err_lines)
			msg = err_str if not msg else join_format.format(prev_msg=msg, sep=sep, err=err_str)
			geo.setGlobalAttribValue(error_attr, msg)
			post_set_flag_f(node, geo)

		try:
			new_f.__name__ = old_f.__name__
		except _any_exception:
			pass
		return new_f

	if func is None:
		return wrap
	return wrap(func)
