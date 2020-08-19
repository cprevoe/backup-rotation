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

""" Module containing steps used to test the core the backup_rotation
    package """
import os
import logging
import re
import fnmatch
import json
import sys
import types
import unittest.mock
from os.path import join
from datetime import datetime
from importlib.machinery import SourceFileLoader
from dateutil.relativedelta import relativedelta
# pylint apparently has issues with star imports used in libraries. These
# names being imported are valid.
# pylint: disable=no-name-in-module
from behave import given, when, then

# Setup Logging
logging.basicConfig(level=logging.WARNING)
LOG = logging.getLogger(__name__)

# Pick a starting date. Test files will be created from this date and earlier.
start_date = datetime(2020, 6, 15)

# Configure our definition of yearly, monthly, and daily.
timedeltas = {
    "yearly":  relativedelta(years=1, day=0, hour=0, minute=0, second=0),
    "monthly": relativedelta(months=1, day=0, hour=0, minute=0, second=0),
    "daily":   relativedelta(days=1, hour=0, minute=0, second=0)
}


@given("{num} {bucket} {file_type} files")
def create_num_bucket_files(context, num, bucket, file_type, suffix=""):
    """ Creates a specified number of files in the bucket of choice, separated
        in creation time by that time bucket's timedelta """
    LOG.debug("Will create %s %s files in %s",
            num, bucket, context.backup_root)
    date_to_use = start_date
    for i in range(int(num)):
        date_to_use = date_to_use - timedeltas[bucket]
        full_filename = join(context.backup_root, bucket,
                             "%s.%s.%s.txt" % (i, suffix, file_type))
        open(full_filename, "a").close()
        os.utime(full_filename,
                 times=(date_to_use.timestamp(), date_to_use.timestamp()))
        context.created_files[bucket][file_type].append(
                {"mtime": date_to_use, "file": full_filename})
        LOG.debug("Created: %s", context.created_files[bucket][file_type][-1])

    assert True is not False


@given(u'{num} {bucket} {file_type} files with duplicates')
def create_num_bucket_backup_files_with_duplicates(
        context,
        num,
        bucket,
        file_type):
    """ Creates a specified number of files, and duplicates of those files. """
    for suffix in ["orig", "dup"]:
        create_num_bucket_files(context, num, bucket, file_type, suffix)


@when("the backup script is executed")
def execute_backup_script(context, entrypoint="external",
                          is_dry_run=False, is_verbose_mode=False):
    """ Actually executes the script we are testing """
    LOG.info("Will execute the backup script here")
    try:
        LOG.warning("Found: %s", context.backup_rotation)
        # Set up the arguments
        argv = []
        if is_dry_run:
            argv.append("-d")
        if is_verbose_mode:
            argv.append("-v")
        argv.append(context.backup_root)
        argv.append("*.backup.txt")
        # Execute the script
        if entrypoint == "external":
            modfile = "src/main/python/scripts/backup-rotation"
            loader = SourceFileLoader("__main__", modfile)
            rotator_runner = types.ModuleType(loader.name)
            argv = ["backup-rotation"] + argv
            with unittest.mock.patch.object(sys, 'argv', argv):
                loader.exec_module(rotator_runner)
        elif entrypoint == "internal":
            context.backup_rotation.rotate(argv)

    except context.backup_rotation.BackupRotationException as ex:
        context.caught_exception = ex
    except SystemExit as ex:
        context.caught_exception = ex


@when("the backup script is executed in a dry-run")
def execute_backup_script_dry_run(context):
    """ Executes the script with the dry-run argument. """
    execute_backup_script(context, is_dry_run=True)


@when("the backup script is executed with verbose mode")
def execute_backup_script_verbose_mode(context):
    """ Executes the script with the verbose mode argument. """
    execute_backup_script(context, is_verbose_mode=True)

@when("the backup script is executed internally")
def execute_backup_script_internally(context):
    """ Executes the backup script using the module which exposes
        exceptions"""
    execute_backup_script(context, entrypoint="internal")


def json_defaults(item_to_convert):
    """ convenience method used during json.dumps for non-json serializable
    items."""
    return "%s" % item_to_convert


def get_files_of_type(context, bucket, file_type):
    """ Retrieves a list of dicts where each item documents one file of the
    type specified in the bucket specified."""
    found_files = []
    pattern = fnmatch.translate("*.%s.txt" % file_type)
    for _, _, files in os.walk(join(context.backup_root, bucket)):
        for file_candidate in files:
            if re.match(pattern, file_candidate):
                filename = join(context.backup_root, bucket, file_candidate)
                found_files.append({
                    "file": filename,
                    "mtime": datetime.fromtimestamp(
                        os.path.getmtime(filename))})
    return found_files


@then("Only the most recent {bucket} {file_type} file remains")
@then("Only the {num} most recent {bucket} {file_type} files remain")
def only_the_n_most_recent_bucket_backups_remain(
        context,
        bucket,
        file_type,
        num=1):
    """ Verifies that only the most recent n files exist in the bucket
        specified. """
    found_files = get_files_of_type(context, bucket, file_type)
    correct_file_count = len(found_files) == int(num)
    if not correct_file_count:
        LOG.debug("Found files: %s", json.dumps(found_files,
                                                indent=4,
                                                default=json_defaults))
    assert correct_file_count, "Found %s files in the bucket, expected %s" % \
                               (len(found_files), int(num))

    # Sorted reverse by modification time implies most recent files first.
    sorted_files = sorted(found_files, reverse=True,
                                key=lambda x: x["mtime"])
    LOG.debug("Sorted found files: %s",
              (json.dumps(sorted_files, indent=4, default=json_defaults)))

    # To know if it's a recent file (maybe fuzzy on the "most" recent file)
    # look at the date of the newest file and ensure that it's within one
    # timedelta unit of the start date. Then ensure each file beyond is
    # within one time delta of that.
    latest_acceptable_date = start_date
    for i in range(int(num)):
        file_being_checked = sorted_files[i]
        LOG.debug("Considering file number %s / %s", i, num)
        earliest_acceptable_date = latest_acceptable_date - timedeltas[bucket]
        file_mtime = file_being_checked["mtime"]
        within_acceptable_range = \
            (earliest_acceptable_date <= file_mtime <= latest_acceptable_date)
        # This is a test file and the arguments are being passed to an
        # assertion message. IMHO, pylint's warning here adds no value.
        # pylint: disable=E1305
        assert within_acceptable_range, \
            "The file %s modification date %s does not fall between " + \
            "the expected range of %s to %s." % (
                    file_being_checked["file"],
                    file_mtime,
                    earliest_acceptable_date,
                    latest_acceptable_date)
        latest_acceptable_date = file_mtime
    LOG.debug("Done scanning")


@then(u'the oldest {bucket} {file_type} file remains')
def oldest_bucket_filetype_file_remains(context, bucket, file_type):
    """ Validates that the oldest file in the bucket specified remains. """
    sorted_files_in_bucket = \
        sorted(context.created_files[bucket][file_type],
               key=lambda x: x["mtime"])
    LOG.info("Expecting %s to exist", sorted_files_in_bucket[0]["file"])
    assert os.path.exists(sorted_files_in_bucket[0]["file"])


@then(u'all {bucket} {file_type} files remain')
def all_filetype_files_remain(context, bucket, file_type):
    """ Validates that all of the files of test files of the type remain in
        the bucket specified. """
    for file_details in sorted(context.created_files[bucket][file_type], key=lambda x: x["mtime"]):
        assert os.path.exists(file_details["file"])


@then(u'the {bucket} {file_type} files are a {time_unit} apart')
def the_bucket_filetype_files_are_unit_apart(context, bucket, file_type, time_unit):
    """ Validates that the modification times of the files in a given bucket
        appropriately spaced for those buckets."""
    time_unit_to_time_delta = {
      "year": "yearly",
      "month": "monthly",
      "day": "daily"
    }
    desired_time_delta = timedeltas[time_unit_to_time_delta[time_unit]]
    found_files = get_files_of_type(context, bucket, file_type)
    found_file_times = map(lambda x: x["mtime"], found_files)
    last_visited = None
    for time in sorted(found_file_times, reverse=True):
        assert last_visited is None or \
               ((last_visited + desired_time_delta) < time)


@given(u'the backup root does not exist')
def backup_root_does_not_exist(context):
    """ Ensures that the backup root for this scenario does not exist. """
    context.backup_root = "%s/this_dir_does_not_exist" % context.backup_root


@then(u'a BackupRootFolderMissingException should have been raised')
def backup_root_folder_missing_exception_was_raised(context):
    """ Asserts that the BackupRootFolderMissingException was raised. """
    assert isinstance(context.caught_exception,
                      context.backup_rotation.BackupRootFolderMissingException)


@given(u"the {time_bucket} backup folder is removed")
def time_bucket_folder_is_removed(context, time_bucket):
    """ Removes the time bucket folder for the scenario. """
    os.rmdir(os.path.join(context.backup_root, time_bucket))


@then(u'there are is no {time_bucket} backup folder')
def time_bucket_folder_is_missing(context, time_bucket):
    """ Asserts that the time bucket folder specified does not exist. """
    assert os.path.exists(os.path.join(context.backup_root, time_bucket))

@then(u'the script should exit with status {expected_exit_code}')
def exit_code_should_be(context, expected_exit_code):
    """ Validates that the exit code is as expected """
    assert isinstance(context.caught_exception, SystemExit)
    assert int(context.caught_exception.code) == int(expected_exit_code), \
          "Found exit code %s but expected %s" % (
              context.caught_exception.code, \
              expected_exit_code)
