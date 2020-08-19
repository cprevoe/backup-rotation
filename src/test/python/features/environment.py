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

""" Environment file which creates the tests directories before all of our
    cucumber tests. """
import logging
import tempfile
import os
import backup_rotation as br

# Load the script we're testing

def before_scenario(context, _):
    """ Creates a new temporary directory and creates the time buckets within
        for each scenario run. """
    context.backup_rotation = br
    context.backup_root_raw = tempfile.TemporaryDirectory()
    context.backup_root = context.backup_root_raw.name
    context.created_files = {}

    logging.info("Creating %s" , context.backup_root)

    for bucket in ["yearly", "monthly", "daily"]:
        os.mkdir(os.path.join(context.backup_root, bucket))
        context.created_files[bucket] = {"backup": [], "miscellaneous": []}

def after_scenario(context, _):
    """ Cleans up the temporary directories created during the tests. """
    context.backup_root_raw.cleanup()
