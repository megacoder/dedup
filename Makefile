all::

rpm::	setup.py
	python setup.py bdist_rpm

clean::
	${RM} -r build

distclean clobber:: clean
	${RM} -r dist
