##############################################################################
# (C) British Crown Copyright 2018 Met Office.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Rose. If not, see <http://www.gnu.org/licenses/>.
##############################################################################

ROOT_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

Q ?= @

export PYTHONPATH:=$(PYTHONPATH):$(ROOT_DIR)../lib/python:$(ROOT_DIR)

.PHONY: style
style: type
	$Qecho Styling...
	$Qpylint $(ROOT_DIR)rose_picker*
	$Qpycodestyle $(ROOT_DIR)

.PHONY: type
type: test
	$Qecho Typing...
	$Qmypy $(ROOT_DIR)

.PHONY: test
test:
	$Qecho Testing...
	$Qpython -m pytest $(ROOT_DIR)
