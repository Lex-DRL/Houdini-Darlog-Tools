# encoding: utf-8
"""
Python code for `uvMesh` sop node.
"""

__author__ = 'Lex Darlog (DRL)'

import hou

from collections import OrderedDict
from json import dumps

from darlog_hou.attributes import CommonAttribsValidator
from darlog_hou.errors import catch_error_message

try:
	import typing as _t
except ImportError:
	pass


class Data:
	def __init__(self):
		self.attr_nm = ''
		self.attr_is_vtx = False
		self.kept_vtx_attrs = []  # type: _t.List[str]
		self.kept_pt_attrs = ['P', ]  # type: _t.List[str]
		self.vector_size = 0

		self.rename_do = False

		self.error_do = False
		self.error = []  # type: _t.List[str]


_sizes = (2, 3, 4)


class InputProcessorParm(CommonAttribsValidator):
	__data = None

	@property
	def _data(self):
		res = self.__data
		if res is None:
			self.__data = res = Data()
		return res

	def _out_data_dict(self):
		res = OrderedDict(sorted(
			(k, v)
			for k, v in self._data.__dict__.items()
			if not k.startswith('_')
		))
		res['error'] = '\n'.join(res['error'])
		return res

	def _add_error(self, message):  # type: (str) -> _t.Any
		self._data.error_do = True
		self._data.error.append(message)

	def _main(
		self,
		attr_nm  # type: str
	):
		attr = self.test_uv(attr_nm, sizes=_sizes)[0]

		self._data.attr_nm = attr_nm = attr.name()
		self._data.attr_is_vtx = is_vtx = (attr.type() == hou.attribType.Vertex)
		self._data.rename_do = attr_nm != 'uv'
		self._data.vector_size = attr.size()

		kept_attrs_list = self._data.kept_vtx_attrs if is_vtx else self._data.kept_pt_attrs
		kept_attrs_list.append(attr_nm)

	def json_str(
		self,
		attr_nm  # type: str
	):
		_ = self._data
		caught_error, msg = catch_error_message(
			lambda: self._main(attr_nm),
			''
		)
		if caught_error is not None:
			self._add_error(msg)
		return dumps(self._out_data_dict(), indent=1)
