# encoding: utf-8
"""
"""

from darlog_hou.pip import verify_version as _verify

__min_version = (1, 2, 0)
__installed_version = None

__import_error = None

_package_name = 'darlog-py23'

try:
	from darlog import py23 as __py23
	from darlog.py23 import *

	__installed_version = __py23.__version_info__

	if not _verify(__installed_version, min_version=__min_version):
		msg = "Installed version {} is below required {}. Upgrading {} package...".format(
			__installed_version,
			__min_version,
			_package_name
		)
		print(msg)
		raise ImportError(msg)
except ImportError:
	from darlog_hou.pip import Pip as _Pip

	_pip = _Pip(upgrade=True, print_errors=True)
	if _pip.install(_package_name):
		__import_error = ImportError(_pip.errors_joined())
	else:
		__import_error = ImportError(
			"Weird error when attempting to install {}:\n"
			"the module isn't installed but 'pip' thinks there's no need to install it.".format(repr(_package_name))
		)

if __import_error is not None:
	raise __import_error
