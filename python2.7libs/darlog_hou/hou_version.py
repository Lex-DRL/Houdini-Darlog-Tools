# encoding: utf-8
"""
A utility module to query/verify version of Houdini.
"""

__author__ = 'Lex Darlog (DRL)'

import typing as _t
from typing import Optional as _O, Union as _U
from itertools import dropwhile as _dropwhile

import hou as _hou


def version() -> _t.Tuple[int, ...]:
	"""Just a typed alias for ``hou.applicationVersion()``"""
	return _hou.applicationVersion()


def no_trailing_zeroes(*ver: _U[int, _t.AnyStr]) -> _t.Tuple[_U[int, _t.AnyStr], ...]:
	"""Remove trailing zeroes from a version."""
	reversed_no_zeroes = tuple(
		_dropwhile(
			lambda x: (
				(isinstance(x, int) and x == 0)
				or (isinstance(x, str) and (x == "0" or not x))
			),
			reversed(ver)
		)
	)
	return tuple(reversed(reversed_no_zeroes))


def verify_min(*min_ver, asset: _O[_hou.Node] = None):
	"""
	Ensure that the currently running Houdini has at least the given version.
	Useful to be called as a separate python node in the very beginning of SOP assets.
	"""
	if not min_ver:
		return

	hou_ver = version()
	hou_ver = no_trailing_zeroes(*hou_ver)
	if hou_ver < min_ver:
		msg = "Houdini {} or above is required (current: {})".format(
			'.'.join(str(v) for v in min_ver),
			'.'.join(str(v) for v in hou_ver)
		)
		msg_print = ""
		if not isinstance(asset, _hou.Node):
			msg_print = "\n\n{}".format(msg)
		else:
			msg_print = "\n\n{} for node:\n{}".format(msg, repr(asset))
			msg = "{} for {} asset type".format(
				msg,
				repr(asset.type().name())
			)
		print(msg_print)
		raise _hou.NodeError(msg)
