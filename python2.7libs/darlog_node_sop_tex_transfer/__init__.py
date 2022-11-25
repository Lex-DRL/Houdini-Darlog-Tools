# encoding: utf-8
__author__ = 'Lex Darlog (DRL)'

from . import __pip_requirements as _pip_req

if _pip_req.pip_called:
	from .__pip_error import InputProcessor
else:
	from .__main import InputProcessor
