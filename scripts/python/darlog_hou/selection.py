# encoding: utf-8
"""
Utility functions to work with Houdini selection.
"""

__author__ = 'Lex Darlog (DRL)'

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t

	# noinspection PyTypeHints,PyShadowingBuiltins
	_T = _t.TypeVar('T')
except ImportError:
	pass

import hou

from darlog_hou.errors import (
	any_exception as _any_exception,
	format_error as _format_error
)


class KeepSelectionContext:
	"""A context-manager class which remembers current selection before entering the block and restores it on exit."""

	def __init__(self, include_hidden=True, suppress_restore_errors=True):
		super(KeepSelectionContext, self).__init__()
		self.__pre_selection = tuple()  # type: _t.Tuple[hou.NetworkMovableItem, ...]
		self.include_hidden = include_hidden
		self.suppress_restore_errors = suppress_restore_errors

	@property
	def pre_selection(self):  # type: () -> _t.Tuple[hou.NetworkMovableItem, ...]
		return self.__pre_selection

	def __enter__(self):
		try:
			self.__pre_selection = hou.selectedItems(include_hidden=self.include_hidden)
		except _any_exception:
			self.__pre_selection = hou.selectedItems()

	def __exit__(self, exc_type, exc_val, exc_tb):
		try:
			hou.clearAllSelected()
		except _any_exception:
			pass

		if self.suppress_restore_errors:
			for item in self.__pre_selection:
				try:
					item.setSelected(True)
				except _any_exception:
					pass
			return

		# when we do need to inform a user about issues with selection restore:
		items_with_errors = list()  # type: _t.List[_t.Tuple[hou.NetworkMovableItem, _t.Union[Exception, hou.Error]]]
		for item in self.__pre_selection:
			try:
				item.setSelected(True)
			except _any_exception as e:
				items_with_errors.append((item, e))

		if items_with_errors:
			error_strings = (
				'{}:\n{}'.format(repr(item), _format_error(ex, tab_level=1))
				for item, ex in items_with_errors
			)
			print("Errors occurred on attempt to restore selection:", *error_strings, sep='\n\n')


def keep_selection(func=None, *_, include_hidden=True, suppress_restore_errors=True):
	"""A shorthand decorator which wraps an entire function with `KeepSelectionContext()`."""
	def wrap(old_f):  # type: (_t.Callable[..., _T]) -> _t.Callable[..., _T]
		def new_f(*args, **kwargs):
			with KeepSelectionContext(include_hidden, suppress_restore_errors):
				return old_f(*args, **kwargs)

		try:
			new_f.__name__ = old_f.__name__
		except _any_exception:
			pass
		return new_f

	if func is None:
		return wrap
	return wrap(func)
