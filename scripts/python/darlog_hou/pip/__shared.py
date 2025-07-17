# encoding: utf-8

py2 = False
py3 = False
# noinspection PyBroadException
try:
	from itertools import izip_longest as _izip_longest
	_unicode = unicode
	_str_types = (str, unicode)
	py2 = True
except Exception:
	from itertools import zip_longest as _izip_longest
	_unicode = str
	_str_types = (str,)
	py3 = True


def safe_format(
	format_pattern,  # type: str
	*args,
	**kwargs
):
	"""For Py2, suppresses Unicode errors and tries to auto-convert a string pattern to unicode instead."""
	try:
		return format_pattern.format(*args, **kwargs)
	except UnicodeError:
		return _unicode(format_pattern).format(*args, **kwargs)


if py3:
	safe_format = str.format
