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

""" Backup file rotation script for backup files. See DESCRIPTION."""
import logging
import argparse
import sys
from dateutil.relativedelta import relativedelta

from .backup_rotation import BackupRotator, BackupRotationException
from .__version__ import __VERSION__

# Set up exit codes
EXIT_CODE_SUCCESS = 0

DESCRIPTION = '''
This script is designed to maintain a certain number of full backups
(This is NOT for differential or incremental backups)

Given a backup directory with subfolders for time buckets yearly, monthly,
and daily, the following will occur:
\t1.\tPromote files into the current time bucket from more granular time
\t\tbuckets if the modification time of the files are appropriately spaced
\t\t(e.g. for the yearly time bucket, if the file being processed is a year
\t\tlater than the most recent file in the yearly time bucket, it will be
\t\tpromoted)
\t2.\tDelete backups such that: There are at least three backups kept and no
\t\tbackups within three time units are delete (e.g. do not delete any files
\t\tless than 3 days old in the daily bucket, do not delete any files less
\t\tthan 3 months old in the monthly time bucket... etc.)
'''

LOG = logging.getLogger(__name__)

# Setup arguments
PARSER = argparse.ArgumentParser(
    prog=__package__,
    description=DESCRIPTION,
    formatter_class=argparse.RawTextHelpFormatter)
PARSER.add_argument(
    "backup_root",
    default="backups",
    help="The directory in which the yearly, monthly, and daily " \
         "time buckets reside.")
PARSER.add_argument(
    "pattern",
    default="*",
    help="The pattern (which you probably need to quote due to shell " \
         "expansion) of the files to be considered.")
PARSER.add_argument(
    '-d', '--dry-run',
    action="store_true",
    help="Makes this a dry run where no promotions or deletions occur.")
PARSER.add_argument(
    '-v', '--verbose',
    action="store_true",
    help="Turns on verbose logging")
PARSER.add_argument(
    '--version',
    action="version",
    version="%(prog)s " + __VERSION__)

# Configuration of our time buckets and their frequencies.
# Note: The time bucket names are also directory names in the backup_root
DEFAULT_TIME_BUCKETS = {
    "daily": {
        "num_files_to_keep": 3,
        "frequency": relativedelta(days=1, hour=0, minute=0, second=0)
    },
    "monthly": {
        "num_files_to_keep": 3,
        "frequency": relativedelta(months=1, day=0, hour=0, minute=0, second=0)
    },
    "yearly": {
        "num_files_to_keep": 3,
        "frequency": relativedelta(years=1, day=0, hour=0, minute=0, second=0)
    }
}


def rotate(argv):
    """ The main method of this application."""
    args = PARSER.parse_args(argv)

    if args.verbose:
        logging.basicConfig(format='%(levelname).1s: %(module)s:%(lineno)d: '
                                   '%(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname).1s: %(module)s:%(lineno)d: '
                                   '%(message)s', level=logging.WARNING)

    backup_rotator = BackupRotator(DEFAULT_TIME_BUCKETS.copy())
    if args.dry_run:
        backup_rotator.is_dry_run = True

    if args.backup_root:
        backup_rotator.backup_root = args.backup_root

    if args.pattern:
        backup_rotator.pattern = args.pattern

    backup_rotator.rotate_backups()
    return backup_rotator


def rotate_and_exit(argv=None):
    """ Wraps the main but actually handles exceptions and translates them
        into appropriate exit statuses. """

    if argv is None:
        argv = sys.argv[1:]

    try:
        rotate(argv)
    except BackupRotationException as ex:
        LOG.error(ex.message)
        sys.exit(ex.preferred_exit_code)
    LOG.info("Finished successful run.")
    sys.exit(EXIT_CODE_SUCCESS)
