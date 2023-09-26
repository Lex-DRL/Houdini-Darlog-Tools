#!/usr/bin/env python
# encoding: utf-8
__author__ = 'Lex Darlog (DRL)'

"""
Create a symlink: `python3.7libs` -> `python2.7libs` - to make the lib work both in Python 2 and 3 versions of Houdini.
"""

import os as _os
from os import path as _path
import errno as _errno

import ctypes as _ctypes
import sys as _sys

def win_require_admin_elevation():
	# https://stackoverflow.com/questions/130763/request-uac-elevation-from-within-a-python-script
	if _os.name != 'nt':
		return False
	try:
		return not _ctypes.windll.shell32.IsUserAnAdmin()
	except:
		return True


def rerun_as_admin():
	try:
		# Py2
		arg_runas = u'runas'
		exe = unicode(_sys.executable)
		argv = unicode(u' '.join(_sys.argv))
		py3 = False
	except Exception:
		# Py3
		arg_runas = 'runas'
		exe = _sys.executable
		argv = ' '.join(_sys.argv)
		py3 = True
	_ctypes.windll.shell32.ShellExecuteW(None, arg_runas, exe, argv, None, 1)
	


def main(symlink_name='python3.7libs', src_dir='python2.7libs'):
	print(
		"\nCreating a symlink: {} -> {}\n"
		"".format(repr(src_dir), repr(symlink_name))
	)
	
	dir_path = _path.dirname(_path.realpath(__file__))
	_os.chdir(dir_path)
	symlink_full_path = _path.join(dir_path, symlink_name)
	src_full_path = _path.join(dir_path, src_dir)
	if not _path.exists(src_full_path):
		raise OSError(_errno.ENOENT, None, src_full_path)
	if not _path.isdir(src_full_path):
		raise OSError(_errno.ENOTDIR, None, src_full_path)

	if _path.exists(symlink_full_path):
		if not _path.islink(symlink_full_path):
			raise OSError(_errno.EEXIST, None, symlink_full_path)
		
		# It exists but it's a symlink already
		print(
			"A symlink is already created: {}\n"
			"If you continue, it will be removed and recreated (only symlink itself, not files under it)."
			"".format(symlink_full_path)
		)
		user_input = None
		while user_input not in {'', 'y', 'Y', 'n', 'N'}:
			user_input = input("Recreate [Y] or exit [n]? >")
		if user_input in {'n', 'N'}:
			print("\nSymlink {} NOT created.".format(repr(symlink_name)))
			return
		
		_os.remove(symlink_full_path)
		print("Old symlink removed.")

	try:
		# Py3
		_os.symlink(src_dir, symlink_full_path, target_is_directory=True)
	except Exception:
		# Py2
		_os.symlink(src_dir, symlink_full_path)

	print("Symlink created:\n{}\n-> {}\n".format(symlink_full_path, src_dir))


def _run():
	import traceback as _traceback
	if win_require_admin_elevation():
		rerun_as_admin()
		return
	
	try:
		for d in (
			'python3.7libs',
			'python3.8libs',
			'python3.9libs',
			'python3.10libs',
		):
			main(d)
	except OSError as e:
		error_str = e.strerror
		error_str = '[ERROR {}] {}'.format(
			e.errno,
			error_str if error_str else _os.strerror(e.errno)
		)
		filename = e.filename
		if filename:
			error_str = '{}:\n{}'.format(error_str, filename)
		print(error_str)
	except Exception as e:
		print("".join(
			_traceback.format_exception(type(e), e, e.__traceback__)
		))
	input("Press Enter to exit...")


if __name__ == '__main__':
	_run()
