# encoding: utf-8
"""
Various utility functions to facilitate work with geometry attributes.
v2
"""

__author__ = 'Lex Darlog (DRL)'

from re import compile as _re_compile


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
