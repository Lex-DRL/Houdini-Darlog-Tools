# encoding: utf-8
"""
Python code for `uvOverlapSeams` sop node.
"""

__author__ = 'Lex Darlog (DRL)'

from darlog_hou.attributes import CommonAttribsValidator, test_name_no_reserved
from darlog_hou.errors import catch_error_message


class InputValidatorParm(CommonAttribsValidator):

	def _main(self, uv_attr, out_gr):  # type: (str, str) -> ...
		self.test_uv(uv_attr, allow_pt=False)
		test_name_no_reserved(out_gr, 'out', entity_type='group')

	def error_str(self, uv_attr, out_gr):  # type: (str, str) -> str
		caught_error, msg = catch_error_message(lambda: self._main(uv_attr, out_gr), default='')
		if caught_error is None:
			return ''
		return msg if msg else repr(caught_error)
