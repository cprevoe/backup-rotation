#
# Copyright (c) 2020 Christopher Prevoe
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

.PHONY: default build clean
VENV := venv
SRC_ROOT := src/main/python
TEST_ROOT := src/test/python

default: .make.artifact

clean:
	rm -rf .make.venv .make.test .make.artifact .make.artifact_name venv target build deb_dist dist

.make.venv: pyproject.toml
	python3 -m venv ${VENV}
	# pyproject.toml support is NOT in pip 9.0.1, so we upgrade it first.
	venv/bin/pip3 install --upgrade pip setuptools
	venv/bin/pip3 install -e '.[dev]'
	touch .make.venv

.make.test: .make.venv ${SRC_ROOT}/*/*.py ${TEST_ROOT}/features/*.feature ${TEST_ROOT}/features/steps/*.py
	@echo
	@echo ================================================================================
	@echo Running tests
	@echo ================================================================================
	${VENV}/bin/coverage run -m behave ${TEST_ROOT}/features
	${VENV}/bin/coverage report --fail-under 100.0 
	@echo
	@echo ================================================================================
	@echo Running pylint
	@echo ================================================================================
	((find ${SRC_ROOT} ${TEST_ROOT} -name "*.py"; ls -1d ${SRC_ROOT}/scripts/*) | grep -v __pycache__) | xargs ${VENV}/bin/pylint
	@echo ================================================================================
	@echo
	@echo Tests and linting completed successfully.
	touch .make.test

.make.artifact: .make.test
	@echo ================================================================================
	@echo Building Packages
	@echo ================================================================================
	venv/bin/python3 setup.py --command-packages=stdeb.command bdist_deb
	touch .make.artifact
