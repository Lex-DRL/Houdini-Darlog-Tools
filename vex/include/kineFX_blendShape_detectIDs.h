// Mozilla Public License 2.0
// 
// Copyright (c) 2020 Lex Darlog (aka DRL)
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.


#ifndef __darlog_kineFX_blendShape_detectIDs_lib__
#define __darlog_kineFX_blendShape_detectIDs_lib__

// #include "kineFX_blendShape_detectIDs.h"

// Utility function which detects whether id-attribs (point/prim) are present in blendShape-geo for KineFX
// (and also whether there's a geo at all).

#include "attrib_type_str.h"
#include "kineFX_blendShape_messageName.h"


function void error_kineFX_blendShape_wrong_id_attr(string bs_msgNm, attr_cls; int tp_id, sz) {
	error("%s has 'id' %s-attribute of a wrong type. Expected: int. Got: %s", bs_msgNm, attr_cls, attrib_type_str(tp_id, sz));
}

// ---------------------------------------------------------

// The actual ID-detecting function, assuming all the error-check work is done.
function void __kineFX_blendShape_detectIDs(
	int input_singleBlendShape_geo, has_bs; // has_bs = 0/1/2
	string bs_msgNm;
	// out:
	int has_id_pt, has_id_prim
) {
	has_id_pt = haspointattrib(input_singleBlendShape_geo, "id");
	if (has_id_pt) {
		int sz = pointattribsize(input_singleBlendShape_geo, "id");
		int tp_id = pointattribtype(input_singleBlendShape_geo, "id");
		if (tp_id != 0 /*int*/ || sz > 1) {
			error_kineFX_blendShape_wrong_id_attr(bs_msgNm, "POINT", tp_id, sz);
		}
	}
	
	has_id_prim = 0;
	if (has_bs < 2) {
		// Has BS-geo, but not prims in it. Thus, ignore prim-IDs
		return;
	}
	has_id_prim = hasprimattrib(input_singleBlendShape_geo, "id"); // on a separate line, since we nedd to set the var ONLY IF we have prims
	if (has_id_prim) {
		int sz = primattribsize(input_singleBlendShape_geo, "id");
		int tp_id = primattribtype(input_singleBlendShape_geo, "id");
		if (tp_id != 0 /*int*/ || sz > 1) {
			error_kineFX_blendShape_wrong_id_attr(bs_msgNm, "PRIM", tp_id, sz);
		}
	}
	
	// has_id_vtx = hasvertexattrib(input_singleBlendShape_geo, "id");
	// if (has_id_vtx) {
	// 	int sz = vertexattribsize(input_singleBlendShape_geo, "id");
	// 	int tp_id = vertexattribtype(input_singleBlendShape_geo, "id");
	// 	if (tp_id != 0 /*int*/ || sz > 1) {
	// 		error_kineFX_blendShape_wrong_id_attr(bs_msgNm, "VERTEX", tp_id, sz);
	// 	}
	// }
}

// ---------------------------------------------------------

// When blendShape's string attribs are promoted to detail in extra input
function void kineFX_blendShape_detectIDs_namesFromDetail(
	int input_singleBlendShape_geo, input_singleBlendShape_detailNames;
	// out:
	int has_bs;
	// 0 - no blendShapes
	// 1 - has blendShape(s)
	// 2 - has blendShape(s) + prims in them
	int has_id_pt, has_id_prim; string bs_msgNm
) {
	has_bs = has_id_pt = has_id_prim = 0;
	bs_msgNm = kineFX_blendShape_messageName_fromDetail(input_singleBlendShape_detailNames);
	
	if (npoints(input_singleBlendShape_geo) < 1) {
		return;
	}
	has_bs = nprimitives(input_singleBlendShape_geo) > 0 ? 2 : 1;
	
	__kineFX_blendShape_detectIDs(
		input_singleBlendShape_geo, has_bs, bs_msgNm,
		/*out*/ has_id_pt, has_id_prim
	);
}

// Overload without blendShape-msgName:
function void kineFX_blendShape_detectIDs_namesFromDetail(
	int input_singleBlendShape_geo, input_singleBlendShape_detailNames;
	// out:
	int has_bs, has_id_pt, has_id_prim
) {
	string bs_msgNm;
	kineFX_blendShape_detectIDs_namesFromDetail(input_singleBlendShape_geo, input_singleBlendShape_detailNames, /*out*/ has_bs, has_id_pt, has_id_prim, bs_msgNm);
}

// ---------------------------------------------------------

// When blendShape's string attribs are on packed prims in extra input
function void kineFX_blendShape_detectIDs_namesFromPacked(
	int input_singleBlendShape_geo, input_singleBlendShape_packed;
	// out:
	int has_bs;
	// 0 - no blendShapes
	// 1 - has blendShape(s)
	// 2 - has blendShape(s) + prims in them
	int has_id_pt, has_id_prim; string bs_msgNm
) {
	has_bs = has_id_pt = has_id_prim = 0;
	bs_msgNm = "";
	
	int n_bs = nprimitives(input_singleBlendShape_packed);
	if (n_bs < 1 || npoints(input_singleBlendShape_geo) < 1) {
		return;
	}
	has_bs = nprimitives(input_singleBlendShape_geo) > 0 ? 2 : 1;
	bs_msgNm = kineFX_blendShape_messageName_fromPacked(input_singleBlendShape_packed, 0);
	
	if (n_bs > 1) {
		string multi_bs_names = sprintf("\n\t%s", bs_msgNm);
		for (int i=1; i<n_bs; i++) {
			multi_bs_names = sprintf("%s\n\t%s", multi_bs_names, kineFX_blendShape_messageName_fromPacked(input_singleBlendShape_packed, i));
		}
		error("Multiple prims (packed blend-shapes?) exist in %d input:%s", input_singleBlendShape_packed, multi_bs_names);
		return;
	}
	
	__kineFX_blendShape_detectIDs(
		input_singleBlendShape_geo, has_bs, bs_msgNm,
		/*out*/ has_id_pt, has_id_prim
	);
}

// Overload without blendShape-msgName:
function void kineFX_blendShape_detectIDs_namesFromPacked(
	int input_singleBlendShape_geo, input_singleBlendShape_packed;
	// out:
	int has_bs, has_id_pt, has_id_prim
) {
	string bs_msgNm;
	kineFX_blendShape_detectIDs_namesFromPacked(input_singleBlendShape_geo, input_singleBlendShape_packed, /*out*/ has_bs, has_id_pt, has_id_prim, bs_msgNm);
}

#endif
