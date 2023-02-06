// Mozilla Public License 2.0
// 
// Copyright (c) 2020 Lex Darlog (aka DRL)
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.


#ifndef __darlog_uv_udim_lib__
#define __darlog_uv_udim_lib__

// #include "uv_udim.h"

// Detect UDIM from UVs.
// Return 1000 if UVs are outside valid UDIM range.


#include "int_floor.h"


function int uv_udim(int u_cell, v_cell) {
	int out_u_cell = u_cell;
	int out_v_cell = v_cell;
	if (out_u_cell < 0 || out_u_cell > 9 || out_v_cell < 0) {
		out_u_cell = -1;
		out_v_cell = 0;
	}
	return 1001 + out_u_cell + out_v_cell * 10;
}

function int uv_udim(float u, v) {
	return uv_udim(int_floor(u), int_floor(v));
}

function int uv_udim(vector2 uv) {
	return uv_udim(uv.x, uv.y);
}
function int uv_udim(vector uv) {
	return uv_udim(uv.x, uv.y);
}
function int uv_udim(vector4 uv) {
	return uv_udim(uv.x, uv.y);
}

#endif
