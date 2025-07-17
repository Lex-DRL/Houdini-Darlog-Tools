# encoding: utf-8
"""
Python code for `clickButton` rop node.
"""

__author__ = 'Lex Darlog (DRL)'

try:
	import typing as _t
except ImportError:
	pass

import hou

from darlog_hou.errors import get_error_message, any_exception


def main(asset_node):  # type: (hou.RopNode) -> None
	report_clicks = bool(asset_node.evalParm("report_clicks"))
	for parm in asset_node.parm("buttonParams_folder").multiParmInstances():
		button_path = parm.evalAsString()
		button = asset_node.parm(button_path)
		if button is None:
			print('{}: button not found: {}'.format(asset_node, button_path))
			continue
		if not isinstance(button.parmTemplate(), hou.ButtonParmTemplate):
			print('{}: not a button: {}'.format(asset_node, button_path))
			continue

		try:
			button.pressButton()
		except any_exception as e:
			tp = type(e).__name__
			msg = '<{}> error raised when attempted to click <{}> button on {}'.format(
				tp, button.name(), button.node().path()
			)

			e_msg = get_error_message(e)
			if e_msg:
				msg = '{}:\n{}'.format(msg, e_msg)

			print(msg)
			raise e

		if report_clicks:
			print(
					'Clicked <{}> button on {}'.format(button.name(), button.node().path())
			)
