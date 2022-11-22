// Mozilla Public License 2.0
// 
// Copyright (c) 2020 Lex Darlog (aka DRL)
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.


#ifndef __darlog_srgb_lib__
#define __darlog_srgb_lib__

// #include "srgb.h"

// This library contains functions converting a color value between
// linear and sRGB color spaces.



// Linear -> sRGB

float to_sRGB(float clr) {
	float sClr = sign(clr);
	float absClr = clr * sClr;
	if (absClr > 0.0031308)
		return sClr * (
			1.055 * pow(
				absClr,
				0.41666666666666666667 // 1.0 / 2.4
			) - 0.055
		);
	return clr * 12.92;
}

vector2 to_sRGB(vector2 clr) {
	vector2 sClr = sign(clr);
	vector2 absClr = clr * sClr;
	
	vector2 below_t = clr * 12.92;
	vector2 above_t = sClr * (
		1.055 * pow(
			absClr,
			0.41666666666666666667 // 1.0 / 2.4
		) - 0.055
	);
	return set(
		absClr.x > 0.0031308 ? above_t.x : below_t.x,
		absClr.y > 0.0031308 ? above_t.y : below_t.y
	);
}

vector to_sRGB(vector clr) {
	vector sClr = sign(clr);
	vector absClr = clr * sClr;
	
	vector below_t = clr * 12.92;
	vector above_t = sClr * (
		1.055 * pow(
			absClr,
			0.41666666666666666667 // 1.0 / 2.4
		) - 0.055
	);
	return set(
		absClr.x > 0.0031308 ? above_t.x : below_t.x,
		absClr.y > 0.0031308 ? above_t.y : below_t.y,
		absClr.z > 0.0031308 ? above_t.z : below_t.z
	);
}

vector4 to_sRGB(vector4 clr) {
	vector4 sClr = sign(clr);
	vector4 absClr = clr * sClr;
	
	vector4 below_t = clr * 12.92;
	vector4 above_t = sClr * (
		1.055 * pow(
			absClr,
			0.41666666666666666667 // 1.0 / 2.4
		) - 0.055
	);
	return set(
		absClr.x > 0.0031308 ? above_t.x : below_t.x,
		absClr.y > 0.0031308 ? above_t.y : below_t.y,
		absClr.z > 0.0031308 ? above_t.z : below_t.z,
		absClr.w > 0.0031308 ? above_t.w : below_t.w
	);
}

// --------------------------------------------------------

// sRGB -> Linear

float from_sRGB(float clr) {
	float sClr = sign(clr);
	float absClr = clr * sClr;
	if (absClr > 0.04045)
		return sClr * pow(
			(absClr + 0.055) * 0.94786729857819905213,  // divide by (1 + 0.055)
			2.4
		);
	return clr * 0.07739938080495356037; // divide by 12.92
}

vector2 from_sRGB(vector2 clr) {
	vector2 sClr = sign(clr);
	vector2 absClr = clr * sClr;
	
	vector below_t = clr * 0.07739938080495356037; // divide by 12.92
	vector above_t = sClr * pow(
		(absClr + 0.055) * 0.94786729857819905213,  // divide by (1 + 0.055)
		2.4
	);
	return set(
		absClr.x > 0.04045 ? above_t.x : below_t.x,
		absClr.y > 0.04045 ? above_t.y : below_t.y
	);
}

vector from_sRGB(vector clr) {
	vector sClr = sign(clr);
	vector absClr = clr * sClr;
	
	vector below_t = clr * 0.07739938080495356037; // divide by 12.92
	vector above_t = sClr * pow(
		(absClr + 0.055) * 0.94786729857819905213,  // divide by (1 + 0.055)
		2.4
	);
	return set(
		absClr.x > 0.04045 ? above_t.x : below_t.x,
		absClr.y > 0.04045 ? above_t.y : below_t.y,
		absClr.z > 0.04045 ? above_t.z : below_t.z
	);
}

vector4 from_sRGB(vector4 clr) {
	vector4 sClr = sign(clr);
	vector4 absClr = clr * sClr;
	
	vector4 below_t = clr * 0.07739938080495356037; // divide by 12.92
	vector4 above_t = sClr * pow(
		(absClr + 0.055) * 0.94786729857819905213,  // divide by (1 + 0.055)
		2.4
	);
	return set(
		absClr.x > 0.04045 ? above_t.x : below_t.x,
		absClr.y > 0.04045 ? above_t.y : below_t.y,
		absClr.z > 0.04045 ? above_t.z : below_t.z,
		absClr.w > 0.04045 ? above_t.w : below_t.w
	);
}

#endif
