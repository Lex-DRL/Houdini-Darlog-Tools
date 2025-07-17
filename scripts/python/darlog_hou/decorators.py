# encoding: utf-8
"""
The most common/generic decorators.
"""

__author__ = 'Lex Darlog (DRL)'

import typing as _t

_T = _t.TypeVar('T')


def setattr_decorator(_cls=None, *_, attr: str = None, value=None):
	"""
	Class decorator which attaches a reused method with 'setattr' - to build those classes
	with composition instead of inheritance.
	"""
	def wrap(cls):
		setattr(cls, attr, value)
		return cls

	if _cls is None:
		return wrap
	return wrap(_cls)
