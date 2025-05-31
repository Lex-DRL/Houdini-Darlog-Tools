// Mozilla Public License 2.0
// 
// Copyright (c) 2020 Lex Darlog (aka DRL)
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.


#ifndef __darlog_kineFX_blendShape_messageName_lib__
#define __darlog_kineFX_blendShape_messageName_lib__

// #include "kineFX_blendShape_messageName.h"

// Generates meaningful (aka suitable for error messages) blendShape name,
// clearly identifying the blendshape and mesh it's a part of.


function string kineFX_blendShape_messageName(string mesh_name, bs_name, bs_ch) {
	// Just format already known geo/BS-name
	if (bs_name == "") {
		// Fall back to blendShape channel name.
		bs_name = bs_ch;
	}
	if (mesh_name != "" && bs_name != "") {
		return sprintf("\"%s\" -> \"%s\" blend-shape", mesh_name, bs_name);
	}
	return sprintf("\"%s\" blend-shape in \"%s\" mesh", bs_name, mesh_name);
}


function string kineFX_blendShape_messageName_fromFirstPacked(int input_i) {
	// From the given input, attempt to find the first non-empty names.
	// Might be useful when multiple blendShapes ONLY for the same mesh
	// are passed at once, but the first one might have an empty name.
	int n_bs = nprimitives(input_i);
	string mesh_name = "";
	string bs_name = "";
	string bs_fallback_name = "";
	for (int i=0; i<n_bs; i++) {
		if (mesh_name == "") {
			mesh_name = prim(input_i, "name", i);
		}
		if (bs_name == "") {
			bs_name = prim(input_i, "blendshape_name", i);
			bs_fallback_name = bs_name != "" ? bs_name : prim(input_i, "blendshape_channel", i);
		}
		if (mesh_name != "" && bs_fallback_name != "") {
			return sprintf("\"%s\" -> \"%s\" blend-shape", mesh_name, bs_fallback_name);
		}
	}
	return sprintf("\"%s\" blend-shape in \"%s\" mesh", bs_fallback_name, mesh_name);
}


function string kineFX_blendShape_messageName_fromPacked(int input_i, packedPrim_i) {
	// When you need to get BS-name from an explicitly specified packed-prim in given input.
	int n_prims = nprimitives(input_i);
	if (packedPrim_i < 0 || packedPrim_i >= n_prims) {
		error(
			"Can't get a name from blend-shape in prim %d: input %d has only %d %s",
			packedPrim_i, input_i, n_prims, (n_prims==1 ? "prim" : "prims")
		);
		return "";
	}
	
	string mesh_name = prim(input_i, "name", packedPrim_i);
	string bs_name = prim(input_i, "blendshape_name", packedPrim_i);
	string bs_ch = prim(input_i, "blendshape_channel", packedPrim_i);
	return kineFX_blendShape_messageName(mesh_name, bs_name, bs_ch);
}


function string kineFX_blendShape_messageName_fromDetail(int input_i) {
	// Useful when you iterate over packed prims per mesh-name in two nested for-loops
	// AND you pre-promote blendShape string-attribs from prim to detail inside the inner loop.
	// Thus, the same attribs are assumed to be in detail class.
	string mesh_name = detail(input_i, "name");
	string bs_name = detail(input_i, "blendshape_name");
	string bs_ch = detail(input_i, "blendshape_channel");
	return kineFX_blendShape_messageName(mesh_name, bs_name, bs_ch);
}

#endif
