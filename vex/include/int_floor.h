// Mozilla Public License 2.0
// 
// Copyright (c) 2020 Lex Darlog (aka DRL)
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.


#ifndef __darlog_int_floor_lib__
#define __darlog_int_floor_lib__

// #include "int_floor.h"

// Proper float-to-int cast, working correct on negative numbers.


function int int_floor(float val) {
	if (val < 0.0) {
		// For some reason, VEX doesn't turn -0.x to -1. So - some trickery:
		float pos_val = ceil(-val) + 0.25;
		return -(int)pos_val;
	}
	return (int)val;
}

#endif
