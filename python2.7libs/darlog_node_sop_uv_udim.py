# encoding: utf-8
"""
Python code for `uvUDIM` sop node.
"""

__author__ = 'Lex Darlog (DRL)'

import hou

from collections import OrderedDict
from json import dumps

from darlog_hou.attributes import CommonAttribsValidator, test_name_p_reserved
from darlog_hou.errors import catch_error_message
from darlog_hou.py23 import str_format as _format


internal_uv_name = 'uv'
internal_udim_name = 'udim'


class InputValidatorParm(CommonAttribsValidator):

	@property
	def data_dict(self):
		try:
			return self.__data_dict
		except AttributeError:
			pass

		# noinspection PyAttributeOutsideInit
		self.__data_dict = data = OrderedDict([
			('uv_is_pt', False),
			# ('uv_rename', False),
			# ('udim_rename', False),
			('error', ''),
		])
		return data

	def _main(self, uv_attr_nm, out_udim_attr_nm):
		data = self.data_dict
		uv_attr = self.test_uv(uv_attr_nm)[0]
		uv_attr_nm = uv_attr.name()
		data['uv_is_pt'] = uv_attr.type() == hou.attribType.Point
		# data['uv_rename'] = uv_attr_nm != internal_uv_name

		out_udim_attr_nm = test_name_p_reserved(out_udim_attr_nm, 'output UDIM')
		if out_udim_attr_nm == uv_attr_nm:
			raise ValueError(_format(
				"Output UDIM attribute can't have the same name as the main UV attribute: {}", repr(out_udim_attr_nm)
			))
		# data['udim_rename'] = out_udim_attr_nm != internal_udim_name

	def json_str(self, uv_attr_nm, out_udim_attr_nm):
		data = self.data_dict
		caught_error, msg = catch_error_message(lambda: self._main(uv_attr_nm, out_udim_attr_nm), default='')
		if caught_error is not None:
			if not msg:
				msg = repr(caught_error)
			data['error'] = msg
		return dumps(data)
