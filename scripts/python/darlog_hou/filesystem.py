# encoding: utf-8
"""
Utility functions to work with files/dirs from within Houdini.
"""

__author__ = 'Lex Darlog (DRL)'


try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass

import errno as _errno
import os as _os
from os import path as _path
from shutil import rmtree as _rmtree

from darlog_hou.errors import (
	default_oserror as _default_oserror,
	format_os_error as _format_os_error,
	_str_types
)


_win_slash = "q\\q"[1]
_slash = '/'


def empty_dir(
	*dir_paths,
	suppress_errors=True,
	print_errors=True
):
	"""
	This function removes all the contained files/folders in the given parent folders,
	effectively making them empty.
	"""

	def clean_single_arg(str_arg):
		if not isinstance(str_arg, _str_types):
			return str_arg
		if not str_arg:
			return None
		str_arg = str_arg.lstrip().replace(_win_slash, _slash)
		while '//' in str_arg:
			str_arg = str_arg.replace('//', _slash)
		return str_arg

	paths = tuple(
		p for p in (
			clean_single_arg(a) for a in dir_paths
		) if p
	)  # type: _t.Tuple[_t.AnyStr, ...]

	errors = list()  # type: _t.List[OSError]

	if not paths:
		return tuple(errors)

	def clean_error_path(path):
		if not(path and isinstance(path, _str_types)):
			return path
		return path.replace(_win_slash, _slash)

	def handle_error_raising(
		error,  # type: OSError
	):
		error.filename = clean_error_path(error.filename)
		raise error

	def handle_error_adding(
		error,  # type: OSError
	):
		if not error.message and error.errno in _errno.errorcode:
			error.message = _os.strerror(error.errno)
		error.filename = clean_error_path(error.filename)
		errors.append(error)

	handle_error_f = handle_error_adding if suppress_errors else handle_error_raising

	def on_rmtree_error(
		function,  # type: _t.Callable
		path,  # type: _t.AnyStr
		excinfo
	):
		try:
			function(path)
		except OSError as e:
			handle_error_f(e)

	def empty_single(dir_path):
		try:
			do_exist = _path.exists(dir_path)
		except TypeError:
			handle_error_f(
				_default_oserror(_errno.ENOENT, repr(dir_path))
			)
			return
		if not do_exist:
			return
		if not _path.isdir(dir_path):
			handle_error_f(
				_default_oserror(_errno.ENOTDIR, repr(dir_path))
			)
			return

		for subpath in _os.listdir(dir_path):
			if not subpath:
				continue
			cur_path = _path.join(dir_path, subpath).replace(_win_slash, _slash)
			cur_path = cur_path.rstrip(_slash)
			is_dir = _path.isdir(cur_path)
			try:
				if is_dir:
					_rmtree(cur_path, onerror=on_rmtree_error)
				else:
					_os.remove(cur_path)
			except OSError as sub_er:
				handle_error_f(sub_er)

	for path in paths:
		empty_single(path)

	if print_errors and errors:
		print('\n'.join(
			_format_os_error(e) for e in errors
		))

	return tuple(errors)
