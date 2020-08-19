# Backup Rotation Script
This is a simple backup rotation script which will scan a directory for files
which match a pattern provided, then determine if each file should be kept, 
promoted, or deleted. The result of this script is that each directory 
representing a time unit (yearly, monthly, or daily) will each end up with the
three most recent backups.

Note: This is NOT an incremental backup script and is only really useful for 
full-backup files. This script doesn't generate backups itself.

# IMPORTANT
THIS PROJECT WILL DELETE FILES IN THE DIRECTORIES WHICH YOU 
SPECIFY. INCORRECT USE *WILL* RESULT IN DATALOSS. 

While tested and while a best effort was made for safety, it is strongly
recommended that you test your use case before using this software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

# Installation
I recommend installing the resulting deb file. You may also use any of the
standard setuptools means to install.

# How to use
Once the backup\_rotation package is installed on your local machine and the
backup-rotation script is installed in your path, simply run 
the command `backup-rotation -h` to view the help.

## Example use:
Given a directories /srv/backups, /srv/backups/yearly, /srv/backups/monthly,
and /srv/backups/daily, which contain backups in "*.tgz" format, then the
following may be used to execute this script:
```
backup-rotation /srv/backups '*.tgz'
```
Note: The quotations around the pattern are crucial. If the shell interprets
      the pattern, then this script will not run correctly.

## Setup for development
This project requires python3 (3.6 or higher) and uses a makefile to generate
the appropriate virtual env with all of it's required packages for 
development. Simply run `make` and the project and tools will install and 
run locally.

## Project Structure
The project structure is fairly simple. The root directory contains any
project build configurations necessary such as makefiles, project.toml,
setup.py, etc.

The source directory is broken down into src/main for code expected to run at
runtime, and src/test for code used to validate runtime code. Afterwords, the
technology is used. So src/main/python will contain all python related scripts
where as src/main/docker will contain any docker related files (to be added).
