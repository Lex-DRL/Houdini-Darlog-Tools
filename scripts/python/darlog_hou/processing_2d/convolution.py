# encoding: utf-8
"""
Utility functions for 2D-convolution.
"""

__author__ = 'Lex Darlog (DRL)'


from dataclasses import dataclass
from math import sqrt

import typing as _t

# noinspection PyTypeHints
_T = _t.TypeVar('T')


def _dummy_f(x: _T) -> _T:
	return x


def _modify_length_for_excluded_center(length: float) -> float:
	"""Subtract 1 from the length, to give the 4 closest pixels weight of exactly 1.0"""
	return max(0.0, length - 1.0)


def _uv_length(u_id: int, v_id: int) -> float:
	return sqrt(float(u_id * u_id + v_id * v_id))


@dataclass
class ConvolutionWindowSquare:
	radius: int = 1
	include_center: bool = True

	_cache_uv_ids: _t.Tuple[_t.Tuple[int, int], ...] = None
	_cache_uv_dirs_normalized: _t.Tuple[_t.Tuple[float, float], ...] = None
	_cache_weights_square_mask: _t.Tuple[float, ...] = None

	def __post_init__(self):
		self.radius = int(max(self.radius, 1))

	def __uv_ids_gen(self):
		"""Generator, producing U/V id-offsets for the whole convolution window."""
		first_id = -self.radius
		stop_id = self.radius + 1
		iter_u: _t.Iterable[int] = range(first_id, stop_id)
		iter_v: _t.Iterable[int] = range(first_id, stop_id)
		if self.include_center:
			# Unconditionally, iterate over all U's and V's:
			for v_id in iter_v:
				for u_id in iter_u:
					yield u_id, v_id
			return

		# Otherwise, we need to exclude the "core" pixel, with both IDs as zeroes:
		for v_id in iter_v:
			v_is_zero = (v_id == 0)
			for u_id in iter_u:
				if v_is_zero and u_id == 0:
					continue
				yield u_id, v_id

	def _build_uv_ids(self):
		self._cache_uv_ids = tuple(self.__uv_ids_gen())

	@property
	def uv_ids(self) -> _t.Tuple[_t.Tuple[int, int], ...]:
		"""Per-pixel id-offsets in U/V for the whole convolution window."""
		if self._cache_uv_ids is None:
			self._build_uv_ids()
		return self._cache_uv_ids

	@staticmethod
	def _pixel_weight_square_mask(
		u_id, v_id, length_normalization_scale, length_pre_normalization_f
	):  # type: (int, int, float, _t.Callable[[float], float]) -> float
		"""Generate pixel weight (via quadratic-square mask) for a specific pixel."""
		length = _uv_length(u_id, v_id)
		length = length_pre_normalization_f(length)
		length_norm = float(length) * length_normalization_scale
		return 1.0 - length_norm * length_norm  # squared + inverse; might get negative at corners

	def _build_weights_square_mask(self):
		# Whether center is included or not, we can't make normalization by just dividing the length with radius.
		# If we did, the orthogonal "cross" pixels right at the border would always get exactly zero weight,
		# and since they have the highest weight in their corresponding rows/columns, the entire border would be discarded.
		# So, we need to "expand" radius an extra pixel above those pixel's distance.
		# It technically makes radius go "outside" the window, but all those "virtual" extra pixels around the window
		# would be discarded exactly the same way, so at the end we get the window of desired size,
		# with non-zero values at the left/right/top/bottom-most pixels.
		if self.include_center:
			# If center itself is included, then _IT_ needs to have max weight of 1.0 - so keep 0 length at zero,
			# but stretch the radius one pixel outwards:
			length_pre_normalization_f = _dummy_f
			length_normalization_scale = float(1.0 / (self.radius + 1))
		else:
			# If the center-most pixel is excluded, then the minimum raw length is 1.
			# So, we subtract 1 from length... which forces us to subtract it from radius, too.
			# And then, same as above, we expand it by 1.
			# In the end, radius stays the same:
			length_pre_normalization_f = _modify_length_for_excluded_center
			length_normalization_scale = float(1.0 / self.radius)
		self._cache_weights_square_mask = tuple(
			self._pixel_weight_square_mask(u_id, v_id, length_normalization_scale, length_pre_normalization_f)
			for u_id, v_id in self.uv_ids
		)

	@property
	def weights_square_mask(self) -> _t.Tuple[float, ...]:
		"""
		Per-pixel weights, assuming quadratic decay from center.

		* If center-most pixel is included, only it has exactly 1.0.
		* If excluded, the 4 surrounding ones have 1.0.
		"""
		if self._cache_weights_square_mask is None:
			self._build_weights_square_mask()
		return self._cache_weights_square_mask

	@staticmethod
	def _uv_dir_normalized(u_id: int, v_id: int) -> _t.Tuple[float, float]:
		if u_id == 0 and v_id == 0:
			return 0.0, 0.0
		scale = 1.0 / _uv_length(u_id, v_id)
		return float(u_id) * scale, float(v_id) * scale

	def _build_uv_dirs_normalized(self):
		self._cache_uv_dirs_normalized = tuple(
			self._uv_dir_normalized(u_id, v_id)
			for u_id, v_id in self.uv_ids
		)

	@property
	def uv_dirs_normalized(self) -> _t.Tuple[_t.Tuple[float, float], ...]:
		"""
		Normalized 2D directions (from window center) for each pixel.

		If the center itself is included, it has 0.0.
		"""
		if self._cache_uv_dirs_normalized is None:
			self._build_uv_dirs_normalized()
		return self._cache_uv_dirs_normalized

	def cache_all(self):
		"""
		All the property values are cached internally on the first call.
		This method explicitly and forcefully (pre- or re-)caches them all.
		"""
		self._build_uv_ids()
		self._build_uv_dirs_normalized()
		self._build_weights_square_mask()
		return self
