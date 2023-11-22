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
from darlog_hou.filesystem import empty_dir
from darlog_hou.selection import keep_selection


def clear_tmp_dir(asset_node):  # type: (hou.RopNode) -> None
	"""Remove EVERYTHING within a temp directory dedicated to this asset type."""
	asset_tmp_dir = asset_node.evalParm("./PARAMS/assetType_tmpDir")
	empty_dir(asset_tmp_dir)


@keep_selection
def copy_labs_vat_node(asset_node):  # type: (hou.RopNode) -> None
	"""
	Fucking juniors are working in Labs!
	They made the node in such a way that it CANNOT be rendered when it's embedded into some other asset... like this one.

	So, to do as simple thing as rendering with it, we need to copy it into an unlocked subnetwork prior tom that.
	"""
	template_node = asset_node.node("./LabsVAT_template_container/ropnet/LabsVAT")  # type: hou.RopNode
	tmp_container_node = asset_node.node("./UNLOCKED_TMP_container/ropnet")  # type: hou.RopNode

	for leftover_child in tmp_container_node.children():
		leftover_child.destroy()

	template_node.copyTo(tmp_container_node)








def main():
	asset_node = hou.node("..")
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
