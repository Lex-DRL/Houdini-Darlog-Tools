# encoding: utf-8
"""
Python code for `forceCook` rop node.
"""

__author__ = 'Lex Darlog (DRL)'

try:
	import typing as _t
except ImportError:
	pass

import hou

from darlog_hou.errors import get_error_message, any_exception


def main(asset_node):  # type: (hou.RopNode) -> None
	report_cooks = bool(asset_node.evalParm("report_cooks"))
	report_wrong_paths = bool(asset_node.evalParm("report_wrong_paths"))
	all_params = asset_node.parm("nodes_folder").multiParmInstances()  # type: _t.Tuple[hou.Parm, ...]
	for parm in all_params:
		node_path = parm.evalAsString()
		if not node_path:
			continue

		try:
			node = parm.evalAsNode()  # type: hou.Node
		except any_exception:
			if report_wrong_paths:
				print('{}: node not found: {}'.format(asset_node, node_path))
			continue

		if not isinstance(node, hou.Node):
			if report_wrong_paths:
				print('{}: not a node: {}'.format(asset_node, repr(node_path if node is None else node)))
			continue

		try:
			node.cook(force=True)
		except any_exception as e:
			tp = type(e).__name__
			msg = '<{}> error raised when attempted to cook node {}'.format(
				tp, repr(node)
			)

			e_msg = get_error_message(e)
			if e_msg:
				msg = '{}:\n{}'.format(msg, e_msg)

			print(msg)
			raise e

		if report_cooks:
			print('Cooked node: {}'.format(repr(node)))
