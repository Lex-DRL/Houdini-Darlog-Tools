# encoding: utf-8
"""
Python code for `uvCell` sop node.
"""

__author__ = 'Lex Darlog (DRL)'

import hou

from collections import OrderedDict
from json import dumps

from darlog_hou.attributes import AttribFuncsPerGeo, CommonAttribsValidator, test_name_p_reserved
from darlog_hou.errors import catch_error_message
from darlog_hou.py23 import str_format


_sizes = (2, 3, 4)
_attr_class_int = {
	hou.attribType.Global: 0,
	hou.attribType.Prim: 1,
	hou.attribType.Point: 2,
	hou.attribType.Vertex: 3
}


class InputValidatorParm(CommonAttribsValidator):

	@property
	def data_dict(self):
		try:
			return self.__data_dict
		except AttributeError:
			pass

		# noinspection PyAttributeOutsideInit
		self.__data_dict = data = OrderedDict([
			('is_error', False),
			('error', ''),

			('in_class', 0),
			('out_class', 0),
			('uv_attr', ''),
			('uv_size', 3),

			('cell_u_attr', ''),
			('cell_v_attr', ''),
			('cell_uv_attr', ''),
			('udim_attr', ''),
		])
		return data

	def _main(
		self, uv_attr_nm,  # type: str
		out_class,  # type: int
		cell_u_v_attrs_do,  # type: bool
		cell_u_attr_nm,  # type: str
		cell_v_attr_nm,  # type: str
		cell_uv_attr_do,  # type: bool
		cell_uv_attr_nm,  # type: str
		udim_attr_do,  # type: bool
		udim_attr_nm,  # type: str
	):
		data = self.data_dict

		attr_test_f = AttribFuncsPerGeo(self.geo).attr_test
		uv_attr = attr_test_f(uv_attr_nm, hou.attribData.Float, sizes=_sizes, error_attr_nice_nm='UV')

		data['uv_attr'] = uv_attr_nm = uv_attr.name()
		data['uv_size'] = uv_attr.size()
		data['in_class'] = in_class = _attr_class_int.get(uv_attr.type(), 0)
		data['out_class'] = in_class if out_class < 1 else out_class - 1

		used_attr_names = {uv_attr_nm: 'UV', }

		for do_attr, attr_nm, k, error_nm in [
			(cell_u_v_attrs_do, cell_u_attr_nm, 'cell_u_attr', 'int U-cell'),
			(cell_u_v_attrs_do, cell_v_attr_nm, 'cell_v_attr', 'int V-cell'),
			(cell_uv_attr_do, cell_uv_attr_nm, 'cell_uv_attr', 'str UV-cell'),
			(udim_attr_do, udim_attr_nm, 'udim_attr', 'int UDIM'),
		]:
			if not do_attr:
				continue

			attr_nm = test_name_p_reserved(attr_nm, error_nm, split_by_spaces=True)
			if attr_nm in used_attr_names:
				raise hou.NodeError(str_format(
					"{nm} attribute can't be used as {nice}: it's already used as {used} attribute",
					nm=repr(attr_nm), nice=error_nm, used=used_attr_names[attr_nm]
				))
			used_attr_names[attr_nm] = error_nm
			data[k] = attr_nm

	def json_str(
		self, uv_attr_nm,  # type: str
		out_class,  # type: int
		cell_u_v_attrs_do,  # type: bool
		cell_u_attr_nm,  # type: str
		cell_v_attr_nm,  # type: str
		cell_uv_attr_do,  # type: bool
		cell_uv_attr_nm,  # type: str
		udim_attr_do,  # type: bool
		udim_attr_nm,  # type: str
	):
		res = self.data_dict
		caught_error, msg = catch_error_message(
			lambda: self._main(
				uv_attr_nm, out_class,
				cell_u_v_attrs_do, cell_u_attr_nm, cell_v_attr_nm,
				cell_uv_attr_do, cell_uv_attr_nm,
				udim_attr_do, udim_attr_nm
			),
			default=''
		)
		res['is_error'] = caught_error is not None
		res['error'] = msg
		return dumps(
			res,
			indent=1,
		)
