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

""" The setuptools configuration for this project. """
import os

from setuptools import setup, find_packages

project_root = os.path.dirname(os.path.abspath(__file__))

def get_version():
    import importlib.machinery; 
    file_with_version = os.path.join(
            project_root, "src/main/python/backup_rotation/__version__.py")
    version = importlib.machinery.SourceFileLoader("ver", file_with_version).load_module().__VERSION__
    if not version:
        raise RuntimeError("Could not extract version string.")
    return version

def get_readme():
    with open(os.path.join(project_root, "README.md"), "r") as readme_raw:
        readme = readme_raw.read()
        return readme
    raise RuntimeError("Could not extract readme contents from README.md")

# TODO: Remove testing dependencies
setup(
    name="backup_rotation",
    version=get_version(),
    author="Christopher Prevoe",
    author_email="code@prevoe.com",
    license="MIT",
    description="Rotate full backup files in daily, monthly, and yearly folders",
    url="https://prevoe.com",
    platforms=['any'],
    long_description=get_readme(),
    package_dir={"": "src/main/python"},
    packages=find_packages(where="src/main/python"),
    scripts=["src/main/python/scripts/backup-rotation"],
    install_requires=[
        "python-dateutil==2.8.1",
    ],
    extras_require={
        "dev": [
            "behave>=1.2.6",
            "pylint>=2.6.0",
            "wheel>=0.35.1",
            "stdeb>=0.9.1",
            "coverage>=5.2.1"
        ]
    }
)
