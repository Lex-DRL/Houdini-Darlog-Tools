// Mozilla Public License 2.0
// 
// Copyright (c) 2020 Lex Darlog (aka DRL)
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.


#ifndef __darlog_uv_cell_lib__
#define __darlog_uv_cell_lib__

// #include "uv_cell.h"

// Detect U/V-cell from the actual UVs.


#include "int_floor.h"


function void uv_cell_ints(float u, v; /*out*/ int u_cell, v_cell) {
	u_cell = int_floor(u);
	v_cell = int_floor(v);
}
function void uv_cell_ints(vector2 uv; /*out*/ int u_cell, v_cell) {
	u_cell = int_floor(uv.x);
	v_cell = int_floor(uv.y);
}
function void uv_cell_ints(vector uv; /*out*/ int u_cell, v_cell) {
	u_cell = int_floor(uv.x);
	v_cell = int_floor(uv.y);
}
function void uv_cell_ints(vector4 uv; /*out*/ int u_cell, v_cell) {
	u_cell = int_floor(uv.x);
	v_cell = int_floor(uv.y);
}


function string uv_cell_str(int u_cell, v_cell) {
	return sprintf("U%i_V%i", u_cell, v_cell);
}


function string uv_cell_str(float u, v) {
	int u_cell = int_floor(u);
	int v_cell = int_floor(v);
	return sprintf("U%i_V%i", u_cell, v_cell);
}
function string uv_cell_str(float u, v; /*out*/ int u_cell, v_cell) {
	u_cell = int_floor(u);
	v_cell = int_floor(v);
	return sprintf("U%i_V%i", u_cell, v_cell);
}

function string uv_cell_str(vector2 uv) {
	return uv_cell_str(uv.x, uv.y);
}
function string uv_cell_str(vector2 uv; /*out*/ int u_cell, v_cell) {
	return uv_cell_str(uv.x, uv.y, u_cell, v_cell);
}

function string uv_cell_str(vector uv) {
	return uv_cell_str(uv.x, uv.y);
}
function string uv_cell_str(vector uv; /*out*/ int u_cell, v_cell) {
	return uv_cell_str(uv.x, uv.y, u_cell, v_cell);
}

function string uv_cell_str(vector4 uv) {
	return uv_cell_str(uv.x, uv.y);
}
function string uv_cell_str(vector4 uv; /*out*/ int u_cell, v_cell) {
	return uv_cell_str(uv.x, uv.y, u_cell, v_cell);
}

#endif
