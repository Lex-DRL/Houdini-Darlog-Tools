// Mozilla Public License 2.0
// 
// Copyright (c) 2020 Lex Darlog (aka DRL)
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.


#ifndef __darlog_is_inline_point_lib__
#define __darlog_is_inline_point_lib__

// #include "is_inline_point.h"

// A function to detect inline points. I.e., the ones that contribute
// to primitive shape less than a given threshold.
// The function is designed to work with non-triangulated geometry.
// I.e., consisting only from primitives with lots of points, each primitive
// being it's own separate piece.
// It will work with a regular geo, but ALL the points shared by more than
// 2 prims will be considered as not-inline, regardless of
// their contribution to the actual shape.


// The check is naiive, it doesn't take into acoount series of points,
// which all have a tiny contribution, but together might change
// the shape significantly.
// This function will mar all of them as inline (subject to deletion).


function int is_inline_point(int pt_i; vector pt_P; float max_dist_val) {
	int pts[] = neighbours(0, pt_i);
	if (len(pts) != 2) {
		return 0;
	}
	if (pts[0] < 0 || pts[1] < 0) {
		return 0;
	}
	
	vector p0 = point(0, "P", pts[0]);
	vector p1 = point(0, "P", pts[1]);
	
	float max_dist = abs(max_dist_val);
	
	vector edgeV = p1 - p0;
	float edge_len = abs(length(edgeV));
	if (edge_len < max_dist) {
		// The prev/next points are so close to each other that any linear algebra doesn't make sense.
		// Let's just assume they are at exactly the same pos, and compensate distance between their
		// average and P with an approximate error.
		// The error value half of each points' distance from their center. I.e., 0.25 of edge length.
		vector midP = (p0 + p1) * 0.5;
		return (
			abs(distance(pt_P, midP)) + 0.25 * edge_len <= max_dist
		);
	}
	
	// The distance between points is at least somewhat meaningful
	vector localP = pt_P - p0;
	vector edgeV_norm = edgeV / edge_len;
	vector local_P_projection = edgeV_norm * dot(edgeV_norm, localP);
	
	return abs(distance(localP, local_P_projection)) <= max_dist;
}

#endif
