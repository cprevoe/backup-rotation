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

Feature: Backup Rotation
  Scenario: Only three backup files remain
     Given 10 yearly backup files
      When the backup script is executed internally
      Then only the 3 most recent yearly backup files remain

  Scenario: Monthly promotion to yearly
     Given 13 monthly backup files
      When the backup script is executed
      Then only the 3 most recent monthly backup files remain
       And only the 2 most recent yearly backup files remain
       And the yearly backup files are a year apart

  Scenario: Daily promotion to monthly and yearly
     Given 364 daily backup files
      When the backup script is executed
      Then only the 3 most recent daily backup files remain
       And only the 3 most recent monthly backup files remain
       And only the most recent yearly backup file remains

  Scenario: Verbose mode daily promotion to monthly and yearly
     Given 364 daily backup files
      When the backup script is executed with verbose mode
      Then only the 3 most recent daily backup files remain
       And only the 3 most recent monthly backup files remain
       And only the most recent yearly backup file remains

  Scenario: Daily promotion to yearly when monthly is missing
     Given 364 daily backup files
       And the monthly backup folder is removed
      When the backup script is executed
      Then only the 3 most recent daily backup files remain
       And only the most recent yearly backup file remains
       And there are is no monthly backup folder

  Scenario: Daily promotion to monthly and yearly
    # There are 365 days in a year, thus 366 is the second year... unless it's a leap year.
    # Chosen 2 days over 365 due to leap years.
     Given 367 daily backup files
      When the backup script is executed
      Then only the 3 most recent daily backup files remain
       And only the 3 most recent monthly backup files remain
       And only the 2 most recent yearly backup files remain

  Scenario: Dry-run does not result in any files modified
     Given 30 daily backup files
      When the backup script is executed in a dry-run
      Then only the 30 most recent daily backup files remain

  Scenario: Only the backup files are affected
     Given 5 daily backup files
       And 4 daily miscellaneous files
      When the backup script is executed
      Then all daily miscellaneous files remain

  Scenario: Extra files do not result in extra promotions
     Given 60 daily backup files with duplicates
      When the backup script is executed
      Then only the 2 most recent monthly backup files remain
      # Files strictly less than 3 days old (3 daily units) should be kept.
      # 3 days * 2 duplicates - 1 file which is not resurrected = 5.
       And only the 5 most recent daily backup files remain

  Scenario: When the backup root folder is missing, the application should exit.
     Given the backup root does not exist
      When the backup script is executed
      Then the script should exit with status 100
