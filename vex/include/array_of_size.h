#ifndef __drl_array_of_size_lib__
#define __drl_array_of_size_lib__

// #include "array_of_size.h"

// A library of many function-overloads to initialize an array of specific size,
// (optionally) with a default value.
//
// There are two overload signatures:
//
// * with a hardcoded array size (slightly faster):
//   '''
//   <type> arr[] = array_of_size(int size [, <type> initial_item_value])
//   '''
//
// * with an arbitrary size provided as argument:
//   '''
//   <type> arr[] = array_of_size<size>([<type> initial_item_value])
//   '''
//
//   * sizes are: 2, 3, 4, 9, 16
//
// Also, for matrices - there's an extra signature - for an ease of
// creating an array with all matrices being identity:
//   '''
//   <type> arr[] = array_of_size(int size, int is_identity)
//   '''



// =====================================
// Initialize empty arrays of size
// =====================================



// ---------------------------
// string[]

function string[] array_of_size(int size) {
	string res[] = {};
	resize(res, max(0, size));
	return res;
}
// and a few edge-case funcs for common numbers:
function string[] array_of_size2() {
	return array("", "");
}
function string[] array_of_size3() {
	return array("", "", "");
}
function string[] array_of_size4() {
	return array("", "", "", "");
}
function string[] array_of_size9() {
	return array("", "", "", "", "", "", "", "", "");
}
function string[] array_of_size16() {
	return array("", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "");
}

// ---------------------------
// int[]

function int[] array_of_size(int size) {
	int res[] = {};
	resize(res, max(0, size));
	return res;
}
// and a few edge-case funcs for common numbers:
function int[] array_of_size2() {
	return array(0, 0);
}
function int[] array_of_size3() {
	return array(0, 0, 0);
}
function int[] array_of_size4() {
	return array(0, 0, 0, 0);
}
function int[] array_of_size9() {
	return array(0, 0, 0, 0, 0, 0, 0, 0, 0);
}
function int[] array_of_size16() {
	return array(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
}

// ---------------------------
// float[]

function float[] array_of_size(int size) {
	float res[] = {};
	resize(res, max(0, size));
	return res;
}
// and a few edge-case funcs for common numbers:
function float[] array_of_size2() {
	return array(0.0, 0.0);
}
function float[] array_of_size3() {
	return array(0.0, 0.0, 0.0);
}
function float[] array_of_size4() {
	return array(0.0, 0.0, 0.0, 0.0);
}
function float[] array_of_size9() {
	return array(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
}
function float[] array_of_size16() {
	return array(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
}

// ---------------------------
// vector2[]

function vector2[] array_of_size(int size) {
	vector2 res[] = {};
	resize(res, max(0, size));
	return res;
}
// and a few edge-case funcs for common numbers:
function vector2[] array_of_size2() {
	vector2 val = {0, 0};
	return array(val, val);
}
function vector2[] array_of_size3() {
	vector2 val = {0, 0};
	return array(val, val, val);
}
function vector2[] array_of_size4() {
	vector2 val = {0, 0};
	return array(val, val, val, val);
}
function vector2[] array_of_size9() {
	vector2 val = {0, 0};
	return array(val, val, val, val, val, val, val, val, val);
}
function vector2[] array_of_size16() {
	vector2 val = {0, 0};
	return array(val, val, val, val, val, val, val, val, val, val, val, val, val, val, val, val);
}

// ---------------------------
// vector[]

function vector[] array_of_size(int size) {
	vector res[] = {};
	resize(res, max(0, size));
	return res;
}
// and a few edge-case funcs for common numbers:
function vector[] array_of_size2() {
	vector val = {0, 0, 0};
	return array(val, val);
}
function vector[] array_of_size3() {
	vector val = {0, 0, 0};
	return array(val, val, val);
}
function vector[] array_of_size4() {
	vector val = {0, 0, 0};
	return array(val, val, val, val);
}
function vector[] array_of_size9() {
	vector val = {0, 0, 0};
	return array(val, val, val, val, val, val, val, val, val);
}
function vector[] array_of_size16() {
	vector val = {0, 0, 0};
	return array(val, val, val, val, val, val, val, val, val, val, val, val, val, val, val, val);
}

// ---------------------------
// vector4[]

function vector4[] array_of_size(int size) {
	vector4 res[] = {};
	resize(res, max(0, size));
	return res;
}
// and a few edge-case funcs for common numbers:
function vector4[] array_of_size2() {
	vector4 val = {0, 0, 0, 0};
	return array(val, val);
}
function vector4[] array_of_size3() {
	vector4 val = {0, 0, 0, 0};
	return array(val, val, val);
}
function vector4[] array_of_size4() {
	vector4 val = {0, 0, 0, 0};
	return array(val, val, val, val);
}
function vector4[] array_of_size9() {
	vector4 val = {0, 0, 0, 0};
	return array(val, val, val, val, val, val, val, val, val);
}
function vector4[] array_of_size16() {
	vector4 val = {0, 0, 0, 0};
	return array(val, val, val, val, val, val, val, val, val, val, val, val, val, val, val, val);
}

// ---------------------------
// matrix2[]

function matrix2[] array_of_size(int size) {
	matrix2 res[] = {};
	resize(res, max(0, size));
	return res;
}
// and a few edge-case funcs for common numbers:
function matrix2[] array_of_size2() {
	matrix2 val = { {1, 0}, {0, 1} }; // identity matrix
	return array(val, val);
}
function matrix2[] array_of_size3() {
	matrix2 val = { {1, 0}, {0, 1} }; // identity matrix
	return array(val, val, val);
}
function matrix2[] array_of_size4() {
	matrix2 val = { {1, 0}, {0, 1} }; // identity matrix
	return array(val, val, val, val);
}
function matrix2[] array_of_size9() {
	matrix2 val = { {1, 0}, {0, 1} }; // identity matrix
	return array(val, val, val, val, val, val, val, val, val);
}
function matrix2[] array_of_size16() {
	matrix2 val = { {1, 0}, {0, 1} }; // identity matrix
	return array(val, val, val, val, val, val, val, val, val, val, val, val, val, val, val, val);
}

// ---------------------------
// matrix3[]

function matrix3[] array_of_size(int size) {
	matrix3 res[] = {};
	resize(res, max(0, size));
	return res;
}
// and a few edge-case funcs for common numbers:
function matrix3[] array_of_size2() {
	matrix3 val = { {1, 0, 0}, {0, 1, 0}, {0, 0, 1} }; // identity matrix
	return array(val, val);
}
function matrix3[] array_of_size3() {
	matrix3 val = { {1, 0, 0}, {0, 1, 0}, {0, 0, 1} }; // identity matrix
	return array(val, val, val);
}
function matrix3[] array_of_size4() {
	matrix3 val = { {1, 0, 0}, {0, 1, 0}, {0, 0, 1} }; // identity matrix
	return array(val, val, val, val);
}
function matrix3[] array_of_size9() {
	matrix3 val = { {1, 0, 0}, {0, 1, 0}, {0, 0, 1} }; // identity matrix
	return array(val, val, val, val, val, val, val, val, val);
}
function matrix3[] array_of_size16() {
	matrix3 val = { {1, 0, 0}, {0, 1, 0}, {0, 0, 1} }; // identity matrix
	return array(val, val, val, val, val, val, val, val, val, val, val, val, val, val, val, val);
}

// ---------------------------
// matrix[]

function matrix[] array_of_size(int size) {
	matrix res[] = {};
	resize(res, max(0, size));
	return res;
}
// and a few edge-case funcs for common numbers:
function matrix[] array_of_size2() {
	matrix val = { {1, 0, 0, 0}, {0, 1, 0, 0}, {0, 0, 1, 0}, {0, 0, 0, 1} }; // identity matrix
	return array(val, val);
}
function matrix[] array_of_size3() {
	matrix val = { {1, 0, 0, 0}, {0, 1, 0, 0}, {0, 0, 1, 0}, {0, 0, 0, 1} }; // identity matrix
	return array(val, val, val);
}
function matrix[] array_of_size4() {
	matrix val = { {1, 0, 0, 0}, {0, 1, 0, 0}, {0, 0, 1, 0}, {0, 0, 0, 1} }; // identity matrix
	return array(val, val, val, val);
}
function matrix[] array_of_size9() {
	matrix val = { {1, 0, 0, 0}, {0, 1, 0, 0}, {0, 0, 1, 0}, {0, 0, 0, 1} }; // identity matrix
	return array(val, val, val, val, val, val, val, val, val);
}
function matrix[] array_of_size16() {
	matrix val = { {1, 0, 0, 0}, {0, 1, 0, 0}, {0, 0, 1, 0}, {0, 0, 0, 1} }; // identity matrix
	return array(val, val, val, val, val, val, val, val, val, val, val, val, val, val, val, val);
}



// =====================================
// Initialize arrays of size with default values
// =====================================



// ---------------------------
// string[]

function string[] array_of_size(int size; string val) {
	string res[] = {};
	resize(res, max(0, size));
	for (int i = 0; i < size; i++) {
		res[i] = val;
	}
	return res;
}
// and a few edge-case funcs for common numbers:
function string[] array_of_size2(string val) {
	return array(val, val);
}
function string[] array_of_size3(string val) {
	return array(val, val, val);
}
function string[] array_of_size4(string val) {
	return array(val, val, val, val);
}
function string[] array_of_size9(string val) {
	return array(val, val, val, val, val, val, val, val, val);
}
function string[] array_of_size16(string val) {
	return array(val, val, val, val, val, val, val, val, val, val, val, val, val, val, val, val);
}

// ---------------------------
// int[]

function int[] array_of_size(int size; int val) {
	int res[] = {};
	resize(res, max(0, size));
	for (int i = 0; i < size; i++) {
		res[i] = val;
	}
	return res;
}
// and a few edge-case funcs for common numbers:
function int[] array_of_size2(int val) {
	return array(val, val);
}
function int[] array_of_size3(int val) {
	return array(val, val, val);
}
function int[] array_of_size4(int val) {
	return array(val, val, val, val);
}
function int[] array_of_size9(int val) {
	return array(val, val, val, val, val, val, val, val, val);
}
function int[] array_of_size16(int val) {
	return array(val, val, val, val, val, val, val, val, val, val, val, val, val, val, val, val);
}

// ---------------------------
// float[]

function float[] array_of_size(int size; float val) {
	float res[] = {};
	resize(res, max(0, size));
	for (int i = 0; i < size; i++) {
		res[i] = val;
	}
	return res;
}
// and a few edge-case funcs for common numbers:
function float[] array_of_size2(float val) {
	return array(val, val);
}
function float[] array_of_size3(float val) {
	return array(val, val, val);
}
function float[] array_of_size4(float val) {
	return array(val, val, val, val);
}
function float[] array_of_size9(float val) {
	return array(val, val, val, val, val, val, val, val, val);
}
function float[] array_of_size16(float val) {
	return array(val, val, val, val, val, val, val, val, val, val, val, val, val, val, val, val);
}

// ---------------------------
// vector2[]

function vector2[] array_of_size(int size; vector2 val) {
	vector2 res[] = {};
	resize(res, max(0, size));
	for (int i = 0; i < size; i++) {
		res[i] = val;
	}
	return res;
}
// and a few edge-case funcs for common numbers:
function vector2[] array_of_size2(vector2 val) {
	return array(val, val);
}
function vector2[] array_of_size3(vector2 val) {
	return array(val, val, val);
}
function vector2[] array_of_size4(vector2 val) {
	return array(val, val, val, val);
}
function vector2[] array_of_size9(vector2 val) {
	return array(val, val, val, val, val, val, val, val, val);
}
function vector2[] array_of_size16(vector2 val) {
	return array(val, val, val, val, val, val, val, val, val, val, val, val, val, val, val, val);
}

// ---------------------------
// vector[]

function vector[] array_of_size(int size; vector val) {
	vector res[] = {};
	resize(res, max(0, size));
	for (int i = 0; i < size; i++) {
		res[i] = val;
	}
	return res;
}
// and a few edge-case funcs for common numbers:
function vector[] array_of_size2(vector val) {
	return array(val, val);
}
function vector[] array_of_size3(vector val) {
	return array(val, val, val);
}
function vector[] array_of_size4(vector val) {
	return array(val, val, val, val);
}
function vector[] array_of_size9(vector val) {
	return array(val, val, val, val, val, val, val, val, val);
}
function vector[] array_of_size16(vector val) {
	return array(val, val, val, val, val, val, val, val, val, val, val, val, val, val, val, val);
}

// ---------------------------
// vector4[]

function vector4[] array_of_size(int size; vector4 val) {
	vector4 res[] = {};
	resize(res, max(0, size));
	for (int i = 0; i < size; i++) {
		res[i] = val;
	}
	return res;
}
// and a few edge-case funcs for common numbers:
function vector4[] array_of_size2(vector4 val) {
	return array(val, val);
}
function vector4[] array_of_size3(vector4 val) {
	return array(val, val, val);
}
function vector4[] array_of_size4(vector4 val) {
	return array(val, val, val, val);
}
function vector4[] array_of_size9(vector4 val) {
	return array(val, val, val, val, val, val, val, val, val);
}
function vector4[] array_of_size16(vector4 val) {
	return array(val, val, val, val, val, val, val, val, val, val, val, val, val, val, val, val);
}

// ---------------------------
// matrix2[]

function matrix2[] array_of_size(int size; matrix2 val) {
	matrix2 res[] = {};
	resize(res, max(0, size));
	for (int i = 0; i < size; i++) {
		res[i] = val;
	}
	return res;
}
// a shorthand-overload:
function matrix2[] array_of_size(int size, is_identity) {
	matrix2 res[] = {};
	resize(res, max(0, size));
	if (is_identity) {
		matrix2 val = { // identity matrix
            {1, 0},
            {0, 1}
        };
		for (int i = 0; i < size; i++) {
			res[i] = val;
		}
	}
	return res;
}
// and a few edge-case funcs for common numbers:
function matrix2[] array_of_size2(matrix2 val) {
	return array(val, val);
}
function matrix2[] array_of_size3(matrix2 val) {
	return array(val, val, val);
}
function matrix2[] array_of_size4(matrix2 val) {
	return array(val, val, val, val);
}
function matrix2[] array_of_size9(matrix2 val) {
	return array(val, val, val, val, val, val, val, val, val);
}
function matrix2[] array_of_size16(matrix2 val) {
	return array(val, val, val, val, val, val, val, val, val, val, val, val, val, val, val, val);
}

// ---------------------------
// matrix3[]

function matrix3[] array_of_size(int size; matrix3 val) {
	matrix3 res[] = {};
	resize(res, max(0, size));
	for (int i = 0; i < size; i++) {
		res[i] = val;
	}
	return res;
}
// a shorthand-overload:
function matrix3[] array_of_size(int size, is_identity) {
	matrix3 res[] = {};
	resize(res, max(0, size));
	if (is_identity) {
		matrix3 val = { // identity matrix
            {1, 0, 0},
            {0, 1, 0},
            {0, 0, 1}
        };
		for (int i = 0; i < size; i++) {
			res[i] = val;
		}
	}
	return res;
}
// and a few edge-case funcs for common numbers:
function matrix3[] array_of_size2(matrix3 val) {
	return array(val, val);
}
function matrix3[] array_of_size3(matrix3 val) {
	return array(val, val, val);
}
function matrix3[] array_of_size4(matrix3 val) {
	return array(val, val, val, val);
}
function matrix3[] array_of_size9(matrix3 val) {
	return array(val, val, val, val, val, val, val, val, val);
}
function matrix3[] array_of_size16(matrix3 val) {
	return array(val, val, val, val, val, val, val, val, val, val, val, val, val, val, val, val);
}

// ---------------------------
// matrix[]

function matrix[] array_of_size(int size; matrix val) {
	matrix res[] = {};
	resize(res, max(0, size));
	for (int i = 0; i < size; i++) {
		res[i] = val;
	}
	return res;
}
// a shorthand-overload:
function matrix[] array_of_size(int size, is_identity) {
	matrix res[] = {};
	resize(res, max(0, size));
	if (is_identity) {
		matrix val = { // identity matrix
            {1, 0, 0, 0},
            {0, 1, 0, 0},
            {0, 0, 1, 0},
            {0, 0, 0, 1}
        };
		for (int i = 0; i < size; i++) {
			res[i] = val;
		}
	}
	return res;
}
// and a few edge-case funcs for common numbers:
function matrix[] array_of_size2(matrix val) {
	return array(val, val);
}
function matrix[] array_of_size3(matrix val) {
	return array(val, val, val);
}
function matrix[] array_of_size4(matrix val) {
	return array(val, val, val, val);
}
function matrix[] array_of_size9(matrix val) {
	return array(val, val, val, val, val, val, val, val, val);
}
function matrix[] array_of_size16(matrix val) {
	return array(val, val, val, val, val, val, val, val, val, val, val, val, val, val, val, val);
}

#endif
