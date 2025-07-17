# encoding: utf-8
"""
Python code for `mobileVAT` rop node.
"""

__author__ = 'Lex Darlog (DRL)'

import hou

import typing as _t

from dataclasses import dataclass
from enum import IntEnum
from json import load
from typing import NamedTuple

from darlog_hou.attributes_2 import (
	AttributeTypeSpecifier,
	ATTR_CLASS_TO_ID,
	ATTR_ID_TO_CLASS,
	_t_cls,
	find_verify as _find_verify
)
from darlog_hou.attributes_meta import catch_error_to_attr
from darlog_hou.errors import any_exception


_catch_error_to_attr_with_pre_skip = catch_error_to_attr(skip_if_pre_error=True)


class PosMode(IntEnum):
	HDR = 0
	LDR = 1
	LDR2 = 2


@catch_error_to_attr
def load_json_config_to_detail_attribs(node: hou.SopNode, geo: hou.Geometry, json_file_path: str,) -> None:
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
	try_read_bytes: int = 4,
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


@_catch_error_to_attr_with_pre_skip
def detect_vat_size(
	node: hou.SopNode, geo: hou.Geometry,
	cop_tex: hou.CopNode,
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


class MetaAttribNames(NamedTuple):
	"""
	An utility class, containing the names of attribs in META branch,
	related to error-checks for actual attribs in input SOP.
	"""
	piece: str = 'attr_piece'
	piece_cls: str = 'attr_piece_cls'
	pivot: str = 'attr_pivot'
	pivot_cls: str = 'attr_pivot_cls'
	ren0_src: str = 'ren0_src'
	ren0_tmp: str = 'ren0_tmp'
	ren1_src: str = 'ren1_src'
	ren1_trg: str = 'ren1_trg'


_default_meta_attrib_names = MetaAttribNames()


class InternalAttribNames(NamedTuple):
	piece: str = 'piece'
	pivot: str = 'pivot'


_default_internal_attrib_names = InternalAttribNames()

_attr_cls_priority: _t.Tuple[_t_cls, ...] = (hou.attribType.Point, hou.attribType.Prim, hou.attribType.Global)
# ATTR_CLASS_TO_ID already has promote-node IDs, so the resulting ints are menu values:
_attr_cls_to_int: _t.Dict[_t_cls, int] = {c: i for c, i in ATTR_CLASS_TO_ID.items() if c in _attr_cls_priority}


_piece_specifier = AttributeTypeSpecifier.from_unsafe_args(_attr_cls_priority, hou.attribData.Int, 1, is_array=False)
_pivot_specifier = AttributeTypeSpecifier.from_unsafe_args(_attr_cls_priority, hou.attribData.Float, 3, is_array=False)


@dataclass
class InputGeoValidator:
	"""
	Functions related to input-geo-check, logically grouped under this container.

	Each function has a number suffix indicating in which order they need to be called.
	"""

	node: hou.SopNode
	geo: hou.Geometry
	asset: hou.SopNode
	in_geo: hou.Geometry

	meta_attrib_names: MetaAttribNames = _default_meta_attrib_names
	internal_attrib_names: InternalAttribNames = _default_internal_attrib_names

	@staticmethod
	@catch_error_to_attr
	def __verify_attr_f(
		node: hou.SopNode, geo: hou.Geometry,  # META branch, required for `@catch_error_to_attr`
		asset: hou.SopNode, in_geo: hou.Geometry,  # actual input SOPs
		name: str, specifier: AttributeTypeSpecifier, meta_attr_name: str, meta_attr_class: str, error_multi: bool = False,
	):
		attr = _find_verify(
			name=name, specifier=specifier, node=asset, geo=in_geo, geo_from_input=1,
			error_multi=error_multi, node_in_error=False
		)
		geo.setGlobalAttribValue(meta_attr_name, attr.name())
		geo.setGlobalAttribValue(meta_attr_class, _attr_cls_to_int.get(attr.type(), -1))

	def _verify_attr(
		self,
		name: str, specifier: AttributeTypeSpecifier, meta_attr_name: str, meta_attr_class: str, error_multi: bool = False,
	):
		return self.__verify_attr_f(
			self.node, self.geo, self.asset, self.in_geo,
			name, specifier, meta_attr_name, meta_attr_class, error_multi
		)

	def verify_piece_attr_0(self, name: str,):
		meta_nm = self.meta_attrib_names
		return self._verify_attr(name, _piece_specifier, meta_nm.piece, meta_nm.piece_cls)

	def verify_pivot_attr_0(self, name: str,):
		meta_nm = self.meta_attrib_names
		return self._verify_attr(name, _pivot_specifier, meta_nm.pivot, meta_nm.pivot_cls)

	@staticmethod
	@_catch_error_to_attr_with_pre_skip
	def __detect_renames(
		node: hou.SopNode, geo: hou.Geometry,  # META branch, required for `@catch_error_to_attr`
		asset: hou.SopNode, in_geo: hou.Geometry,  # actual input SOPs
		meta_nm: MetaAttribNames, internal_nm: InternalAttribNames
	):
		"""
		Internally, required attributes are (in this specific order):
		1. Promoted to Point type (if not)
		2. Renamed to hard-coded internal names.

		... therefore, as step 0, we need to free up those internal names if present -
		by temporarily renaming existing attributes, then doing the node's job,
		then performing all 3 steps in reverse order.

		No extra meta-attribs are needed for promotions themselves. Attr-class attribs already contain proper IDs.
		"""
		piece_class = ATTR_ID_TO_CLASS.get(geo.intAttribValue(meta_nm.piece_cls), None)
		pivot_class = ATTR_ID_TO_CLASS.get(geo.intAttribValue(meta_nm.pivot_cls), None)
		assert (
			piece_class in _attr_cls_to_int and pivot_class in _attr_cls_to_int
		), "Internal error: invalid attribute classes for piece/pivot:\n{}\n{}".format(repr(piece_class), repr(pivot_class))
		piece_nm: str = geo.stringAttribValue(meta_nm.piece)
		pivot_nm: str = geo.stringAttribValue(meta_nm.pivot)
		assert (
			piece_nm and isinstance(piece_nm, str) and
			pivot_nm and isinstance(pivot_nm, str)
		), "Internal error: invalid attribute names for piece/pivot:\n{}\n{}".format(repr(piece_nm), repr(pivot_nm))
		assert isinstance(geo, hou.Geometry), "Internal error: not a valid geo in META: {}".format(repr(geo))

		existing_point_attr_names: _t.Set[str] = set(x.name() for x in in_geo.pointAttribs())
		pre_renames_src: _t.List[str] = list()
		pre_renames_tmp: _t.List[str] = list()

		def pre_free_up_point_attr_name(attr_nm: str):
			do_rename = False
			new_name: str = attr_nm
			while new_name in existing_point_attr_names:
				new_name = '_{}'.format(new_name)  # prefix with '_'
				do_rename = True
			if do_rename:
				pre_renames_src.append(attr_nm)
				pre_renames_tmp.append(new_name)

		def schedule_pre_renames_for_single_attr(
			attr_cls: _t_cls, attr_nm_src: str, attr_nm_internal: str
		):
			is_promoted = attr_cls != hou.attribType.Point
			if is_promoted:
				# Source attrib will be promoted. We need to free up it's source name, too:
				pre_free_up_point_attr_name(attr_nm_src)
				# ... and since we've freed the name, remove it from the set:
				if attr_nm_src in existing_point_attr_names:
					existing_point_attr_names.remove(attr_nm_src)
			if is_promoted or attr_nm_src != attr_nm_internal:
				# We might need to free up internal name unless the attr already has it and already is point:
				pre_free_up_point_attr_name(attr_nm_internal)
				# similarly, remove it from the set:
				if attr_nm_internal in existing_point_attr_names:
					existing_point_attr_names.remove(attr_nm_internal)

		schedule_pre_renames_for_single_attr(piece_class, piece_nm, internal_nm.piece)
		schedule_pre_renames_for_single_attr(pivot_class, pivot_nm, internal_nm.pivot)

		# After pre-rename, point-attrib-names-set will be extended with temporary names, too:
		existing_point_attr_names.update(pre_renames_tmp)

		# However, during this pre-check, we've might already pre-renamed our main attribs,
		# if they already were of point class, but was taking other attribs' names.
		# If so, we need to detect their new names (after pre-rename):
		def find_pre_renamed_clashing_source_name(attr_cls: _t_cls, attr_nm_src: str):
			if attr_cls != hou.attribType.Point:
				return attr_nm_src
			start = 0
			attr_nm_src = attr_nm_src
			while True:  # just in case source attr might've been renamed multiple times in sequence
				try:
					index = pre_renames_src.index(attr_nm_src, start)
				except any_exception:
					return attr_nm_src
				attr_nm_src = pre_renames_tmp[index]
				start = index

		piece_nm = find_pre_renamed_clashing_source_name(piece_class, piece_nm)
		pivot_nm = find_pre_renamed_clashing_source_name(pivot_class, pivot_nm)

		promoted_renames_src: _t.List[str] = list()
		promoted_renames_internal: _t.List[str] = list()

		# First, we need to ensure source names don't clash with other attrib's internal names,
		# and if so - post-rename them to "buffers":

		def rename_to_buffer(src_nm: str, *other_internal_names: str):
			other_internal_names = set(other_internal_names)
			src_nm = src_nm
			while src_nm in other_internal_names:
				new_name: str = '_{}'.format(src_nm)
				while new_name in existing_point_attr_names:
					new_name = '_{}'.format(new_name)
				promoted_renames_src.append(src_nm)
				promoted_renames_internal.append(new_name)
				existing_point_attr_names.add(new_name)
				if src_nm in existing_point_attr_names:
					existing_point_attr_names.remove(src_nm)
				src_nm = new_name
			return src_nm

		piece_nm = rename_to_buffer(piece_nm, *[x for x in internal_nm if x != internal_nm.piece])
		pivot_nm = rename_to_buffer(pivot_nm, *[x for x in internal_nm if x != internal_nm.pivot])

		# Source attribs are promoted, their internal names are freed, and they're ready do be finally renamed.
		for src_nm, desired_nm in [
			(piece_nm, internal_nm.piece),
			(pivot_nm, internal_nm.pivot),
		]:
			if src_nm == desired_nm:
				continue
			promoted_renames_src.append(src_nm)
			promoted_renames_internal.append(desired_nm)

		# Finally, what's left is assigning these values to meta geo:
		geo.setGlobalAttribValue(meta_nm.ren0_src, pre_renames_src)
		geo.setGlobalAttribValue(meta_nm.ren0_tmp, pre_renames_tmp)
		geo.setGlobalAttribValue(meta_nm.ren1_src, promoted_renames_src)
		geo.setGlobalAttribValue(meta_nm.ren1_trg, promoted_renames_internal)

	def detect_internal_renames_1(self, ):
		return self.__detect_renames(
			self.node, self.geo, self.asset, self.in_geo, self.meta_attrib_names, self.internal_attrib_names
		)
