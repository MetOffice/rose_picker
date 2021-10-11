##############################################################################
# (C) British Crown Copyright 2021 Met Office.
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

.PHONY: test
test:
	@module use /data/users/lfric/modules/modulefiles.rhel7; \
	module load environment/lfric/intel; \
	echo Styling...; \
	echo "Running pylint"; \
	pylint *.py ; \
	echo "Running pycodestyle"; \
	pycodestyle .; \
	echo Testing... ; \
	python -m pytest -vv tests/

.PHONY: style
style:
	@module use /data/users/lfric/modules/modulefiles.rhel7; \
	module load environment/lfric/intel; \
    echo "Running pylint"; \
	pylint *.py ; \
	echo "Running pycodestyle"; \
	pycodestyle .;
