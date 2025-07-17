# encoding: utf-8
"""
Python code for `shadowBorder` sop node.
"""

__author__ = 'Lex Darlog (DRL)'

import typing as _t
from typing import NamedTuple

from itertools import chain

import hou

from darlog_hou.errors import any_exception
from darlog_hou.processing_2d.convolution import ConvolutionWindowSquare


class ConvPixel(NamedTuple):
	u: int
	v: int
	weight: float
	uv_dir: hou.Vector2

	@classmethod
	def pixels_from_radius(cls, pixel_radius: int) -> _t.Tuple['ConvPixel', ...]:
		window = ConvolutionWindowSquare(radius=pixel_radius, include_center=False)
		pixels = tuple(
			ConvPixel(uv_id[0], uv_id[1], weight, hou.Vector2(uv_dir))
			for uv_id, uv_dir, weight in zip(window.uv_ids, window.uv_dirs_normalized, window.weights_square_mask)
		)
		# First, filter out any pixels with zero and below weight:
		pixels = tuple(px for px in pixels if px.weight > 0.0)
		# Next, sort them from core and outwards:
		pixels = tuple(sorted(pixels, key=cls.sorting_key))
		return pixels

	@staticmethod
	def sorting_key(pixel: 'ConvPixel'):
		u = pixel.u
		v = pixel.v
		return u*u + v*v, v, u


_cached_conv_pixels: _t.Dict[int, _t.Tuple[ConvPixel, ...]] = {
	x: ConvPixel.pixels_from_radius(x)
	for x in [1, 2, 3]
}


def set_convolution_window_attribs(geo: hou.Geometry, pixel_radius: int):
	assert isinstance(geo, hou.Geometry)
	radius = int(max(pixel_radius, 1))

	pixels = (
		_cached_conv_pixels[radius]
		if radius in _cached_conv_pixels
		else ConvPixel.pixels_from_radius(radius)
	)
	u_ids, v_ids, weights, uv_dirs = zip(*pixels)

	# Non-array attribs:
	for attr_nm, value in [
		('conv_radius', radius),
		('conv_px_n', len(pixels)),
	]:
		try:
			geo.addAttrib(hou.attribType.Global, attr_nm, type(value)(), create_local_variable=False)
		except any_exception:
			geo.addAttrib(hou.attribType.Global, attr_nm, type(value)())
		geo.setGlobalAttribValue(attr_nm, value)

	# Array attribs:
	for attr_nm, dt, value, vector_size in [
		('conv_idU', hou.attribData.Int, u_ids, 1),
		('conv_idV', hou.attribData.Int, v_ids, 1),
		('conv_weight', hou.attribData.Float, weights, 1),
		('conv_dirUV', hou.attribData.Float, uv_dirs, 2),
	]:
		geo.addArrayAttrib(hou.attribType.Global, attr_nm, dt, vector_size)
		if vector_size > 1:
			value = tuple(chain(*value))
		geo.setGlobalAttribValue(attr_nm, list(value))
