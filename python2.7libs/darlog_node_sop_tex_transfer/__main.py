# encoding: utf-8

import hou
from collections import OrderedDict
from json import dumps

from darlog_hou.attributes import (
	test_name_p_reserved,
	test_name_no_reserved,
	AttribFuncsPerGeo,
	_attr_types_default_sort_map
)
from darlog_hou.errors import catch_error_message

import typing as _t

_O = _t.Optional
_U = _t.Union


_channels_keys = (
	'color',
	'alpha',
	'colorAlpha',
	'em',
	'metal',
	'smooth',
	'metalSmooth',
	'ao',
	'pbr',
	'nm',
)


def channel_labels():
	return {
		'color': 'Base Color',
		'alpha': 'Base Alpha',
		'colorAlpha': 'Base Color+Alpha',
		'em': 'Emission',
		'metal': 'Metallic',
		'smooth': 'Smoothness',
		'metalSmooth': 'Metal+Smooth',
		'ao': 'AO',
		'pbr': 'PBR',
		'nm': 'Normal Map',
	}


def channels_dict(val):
	return OrderedDict((k, val) for k in _channels_keys)


_mask_channels_keys = (
	'comb', '1', '2', '3', '4'
)


def mask_channels_dict(val):
	return OrderedDict((k, val) for k in _mask_channels_keys)


def mask_dict():
	return OrderedDict([
		('key', ''),
		('label', ''),
		('in_mode', 0),
		('out_mode', 0),
		('srcCh', mask_channels_dict('')),
		('trgCh', mask_channels_dict('')),
	])


_mask_channel_labels = {
	'comb': 'combined {}',
	'1': '{}-1',
	'2': '{}-2',
	'3': '{}-3',
	'4': '{}-4'
}


def mask_label(main_label, channel_key):
	f_string = _mask_channel_labels.get(channel_key, '<unknown> {} channel')
	return f_string.format(main_label)


# To avoid extra dependencies, we can't use `@attr.s` here, so let's build an output data as OrderedDict:
def out_dict_init():
	return OrderedDict([
		('srcUVs', ''),
		('srcUVs_isVtx', False),
		('trgUVs', ''),
		('trgUVs_isVtx', False),

		('srcCh', channels_dict('')),
		('trgCh', channels_dict('')),

		('baseColor', OrderedDict([
			('in_mode', 0), ('out_mode', 0),
		])),

		('pbr', OrderedDict([
			('in_mode', 0), ('out_mode', 0), ('invertSmooth', False),
		])),

		('nm', OrderedDict([
			('srcN', ''),
			('srcN_mode', 0),
			('trgN', ''),
			('trgN_mode', 0),

			('srcTg', ''),
			('srcTg_mode', 0),
			('trgTg', ''),
			('trgTg_mode', 0),
			('srcBiTg', ''),
			('srcBiTg_mode', 0),
			('trgBiTg', ''),
			('trgBiTg_mode', 0),
		])),

		('masks', tuple()),

		# use UDIMs / pre-provided attrib name / attrib type:
		('srcUDIMs', OrderedDict([
			('do', False), ('attr', ''), ('type', 0)
		])),
		('trgUDIMs', OrderedDict([
			('do', False), ('attr', ''), ('type', 0)
		])),

		('inAttribs', OrderedDict([
			(k, '') for k in (
				'srcUVs', 'trgUVs',
				'srcUVW',
				'srcUDIMs', 'trgUDIMs',
				'srcN', 'trgN',
				'srcTg', 'trgTg',
				'srcBiTg', 'trgBiTg',
			)
		])),

		('error', ''),
	])


_cleaned_up_out_dict_values = {0, ''}


def _is_cleaned_up_val(val):
	return val in _cleaned_up_out_dict_values and val is not False


def _cleanup_out_dict(out_data, del_root_keys=True):  # type: (dict, bool) -> ...
	assert isinstance(out_data, dict)
	orig_keys = list(out_data.keys())

	for key in orig_keys:
		val = out_data[key]
		if isinstance(val, (dict, list, tuple, set)):
			out_data[key] = val = cleanup_out_data(val, True)
			if del_root_keys and not val:
				out_data.pop(key)
			continue
		if del_root_keys and _is_cleaned_up_val(val):
			out_data.pop(key)

	return out_data


def _cleanup_out_iterable(out_data, del_root_keys=True):  # type: (_t.Iterable, bool) -> _t.Iterable
	assert isinstance(out_data, (list, tuple, set))
	iter_type = type(out_data)

	def gen():
		for val in out_data:
			if isinstance(val, (dict, list, tuple, set)):
				val = cleanup_out_data(val, True)
				if val or not del_root_keys:
					yield val
				continue
			if del_root_keys and _is_cleaned_up_val(val):
				continue
			yield val

	return iter_type(gen())


def cleanup_out_data(out_data, del_root_keys=True):  # type: (_t.Iterable, bool) -> ...
	assert isinstance(out_data, (dict, list, tuple, set))
	if isinstance(out_data, dict):
		return _cleanup_out_dict(out_data, del_root_keys)
	return _cleanup_out_iterable(out_data, del_root_keys)


ChannelParams = _t.NamedTuple('ChannelParams', [('key', str), ('src', str), ('trg', str)])


class ChannelsPerModeBlock:
	"""Populates src/trg channels for a single channel-block which might be in multiple modes."""
	def __init__(
		self,
		in_mode,  # type: int
		out_mode,  # type: int
		out_modes_dict,  # type: _t.Dict[str, _t.Any]
		channels_per_mode,  # type: _t.Sequence[_t.Set[str]]
		param_names,  # type: _t.Iterable[ChannelParams]
	):
		self.in_mode = max(in_mode, 0)
		self.out_mode = max(out_mode, 0)
		self.channels_per_mode = channels_per_mode
		self.out_modes_dict = out_modes_dict
		self.param_names = param_names

	def get_channels_per_mode(self, mode): # type: (int) -> _t.Set[str]
		try:
			return self.channels_per_mode[mode]
		except IndexError:
			return set()

	def main(
		self,
		channel_labels_dict,    # type: _t.Dict[str, str]
		main_data_dict,  # type: dict
		src_ch_dict=None,  # type: _t.Dict[str, str]
		trg_ch_dict=None,  # type: _t.Dict[str, str]
	):
		in_mode, out_mode = self.in_mode, self.out_mode
		self.out_modes_dict['in_mode'] = in_mode
		if in_mode < 1:
			return
		if out_mode < 1:
			self.out_mode = out_mode = in_mode
		self.out_modes_dict['out_mode'] = out_mode

		if not isinstance(src_ch_dict, dict):
			src_ch_dict = main_data_dict['srcCh']
		if not isinstance(trg_ch_dict, dict):
			trg_ch_dict = main_data_dict['trgCh']

		src_required_ch = self.get_channels_per_mode(in_mode)
		trg_required_ch = self.get_channels_per_mode(out_mode)
		for key, src_parm, trg_parm in self.param_names:
			if not (key in src_required_ch or key in trg_required_ch):
				continue

			nice_nm = channel_labels_dict.get(key, key)
			src_nm = test_name_no_reserved(
				hou.evalParm(src_parm), 'source {}'.format(nice_nm), entity_type='channel', split_by_spaces=True
			)
			src_ch_dict[key] = '' if key not in src_required_ch else src_nm
			trg_ch_dict[key] = '' if key not in trg_required_ch else test_name_no_reserved(
				hou.evalParm(trg_parm), 'target {}'.format(nice_nm), entity_type='channel', split_by_spaces=True,
				default_name=src_nm, default_name_always_ok=True
			)


class InputProcessor:
	def __init__(
		self,
		geo  # type: hou.Geometry
	):
		if not isinstance(geo, hou.Geometry):
			raise hou.NodeError("Not a geometry: {}".format(geo))
		self.geo = geo

		self.attr_test_all_types = AttribFuncsPerGeo(geo).attr_test
		self.attr_test_uv = AttribFuncsPerGeo(geo, (hou.attribType.Vertex, hou.attribType.Point)).attr_test

		self.channel_labels = channel_labels()
		self.data_dict = out_dict_init()

	def __repr__(self):
		return '{}({})'.format(self.__class__.__name__, self.geo)

	def _main_uvs(self):
		data_dict = self.data_dict
		for key, attr_name, nice_nm in [
			('srcUVs', hou.evalParm("../srcUV_attr"), 'source-UV'),
			('trgUVs', hou.evalParm("../trgUV_attr"), 'target-UV'),
		]:
			attr = self.attr_test_uv(attr_name, hou.attribData.Float, sizes=3, error_attr_nice_nm=nice_nm)
			data_dict[key] = attr.name()
			data_dict['{}_isVtx'.format(key)] = bool(attr.type() == hou.attribType.Vertex)
		if data_dict['srcUVs'] == data_dict['trgUVs']:
			raise hou.NodeError("UV attribute {a_nm} can't be both source and target UV-set".format(
				a_nm=repr(data_dict['srcUVs'])
			))

	def _main_udims(self):
		data_dict = self.data_dict
		for udim_do, name, nice_nm, data_key in [
			(hou.evalParm("../srcUDIMs_do"), hou.evalParm("../srcUDIMs_attr"), 'source-UDIMs', 'srcUDIMs'),
			(hou.evalParm("../trgUDIMs_do"), hou.evalParm("../trgUDIMs_attr"), 'target-UDIMs', 'trgUDIMs'),
		]:
			udim_do = bool(udim_do)
			data_dict[data_key]['do'] = udim_do
			name = test_name_p_reserved(name, nice_nm, default_name='', default_name_always_ok=True, split_by_spaces=True)
			if not (udim_do and name):
				continue
			assert bool(name) and udim_do

			attr = self.attr_test_all_types(name, hou.attribData.Int, sizes=1, ok_not_found=True, error_attr_nice_nm=nice_nm)
			if attr is None:
				continue
			assert isinstance(attr, hou.Attrib)

			data_dict[data_key]['attr'] = attr.name()
			data_dict[data_key]['type'] = _attr_types_default_sort_map.get(attr.type(), 0)

	def _main_mask_channels(self):
		masks_list = list()  # type: _t.List[dict]
		mask_literals = ['A', 'B', 'C', 'D']
		# mask_literals = ['A', ]

		for i, nm in enumerate(mask_literals, 1):
			out_dict = mask_dict()
			out_dict['key'] = 'mask{}'.format(i)
			out_dict['label'] = 'Mask-{}'.format(nm)
			ChannelsPerModeBlock(
				hou.evalParm("../mask{}_mode".format(i)),
				hou.evalParm("../mask{}_convert_mode".format(i)),
				out_modes_dict=out_dict,
				channels_per_mode=(
					set(),  # 0
					{'1', '2', '3', '4'},  # 1: sepFiles
					{'comb', },  # 2: combRGB
					{'comb', },  # 3: combRGBA
				),
				param_names=(
					ChannelParams('comb', "../mask{}_comb_src".format(i), "../mask{}_comb_trg".format(i)),
					ChannelParams('1', "../mask{}_1_src".format(i), "../mask{}_1_trg".format(i)),
					ChannelParams('2', "../mask{}_2_src".format(i), "../mask{}_2_trg".format(i)),
					ChannelParams('3', "../mask{}_3_src".format(i), "../mask{}_3_trg".format(i)),
					ChannelParams('4', "../mask{}_4_src".format(i), "../mask{}_4_trg".format(i)),
				)
			).main(self.channel_labels, self.data_dict, src_ch_dict=out_dict['srcCh'], trg_ch_dict=out_dict['trgCh'])
			if out_dict['out_mode'] > 0:
				masks_list.append(out_dict)

		self.data_dict['masks'] = tuple(masks_list)

	def _main_pbr_channels(self):
		data_dict_modes = self.data_dict['pbr']
		ChannelsPerModeBlock(
			hou.evalParm("../pbr_mode"),
			hou.evalParm("../pbr_convert_mode"),
			out_modes_dict=data_dict_modes,
			channels_per_mode=(
				set(),  # 0
				{'metal', 'smooth', 'ao'},  # 1
				{'metalSmooth', 'ao'},  # 2
				{'pbr', },  # 3
			),
			param_names=(
				ChannelParams('metal', "../metal_src", "../metal_trg"),
				ChannelParams('smooth', "../smooth_src", "../smooth_trg"),
				ChannelParams('ao', "../ao_src", "../ao_trg"),
				ChannelParams('metalSmooth', "../metalSmooth_src", "../metalSmooth_trg"),
				ChannelParams('pbr', "../pbr_src", "../pbr_trg"),
			)
		).main(self.channel_labels, self.data_dict)
		data_dict_modes['invertSmooth'] = bool(hou.evalParm("../smoothTex_invert"))

	def _main_base_color_channels(self):
		ChannelsPerModeBlock(
			hou.evalParm("../base_mode"),
			hou.evalParm("../base_convert_mode"),
			out_modes_dict=self.data_dict['baseColor'],
			channels_per_mode=(
				set(),  # 0
				{'color', },  # 1
				{'alpha', },  # 2
				{'color', 'alpha'},  # 3
				{'colorAlpha'},  # 4
			),
			param_names=(
				ChannelParams('color', "../baseColor_src", "../baseColor_trg"),
				ChannelParams('alpha', "../baseAlpha_src", "../baseAlpha_trg"),
				ChannelParams('colorAlpha', "../baseColorAlpha_src", "../baseColorAlpha_trg"),
			)
		).main(self.channel_labels, self.data_dict)

	def _main_on_off_channels(self):
		for key, do_parm, src_parm, trg_parm in [
			('em', "../emission_do", "../emission_src", "../emission_trg",),
			('nm', "../nm_do", "../nm_src", "../nm_trg",),
		]:
			chan_do = hou.evalParm(do_parm)  # type: int
			if not chan_do:
				continue

			nice_nm = self.channel_labels.get(key, key)
			src_name = test_name_no_reserved(
				hou.evalParm(src_parm), 'source {}'.format(nice_nm), entity_type='channel', split_by_spaces=True
			)
			trg_name = test_name_no_reserved(
				hou.evalParm(trg_parm), 'target {}'.format(nice_nm), entity_type='channel', split_by_spaces=True,
				default_name=src_name, default_name_always_ok=True
			)
			self.data_dict['srcCh'][key] = src_name
			self.data_dict['trgCh'][key] = trg_name

	def _main_ensure_out_channel_names_unique(self):
		data_dict = self.data_dict
		assert 'trgCh' in data_dict and isinstance(data_dict['trgCh'], dict)
		all_trg_ch = OrderedDict(data_dict['trgCh'])

		# To ACTUALLY check all the channels, we need to add all the mask-channels to the rest of them
		for mask_data in data_dict['masks']:
			assert isinstance(mask_data, dict)
			assert 'key' in mask_data and isinstance(mask_data['key'], str)
			main_key = mask_data['key']  # type: str
			assert 'label' in mask_data and isinstance(mask_data['label'], str)
			main_label = mask_data['label']  # type: str
			assert 'trgCh' in mask_data and isinstance(mask_data['trgCh'], dict)
			for ch_key, ch_val in mask_data['trgCh'].items():
				full_ch_key = '{}_{}'.format(main_key, ch_key)
				self.channel_labels[full_ch_key] = mask_label(main_label, ch_key)
				all_trg_ch[full_ch_key] = ch_val

		seen = dict()
		for key, ch in all_trg_ch.items():
			assert isinstance(key, str) and isinstance(ch, str)
			if not ch:
				continue
			ch_label = self.channel_labels.get(key, key)
			if ch in seen:
				raise hou.NodeError("{ch} channel can't be used for multiple outputs: {o1}, {o2}".format(
					ch=repr(ch), o1=seen[ch], o2=ch_label
				))
			seen[ch] = ch_label

	def _main_nm_attribs(self):
		data_dict = self.data_dict
		if not data_dict['trgCh']['nm']:
			return

		out_dict = data_dict['nm']  # type: dict

		for required, key, nice_nm in [
			# Normal attribute is required anyway:
			(True, 'srcN', "source Normal"),
			(True, 'trgN', "target Normal"),

			# Tangent attributes might be absent, we'll just re-calculate them:
			(False, 'srcTg', 'source Tangent'),
			(False, 'trgTg', 'target Tangent'),
			(False, 'srcBiTg', 'source biTangent'),
			(False, 'trgBiTg', 'source biTangent'),
		]:
			attr = self.attr_test_all_types(
				hou.evalParm("../{}_attr".format(key)),
				hou.attribData.Float, sizes=3, ok_not_found=not required, error_attr_nice_nm=nice_nm,
			)
			if attr is None:
				continue
			out_dict[key] = attr.name()
			out_dict['{}_mode'.format(key)] = _attr_types_default_sort_map.get(attr.type(), 0)

		# Now we should check that in each tangentBasis at least each vector isn't used twice:
		vector_labels = ('Normal', 'Tangent', 'biTangent')
		uv_attrib_names = {data_dict['srcUVs'], data_dict['trgUVs']}
		for src_trg, ts_vector_names in [
			('source', (out_dict['srcN'], out_dict['srcTg'], out_dict['srcBiTg'])),
			('target', (out_dict['trgN'], out_dict['trgTg'], out_dict['trgBiTg'])),
		]:
			# Ensure none of the vectors uses any of UV attribs:
			for a_nm, a_label in zip(ts_vector_names, vector_labels):
				if a_nm and a_nm in uv_attrib_names:
					raise hou.NodeError("Can't use UV attribute {a_nm} as {{{src_trg} {v_nm}}}".format(
						a_nm=repr(a_nm), src_trg=src_trg, v_nm=a_label
					))

			# Compare each pair:
			for a_i, b_i in [
				(0, 1),
				(1, 2),
				(0, 2)
			]:
				a_nm, b_nm = ts_vector_names[a_i], ts_vector_names[b_i]
				if a_nm and a_nm and a_nm == b_nm:
					raise hou.NodeError(
						"Can't use the same attribute {a_nm} for {src_trg} {{{a}}} and {{{b}}}: "
						"they form a Tangent-basis and therefore must be perpendicular vectors".format(
							a_nm=repr(a_nm), src_trg=src_trg, a=vector_labels[a_i], b=vector_labels[b_i]
						)
					)

	def _main_internal_attribs(self):
		"""Must be called AFTER all the attrib names are already checked/set."""
		data_dict = self.data_dict
		out_dict = data_dict['inAttribs']  # type: _t.Dict[str, str]
		already_passed_attribs = set()
		already_passed_add = already_passed_attribs.add
		auto_generated_keys = list()
		auto_generated_add = auto_generated_keys.append

		def classify_attrib_name(key, attr_name):
			if not attr_name:
				# Don't pass an auto-attrib right away, but schedule it for later,
				# after all the user-specified attribs would already take their names:
				assert key not in auto_generated_keys
				auto_generated_add(key)
				return
			# User have provided name. Set it right away.
			# Even if name clashes with smth else, it's a user intention
			# (previous check would already have thrown an error if it's forbiden).
			out_dict[key] = attr_name
			already_passed_add(attr_name)

		for key in [
			'srcUVs', 'trgUVs'
		]:
			classify_attrib_name(key, data_dict[key])

		classify_attrib_name('srcUVW', '')

		for key in [
			'srcUDIMs', 'trgUDIMs'
		]:
			classify_attrib_name(key, data_dict[key]['attr'])

		nm_dict = data_dict['nm']  # type: dict
		for key in [
			'srcN', 'trgN',
			'srcTg', 'trgTg',
			'srcBiTg', 'trgBiTg',
		]:
			classify_attrib_name(key, nm_dict[key])

		for key in auto_generated_keys:
			attr_name = key
			while attr_name in already_passed_attribs:
				attr_name = '{}_'.format(attr_name)
			assert attr_name not in already_passed_attribs
			out_dict[key] = attr_name
			already_passed_add(attr_name)

	def _main(self):
		self._main_uvs()
		self._main_udims()
		self._main_on_off_channels()
		self._main_base_color_channels()
		self._main_pbr_channels()
		self._main_mask_channels()
		self._main_ensure_out_channel_names_unique()
		self._main_nm_attribs()
		self._main_internal_attribs()
		cleanup_out_data(self.data_dict, del_root_keys=False)

	def main(self):
		caught_error, msg = catch_error_message(self._main, '')
		if caught_error is not None:
			self.data_dict['error'] = msg
		return dumps(self.data_dict, indent=2)
