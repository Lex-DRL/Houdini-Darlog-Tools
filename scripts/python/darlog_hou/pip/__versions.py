# encoding: utf-8

import re as _re

from .__shared import safe_format as _format, _str_types, _izip_longest

try:
	import typing as _t

	# noinspection PyTypeHints,PyShadowingBuiltins
	_T = _t.TypeVar('T')
	_t_version = _t.Union[None, int, str]
	_t_version_arg = _t.Union[_t_version, _t.Iterable[_t_version]]
except ImportError:
	pass


_re_alphanumeric_split = _re.compile(
	'([a-zA-Z]+|[0-9]+)'
	'([a-zA-Z0-9]*)'
).match
_re_digits_only = _re.compile('[0-9]+$').match


def _str_subversion_alphanumeric_gen(
	subversion  # type: str
):
	assert isinstance(subversion, _str_types)
	ending = subversion
	while ending:
		alpha_split = _re_alphanumeric_split(ending)
		if not alpha_split:
			return

		first, ending = alpha_split.groups()  # type: str
		try:
			yield int(first)
		except ValueError:
			yield first


def _str_subversion_no_dashes_gen(
	subversion  # type: str
):
	assert isinstance(subversion, _str_types) and '-' not in subversion
	for v_dot in subversion.split('.'):
		if not v_dot:
			continue
		for v_dot_underscore in v_dot.split('_'):
			if not v_dot_underscore:
				continue
			for v_split in v_dot_underscore.split():
				for v in _str_subversion_alphanumeric_gen(v_split):
					yield v


def _str_subversion_gen(
	subversion  # type: str
):
	"""
	From:

	``'1 2.3a4_5 , or unsupported ; chars - abracadabra1 or 2lumos-beta 1.2 # or other unsupported'``

	To:

	``(1, 2, 3, 'a', 4, 5, 'abracadabra1 or 2lumos', 'beta 1.2')``
	"""
	dash_parts = [x for x in subversion.split('-') if x]
	if not dash_parts:
		return
	rest_parts = iter(dash_parts)
	first_part = next(rest_parts)
	for v in _str_subversion_no_dashes_gen(first_part):
		yield v
	# Every part separated with dash - returned as is:
	for v in rest_parts:
		yield v


def flat_version_gen(
	version  # type: _t_version_arg
):
	"""Convert version from (presumably) any format to a standard form: a sequence of ints/strings."""
	if not version:
		yield 0
		return
	if isinstance(version, int):
		yield int(version)
		return

	if isinstance(version, _str_types):
		for v in _str_subversion_gen(version):
			yield v
		return

	try:
		version_i = iter(version)
	except Exception:
		raise ValueError(_format(
			"Unsupported version value: {}", repr(version)
		))
	for ver in version_i:
		for v in flat_version_gen(ver):
			yield v


def _is_pre_version(subversion):
	if not isinstance(subversion, _str_types):
		return False
	str_lower = subversion.lower()
	return str_lower.startswith('rc') or any(
		x in str_lower
		for x in ['alpha', 'beta', 'release candidate']
	)


def verify_version(actual_version, min_version):  # type: (_t_version_arg, _t_version_arg) -> bool
	"""Checks whether the current module version matches the given requirement."""
	for min_v, act_v in _izip_longest(
		flat_version_gen(min_version),
		flat_version_gen(actual_version),
		# TODO: max_version
		fillvalue=None
	):
		act_is_pre = _is_pre_version(act_v)
		if min_v is None:
			if not act_is_pre:
				return True
			min_v = 0
		if act_v is None:
			act_v = 0

		if min_v == act_v:
			continue

		# Sub-versions aren't equal. I.e., one of them is definitely bigger than the other in this iteration.

		min_is_int = isinstance(min_v, int)
		act_is_int = isinstance(act_v, int)
		if min_is_int == act_is_int:
			# Both sub-versions are of the same type (int/str):
			return min_v < act_v

		if act_is_pre:
			return False
		if act_is_int and _is_pre_version(min_v):
			return True

		# One of sub-versions is a string, while the other one is a regular int.
		int_val = act_v if act_is_int else min_v  # type: int

		# In versions, there are two possible cases:
		# * Any string part is always smaller than int. I.e.: 1.2.3a is smaller than 1.2.3.1
		# * ... except when int is 0. In this case, any string is bigger. I.e., 1.2.3a is bigger than 1.2.3.0

		# So, 0 flips the condition:
		if int_val == 0:
			# (min = 1.2.3{a}, act = 1.2.3.{0}) -> False
			# (min = 1.2.3{0}, act = 1.2.3.{a}) -> True <- min_is_int
			return min_is_int
		# (min = 1.2.3{a}, act = 1.2.3.{1}) -> True <- act_is_int
		# (min = 1.2.3{1}, act = 1.2.3.{a}) -> False
		return act_is_int

	# We've checked all the parts and they match. The versions are exactly the same:
	return True
