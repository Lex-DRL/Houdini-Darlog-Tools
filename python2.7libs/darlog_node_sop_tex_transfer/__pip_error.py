# encoding: utf-8

from json import dumps

from .__pip_requirements import pip


class InputProcessor:
	def __init__(self, *args, **kwargs):
		pass

	def main(self):
		return dumps(pip.errors_out_dict(), indent=2)
