##############################################################################
# Copyright (c) 2017,  Met Office, on behalf of HMSO and Queen's Printer
# For further details please refer to the file GPL/LICENCE which you
# should have received as part of this distribution.
##############################################################################

export ROOT_DIR ?= ../../

.PHONY: test
test: export GPL_DIR ?= $(ROOT_DIR)/GPL
test: export GPL_PYTHON_LIB ?= $(GPL_DIR)/lib/python
test: PYTHONPATH:=$(PYTHONPATH):./:$(GPL_PYTHON_LIB)
test:
	python2.7 -m unittest discover -p '*test.py'
