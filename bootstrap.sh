#!/bin/sh
if [ -x /bin/python3 ]; then
	PYTHON=/bin/python3
else
	PYTHON=/bin/python
fi
if [ $# -eq 0 ]; then
	set -- bztar gztar rpm
fi
rm -rf build dist
(
	for PKG in "${@}"; do
		${PYTHON} ./setup.py bdist --format="${PKG}"
	done
) 2>&1 | tee build.log
