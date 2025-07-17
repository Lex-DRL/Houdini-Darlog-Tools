# encoding: utf-8
import subprocess as _subprocess

from .__shared import safe_format as _format, _str_types, _unicode

try:
	import typing as _t

	# noinspection PyTypeHints,PyShadowingBuiltins
	_T = _t.TypeVar('T')
	_t_version = _t.Union[None, int, str]
except ImportError:
	pass


class Pip(object):
	def __init__(self, upgrade=True, print_errors=True):
		self.upgrade = upgrade
		self.print_errors = print_errors

		self.errors = ['']  # a simple hack to type-hint w/o importing typing
		self.errors.pop()

	def __repr__(self):
		arg_val_strings = (
			_format('{}={}', k, repr(v))
			for k, v in [
				('upgrade', self.upgrade),
				('print_errors', self.print_errors),
			]
		)
		return _format(
			'{}({})',
			self.__class__.__name__,
			', '.join(arg_val_strings)
		)

	__python_exe = None  # type: str

	@staticmethod
	def python_exe_path():  # type: () -> str
		hython_path = Pip.__python_exe
		if hython_path is not None:
			return hython_path

		import sys
		from os import path
		base_dir, main_exe = path.split(sys.executable)  # type: str
		hython_exe = 'hython.exe' if main_exe.lower().endswith('.exe') else 'hython'
		hython_path = path.join(base_dir, hython_exe)
		Pip.__python_exe = hython_path
		return hython_path

	def error_add(self, msg):  # type: (str) -> ...
		self.errors.append(msg)
		if self.print_errors:
			print(msg)

	def errors_joined(self, sep='\n'):  # type: (str) -> str
		if not isinstance(sep, _str_types):
			# noinspection PyBroadException
			try:
				sep = str(sep)
			except Exception:
				sep = _unicode(sep)
		return sep.join(self.errors)

	def errors_out_dict(self, key='error', sep='\n'):
		"""A dictionary with only a single key, which contains all the error messages joined."""
		return {key: self.errors_joined(sep=sep), }

	def _update_exception(self, e, format_pattern, cmd_args=None):  # type: (Exception, str, _t.List[str]) -> ...
		if not cmd_args:
			cmd_args = []
		old_err = e.message
		e.message = _format(
			format_pattern,
			old_err=old_err,
			cmd=' '.join((repr(x) if ' ' in x else x) for x in cmd_args),
		)
		self.error_add(e.message)
		e.args = tuple((e.message if isinstance(x, str) and x == old_err else x) for x in e.args)

	def _install_pip_itself(self):
		self.error_add("\n'pip' is not installed. Installing...")
		try:
			import ensurepip
		except ImportError as e:
			e.message = "Unable to install 'pip': missing internal module 'ensurepip'"
			self.error_add(e.message)
			e.args = (e.message,)
			raise e

		cmd_args = [self.python_exe_path(), '-m', 'ensurepip', '--upgrade']
		try:
			res = _subprocess.check_output(cmd_args)
		except Exception as e:
			self._update_exception(
				e, "Unable to install {{pip}}: {{ensurepip}} has run with error:\n{old_err}\nCommand: {cmd}", cmd_args
			)
			raise e
		self.error_add(res)
		self.error_add("\n'pip' module installed. Please, restart Houdini.\n")

	def install(
		self,
		*modules  # type: str
	):
		"""Returns boolean indicating whether there are some errors/messages."""
		if len(modules) == 1:
			modules = tuple(modules[0].split())
		if not modules:
			return False

		try:
			import pip
		except ImportError:
			self._install_pip_itself()
			return True

		cmd_args = [self.python_exe_path(), '-m', 'pip', 'install']
		if self.upgrade:
			cmd_args.append('-U')
			cmd_args.append('pip')
		cmd_args.extend(modules)
		try:
			res = _subprocess.check_output(cmd_args)
		except Exception as e:
			self._update_exception(
				e, "The command has run with error:\n{old_err}\nCommand: {cmd}", cmd_args
			)
			raise e
		self.error_add(res)
		self.error_add("\nModules installed. Please, restart Houdini.\n")
		return True
