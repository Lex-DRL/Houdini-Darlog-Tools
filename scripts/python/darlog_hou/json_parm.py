# encoding: utf-8
"""
Utility functions to work with a pre-processing JSON parm inside custom assets.
"""

from json import loads as _loads

from darlog_hou.errors import any_exception

try:
	import typing as _t

	# noinspection PyTypeHints,PyShadowingBuiltins
	_T = _t.TypeVar('T')
except ImportError:
	pass


def dict_key(json_dict_str, default, *keys_sequence):  # type: (_t.AnyStr, _t.Any, ...) -> _t.Any
	if not keys_sequence:
		return default

	data = _loads(json_dict_str)  # type: dict
	for key in keys_sequence:
		# noinspection PyBroadException
		try:
			data = data[key]
		except any_exception:
			return default
	return data
