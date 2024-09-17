// Mozilla Public License 2.0
// 
// Copyright (c) 2020 Lex Darlog (aka DRL)
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.


#ifndef __darlog_matrix_swap_lines_lib__
#define __darlog_matrix_swap_lines_lib__

// #include "matrix_swap_lines.h"

function void matrix_swap_rows(export matrix M; int a, b) {
    if(a == b)
        return;
	vector4 buffer = set(
		getcomp(M, b, 0),
		getcomp(M, b, 1),
		getcomp(M, b, 2),
		getcomp(M, b, 3)
	);
	setcomp(M, getcomp(M, a, 0), b, 0);
	setcomp(M, getcomp(M, a, 1), b, 1);
	setcomp(M, getcomp(M, a, 2), b, 2);
	setcomp(M, getcomp(M, a, 3), b, 3);
	
	setcomp(M, buffer.x, a, 0);
	setcomp(M, buffer.y, a, 1);
	setcomp(M, buffer.z, a, 2);
	setcomp(M, buffer.w, a, 3);
}

function void matrix_swap_rows(export matrix3 M; int a, b) {
    if(a == b)
        return;
	vector buffer = set(
		getcomp(M, b, 0),
		getcomp(M, b, 1),
		getcomp(M, b, 2)
	);
	setcomp(M, getcomp(M, a, 0), b, 0);
	setcomp(M, getcomp(M, a, 1), b, 1);
	setcomp(M, getcomp(M, a, 2), b, 2);
	
	setcomp(M, buffer.x, a, 0);
	setcomp(M, buffer.y, a, 1);
	setcomp(M, buffer.z, a, 2);
}

function void matrix_swap_rows(export matrix2 M; int a, b) {
    if(a == b)
        return;
	vector2 buffer = set(
		getcomp(M, b, 0),
		getcomp(M, b, 1)
	);
	setcomp(M, getcomp(M, a, 0), b, 0);
	setcomp(M, getcomp(M, a, 1), b, 1);
	
	setcomp(M, buffer.x, a, 0);
	setcomp(M, buffer.y, a, 1);
}

// --------------------------------------------------------

function void matrix_swap_columns(export matrix M; int a, b) {
    if(a == b)
        return;
	vector4 buffer = set(
		getcomp(M, 0, b),
		getcomp(M, 1, b),
		getcomp(M, 2, b),
		getcomp(M, 3, b)
	);
	setcomp(M, getcomp(M, 0, a), 0, b);
	setcomp(M, getcomp(M, 1, a), 1, b);
	setcomp(M, getcomp(M, 2, a), 2, b);
	setcomp(M, getcomp(M, 3, a), 3, b);
	
	setcomp(M, buffer.x, 0, a);
	setcomp(M, buffer.y, 1, a);
	setcomp(M, buffer.z, 2, a);
	setcomp(M, buffer.w, 3, a);
}

function void matrix_swap_columns(export matrix3 M; int a, b) {
    if(a == b)
        return;
	vector buffer = set(
		getcomp(M, 0, b),
		getcomp(M, 1, b),
		getcomp(M, 2, b)
	);
	setcomp(M, getcomp(M, 0, a), 0, b);
	setcomp(M, getcomp(M, 1, a), 1, b);
	setcomp(M, getcomp(M, 2, a), 2, b);
	
	setcomp(M, buffer.x, 0, a);
	setcomp(M, buffer.y, 1, a);
	setcomp(M, buffer.z, 2, a);
}

function void matrix_swap_columns(export matrix2 M; int a, b) {
    if(a == b)
        return;
	vector2 buffer = set(
		getcomp(M, 0, b),
		getcomp(M, 1, b)
	);
	setcomp(M, getcomp(M, 0, a), 0, b);
	setcomp(M, getcomp(M, 1, a), 1, b);
	
	setcomp(M, buffer.x, 0, a);
	setcomp(M, buffer.y, 1, a);
}

#endif
