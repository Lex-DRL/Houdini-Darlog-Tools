# encoding: utf-8

from darlog_hou.pip import Pip as _Pip

pip = _Pip(upgrade=True, print_errors=True)
pip_called = False

try:
	import typing as _t
except ImportError:
	if pip.install('typing'):
		pip_called = True
