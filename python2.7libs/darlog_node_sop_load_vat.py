# encoding: utf-8
"""
Python code for `mobileVAT` rop node.
"""

__author__ = 'Lex Darlog (DRL)'

import hou

import typing as _t

from enum import IntEnum
from json import load
from traceback import format_exception_only

from darlog_hou.errors import any_exception

_T = _t.TypeVar('T')


class PosMode(IntEnum):
	HDR = 0
	LDR = 1
	LDR2 = 2


def catch_error_to_attr(func=None, *_, skip_if_pre_error=False, error_types=None):
	error_types = error_types if error_types else any_exception

	def wrap(old_f):
		def new_f(node: hou.SopNode, geo: hou.Geometry, *args, **kwargs):
			if skip_if_pre_error and geo.attribValue('errorDo'):
				return
			e = None
			try:
				return old_f(node, geo, *args, **kwargs)
			except error_types as _e:
				e = _e
			msg: str = geo.attribValue('error')
			msg = msg.strip()
			err_str = '\n'.join(
				x.strip() for x in format_exception_only(type(e), e)
			)
			msg = err_str if not msg else '{}\n\n{}'.format(msg, err_str)
			geo.setGlobalAttribValue('error', msg)
			geo.setGlobalAttribValue('errorDo', 1)

		try:
			new_f.__name__ = old_f.__name__
		except any_exception:
			pass
		return new_f

	if func is None:
		return wrap
	return wrap(func)


@catch_error_to_attr
def load_json_config_to_detail_attribs(node: hou.SopNode, geo: hou.Geometry, json_file_path: str) -> None:
	with open(json_file_path, 'r') as f:
		data = load(f)
	pos_unpack = data['pos_unpack']
	p_min, p_size = [
		tuple(float(x) for x in p[:3])
		for p in (
			pos_unpack['min'], pos_unpack['size']
		)
	]
	geo.setGlobalAttribValue('p_min', p_min)
	geo.setGlobalAttribValue('p_size', p_size)


@catch_error_to_attr
def verify_images_exist(
	node: hou.SopNode, geo: hou.Geometry,
	pos_mode: PosMode, path_pos_hdr: str, path_pos: str, path_pos2: str, path_rot: str,
	try_read_bytes: int = 4
) -> None:
	@catch_error_to_attr
	def read_single_file_or_error(_node: hou.SopNode, _geo: hou.Geometry, file_path: str):
		with open(file_path, 'rb') as f:
			return f.read(try_read_bytes)

	if not isinstance(pos_mode, PosMode):
		pos_mode = PosMode(pos_mode)

	pos_main_tex = path_pos_hdr if pos_mode == PosMode.HDR else path_pos

	used_files = [pos_main_tex, path_pos2] if pos_mode == PosMode.LDR2 else [pos_main_tex, ]
	used_files.append(path_rot)

	for path in used_files:
		# Do nothing, just try reading the file:
		_ = read_single_file_or_error(node, geo, path)

	geo.setGlobalAttribValue('p_main_tex', pos_main_tex)


@catch_error_to_attr(skip_if_pre_error=True)
def detect_vat_size(
	node: hou.SopNode, geo: hou.Geometry,
	cop_tex: hou.CopNode
):
	n_pieces = int(cop_tex.xRes())
	n_frames = int(cop_tex.yRes())

	for n, what in [
		(n_pieces, 'pieces'),
		(n_frames, 'frames'),
	]:
		if n < 2:
			raise ValueError("Incorrect number of {} in pos-VAT: {} (min: 2)".format(what, n))

	geo.setGlobalAttribValue('n_pieces', n_pieces)
	geo.setGlobalAttribValue('n_frames', n_frames)
