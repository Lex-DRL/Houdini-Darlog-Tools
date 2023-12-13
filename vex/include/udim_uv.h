// Mozilla Public License 2.0
// 
// Copyright (c) 2020 Lex Darlog (aka DRL)
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.


#ifndef __darlog_udim_uv_lib__
#define __darlog_udim_uv_lib__

// #include "udim_uv.h"

// Calculate position (aka offset) of a specific UDIM.
// All incorrect UDIMs (less than 1001) are treated as (-1, 0).


function void udim_cell_ints(int udim_i; /*out*/ int cell_u, cell_v) {
	int cell_i = udim_i - 1001;
	if (cell_i < 0) {
		cell_u = -1;
		cell_v = 0;
		return;
	}
	cell_u = cell_i % 10;
	cell_v = cell_i / 10;
}

function vector2 udim_uv(int udim_i) {
	int cell_u, cell_v;
	udim_cell_ints(udim_i, cell_u, cell_v);
	return set(cell_u, cell_v);
}
function vector2 udim_uv(int udim_i; /*out*/ int cell_u, cell_v) {
	udim_cell_ints(udim_i, cell_u, cell_v);
	return set(cell_u, cell_v);
}

function vector udim_uv(int udim_i) {
	int cell_u, cell_v;
	udim_cell_ints(udim_i, cell_u, cell_v);
	return set(cell_u, cell_v, 0);
}
function vector udim_uv(int udim_i; /*out*/ int cell_u, cell_v) {
	udim_cell_ints(udim_i, cell_u, cell_v);
	return set(cell_u, cell_v, 0);
}

function vector4 udim_uv(int udim_i) {
	int cell_u, cell_v;
	udim_cell_ints(udim_i, cell_u, cell_v);
	return set(cell_u, cell_v, 0, 0);
}
function vector4 udim_uv(int udim_i; /*out*/ int cell_u, cell_v) {
	udim_cell_ints(udim_i, cell_u, cell_v);
	return set(cell_u, cell_v, 0, 0);
}

#endif
