// Mozilla Public License 2.0
// 
// Copyright (c) 2020 Lex Darlog (aka DRL)
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.


#ifndef __darlog_attrib_type_str_lib__
#define __darlog_attrib_type_str_lib__

// #include "attrib_type_str.h"

// Turns attribute's type-id (the value returned by attribtype() and its class-specific variants)
// and size into a readable string.


function string attrib_type_str(int type_id, size) {
    string names[] = {"integer", "float", "string", "integers-array", "floats-array", "strings-array", "dictionary", "dictionaries-array"};
    if (type_id < 0 || type_id > 7) {
        return "unknown";
    }
    if (type_id == 1 && size > 1) {
        return sprintf("vector%d", size);
    }
    if (type_id == 4 && size > 1) {
        return sprintf("vector%d-array", size);
    }
    return names[type_id];
}

function string attrib_type_Capital_str(int type_id, size) {
    string names[] = {"Integer", "Float", "String", "Integers-array", "Floats-array", "Strings-array", "Dictionary", "Dictionaries-array"};
    if (type_id < 0 || type_id > 7) {
        return "Unknown";
    }
    if (type_id == 1 && size > 1) {
        return sprintf("Vector%d", size);
    }
    if (type_id == 4 && size > 1) {
        return sprintf("Vector%d-array", size);
    }
    return names[type_id];
}

#endif
