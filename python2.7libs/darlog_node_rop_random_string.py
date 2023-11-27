# encoding: utf-8
"""
Python code for `randomString` rop node.
"""

__author__ = 'Lex Darlog (DRL)'

try:
	import typing as _t
except ImportError:
	pass

from string import digits, ascii_lowercase, ascii_uppercase, ascii_letters
from random import choices

import hou

digits_no_similar = '23456789'
lowercase_no_similar = 'abcdefghijkmnopqrstuvwxyz'
uppercase_no_similar = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
letters_no_similar = lowercase_no_similar + uppercase_no_similar

_char_sets = {
	# exclude_confusing, digits, lower, upper

	(True, True, True, True): digits_no_similar + letters_no_similar,
	(True, True, True, False): digits_no_similar + lowercase_no_similar,
	(True, True, False, True): digits_no_similar + uppercase_no_similar,
	(True, True, False, False): digits_no_similar,
	(True, False, True, True): letters_no_similar,
	(True, False, True, False): lowercase_no_similar,
	(True, False, False, True): uppercase_no_similar,
	(True, False, False, False): "",

	(False, True, True, True): digits + ascii_letters,
	(False, True, True, False): digits + ascii_lowercase,
	(False, True, False, True): digits + ascii_uppercase,
	(False, True, False, False): digits,
	(False, False, True, True): ascii_letters,
	(False, False, True, False): ascii_lowercase,
	(False, False, False, True): ascii_uppercase,
	(False, False, False, False): "",
}


def _detect_char_set(asset_node):  # type: (hou.RopNode) -> str
	"""Get a set of valid characters for the current state of node settings."""
	exclude_confusing = bool(asset_node.evalParm("excludeConfusing_do"))
	digits_do = bool(asset_node.evalParm("digits_do"))
	lower_do = bool(asset_node.evalParm("charLower_do"))
	upper_do = bool(asset_node.evalParm("charUpper_do"))
	return _char_sets[(exclude_confusing, digits_do, lower_do, upper_do)]


def _get_length(asset_node):  # type: (hou.RopNode) -> int
	length = asset_node.evalParm("length")  # type: int
	return max(1, length)


def _set_value(asset_node, value):  # type: (hou.RopNode, str) -> None
	"""We store the value not on any parameter, but within userData. This function sets it."""
	out_node = asset_node.node("./STORAGE")  # type: hou.RopNode
	out_node.setCachedUserData("random_string", value)
	out_node.cook(force=True)


def main(asset_node):  # type: (hou.RopNode) -> None
	"""The main function executed on ROP render."""
	length = _get_length(asset_node)
	char_set = _detect_char_set(asset_node)

	random_str = ''
	if char_set:
		random_seq = choices(char_set, k=length)
		random_str = ''.join(random_seq)

	_set_value(asset_node, random_str)


_manual_input_window_args = dict(
	message="Enter new value",
	help=(
		"Any disallowed characters will be stripped.\n\nValue won't be set changed if:"
		"\n  - empty input is provided"
		"\n  - window is closed (Esc)"
	),
	title='Manual input'
)


def _valid_chars_gen(asset_node, value_str):  # type: (hou.RopNode, str) -> ...
	"""Takes a string, iterates only over those characters which comply to the current char-set options."""
	char_set_str = _detect_char_set(asset_node)
	if not char_set_str:
		return

	char_set = set(char_set_str)

	for char in value_str:
		if char not in char_set:
			continue
		yield char


def set_manually(asset_node):  # type: (hou.RopNode) -> None
	"""Callback function to run when `set_manually` button is pressed."""
	_, value_str = hou.ui.readInput(**_manual_input_window_args)  # type: (int, str)
	value_str = value_str.strip()
	if not value_str:
		return

	value_str = ''.join(_valid_chars_gen(asset_node, value_str))
	if not value_str:
		return

	_set_value(asset_node, value_str)
