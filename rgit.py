#!/usr/bin/env python

# @desc     Recursive git. This is simple python script 
# to execute git pull/push and fetch recursively
# on multiple repositories
#
# @author   Dariusz Ostolski

import sys
import os
import logging
import argparse
import shlex
import subprocess

parser = argparse.ArgumentParser(description="rgit execute git commands recursively")
parser.add_argument('-v', '--verbose', action="store_true", default=False)
parser.add_argument("-d", "--dir",
                    dest="dirname",
                    action="store",
                    help="The directory to scan sub dirs from. The default is current working directory",
                    default=os.path.abspath("./"))

parser.add_argument("-r", "--remote",
                    action="store",
                    dest="remote",
                    default="",
                    help="Set the remote name (remotename:branchname)")

subparsers = parser.add_subparsers(title='Action', dest='action',
                                   description='git action to execute: pull, push, fetch, status',
                                   help='git action to execute recursively')

pull_parser = subparsers.add_parser('pull')
pull_parser.add_argument("--all", dest='all', action='store_true', default=False
                         , help='Fetch all remotes.')
pull_parser.add_argument('-r', '--rebase', dest='rebase', choices=['false', 'true', 'preserve']
                         , help="""When true, rebase the current branch on top of the upstream branch after fetching.
If there is a remote-tracking branch corresponding to the upstream branch and the upstream branch was rebased since last
fetched, the rebase uses that information to avoid rebasing non-local changes.\n\n
When preserve, also rebase the current branch on top of the upstream branch, but pass --preserve-merges along to git
rebase so that locally created merge commits will not be flattened.\n\n
When false, merge the current branch into the upstream branch.\n\n

See pull.rebase, branch.<name>.rebase and branch.autosetuprebase in git-config(1) if you want to make git pull always
use --rebase instead of merging.\n\n
\tNote
\tThis is a potentially dangerous mode of operation. It rewrites history, which does not bode well when you published that history
\talready. Do not use this option unless you have read git-rebase(1) carefully.""")

subparsers.add_parser('push')
subparsers.add_parser('fetch')
status_parser = subparsers.add_parser('status')
status_parser.add_argument('-s', '--summary', dest='summary', action="store_true"
                           , default=False
                           , help='Display summary for each subdirectory')
parser.add_argument("--dry-run",
                    action="store_true",
                    dest="dry",
                    default=False,
                    help="Don't execute anything actually. Just display executed commands")

"""
http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
"""
HEADER = '-- Starting rgit...'


class ColorFormatter(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def __init__(self):
        pass

    def normal(self, str):
        return str

    def header(self, str):
        return self._format_impl(self.HEADER, str)

    def info(self, str):
        return self._format_impl(self.OKGREEN, str)

    def info_darker(self, str):
        return self._format_impl(self.OKBLUE, str)

    def warning(self, str):
        return self._format_impl(self.WARNING, str)

    def fail(self, str):
        return self._format_impl(self.FAIL, str)

    def _format_impl(self, color, str):
        return '{0}{1}{2}'.format(color, str, self.ENDC)

    def println(self, str):
        sys.stdout.write("{0}\n".format(str))
        return self

    def print_header(self, header):
        self.println(self.header(header))
        return self


class Action(object):
    def __init__(self, action, remote, executor):
        self._remote = remote
        self._action = action
        self._executor = executor

    def execute(self, directory):
        return self._executor.getoutput(directory, self.get_command())

    def get(self):
        return "({0})".format(self._action)

    def safe(self):
        return self._action == 'fetch'

    def get_command(self):
        return "git {0} {1}".format(self._action, self.get_options()) + ' '.join(self._remote.split(":"))

    def get_options(self):
        return ''

class StatusResult(object):
    def __init__(self):
        self._modified_staged = []
        self._modified_unstaged = []
        self._untracked = []
        self._deleted_staged = []
        self._branch = None
        self._branch_remote = None
        self._ahead = 0
        self._behind = 0

    @property
    def branch(self):
        return self._branch

    @branch.setter
    def branch(self, branch):
        self._branch = branch

    @property
    def branch_remote(self):
        return self._branch_remote

    @branch_remote.setter
    def branch_remote(self, remote):
        self._branch_remote = remote

    @property
    def ahead(self):
        return self._ahead

    @ahead.setter
    def ahead(self, ahead):
        self._ahead = ahead

    @property
    def behind(self):
        return self._behind

    @behind.setter
    def behind(self, behind):
        self._behind = behind


class StatusParser(object):
    def __init__(self):
        pass

    def parse(self, output):
        result = StatusResult()
        lines = output.splitlines()
        if lines[0].startswith('##'):
            result.branch, result.branch_remote, result.ahead, result.behind = self._parse_branch(lines[0])
            lines = lines[1:]

        for line in lines:
            self._parse_line(line)
        return result

    def _parse_line(self, line):
        pass

    def _parse_branch(self, line):
        branch = None
        branch_remote = None
        ahead = 0
        behind = 0
        if line is None or not line.startswith('##'):
            return branch, branch_remote, ahead, behind
        #skip '## '
        line = line.strip()
        line = line[2:]
        tokens = line.split('[')
        branch_str = tokens[0]
        if len(tokens)==2:
            ahead, behind = self._parse_ahead_behind(tokens[1])
        branch, branch_remote = self._parse_branch_str(branch_str)
        return branch, branch_remote, ahead, behind

    def _parse_ahead_behind(self, line):
        line = line.strip('[]')
        lines = line.split(',')
        ahead = 0
        behind = 0
        for line in lines:
            line = line.strip()
            if line.startswith('ahead'):
                ahead = int(line.split()[1])
            if line.startswith('behind'):
                behind = int(line.split()[1])
        return ahead, behind

    def _parse_branch_str(self, branch_str):
        branch_str = branch_str.strip()
        branch = None
        remote = None
        if branch_str == 'HEAD (no branch)':
            branch = 'detached'
        else:
            branches = branch_str.split('...')
            branch = branches[0]
            if len(branches)==2:
                remote = branches[1]
        return branch, remote



class PullAction(Action):
    def __init__(self, remote, executor, options):
        Action.__init__(self, 'pull', remote, executor)
        self._options = options


    def get_options(self):
        options = ''
        if self._options.all:
            options = '--all'
        if self._options.rebase:
            options += ' --rebase={0}'.format(self._options.rebase)
        return options


class StatusAction(Action):
    def __init__(self, remote, executor, summary=False):
        """

        :param remote:
        :param executor:
        :param summary:
        """
        Action.__init__(self, 'status', remote, executor)
        self._summary = summary

    def execute(self, directory):
        out = Action.execute(self, directory)
        if self._summary:
            out = ''
        return out

    def safe(self):
        return True


class DryRunExecutor:
    def __init__(self):
        pass

    def getoutput(self, directory, command):
        logging.warning("Executing: %s in %s", command, directory)
        if command.find('git status') != -1:
            return """On branch master
Your branch is up-to-date with 'origin/master'.

nothing to commit, working directory clean"""
        return ""


class SubprocessExecutor:
    def __init__(self):
        pass

    def get_output(self, directory, command):
        logging.debug("Executing: %s in %s", command, directory)
        args = shlex.split(command)
        git_process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=directory)
        stdout, stderr = git_process.communicate()
        return stdout


ON_BRANCH = 'On branch'


def get_dir_status(dirname, executor):
    return StatusAction('', executor).execute(dirname)


def get_branch(out):
    branch_begin = out.find(ON_BRANCH)
    branch_end = out.find('\n', branch_begin)
    return out[branch_begin + len(ON_BRANCH) + 1:branch_end]


def execute(dirname, action, executor, formatter):
    out = get_dir_status(dirname, executor)
    logging.debug(out)
    branch = get_branch(out)

    no_changes = (-1 != out.find('nothing'))
    safe_to_execute_action = (action is not None and (action.safe() or no_changes))

    if no_changes:
        result = formatter.info("No Changes")
    else:
        result = formatter.fail("Changes")

    # Execute requested action
    if safe_to_execute_action:
        command_result = action.execute(dirname)
        result = result + " {0} \n".format(action.get()) + command_result

    formatter.println("-- " + formatter.info_darker(dirname.ljust(55)) + branch + " : " + result)


def scan(dirname, action, executor, formatter):
    full_path = os.path.join(dirname, '.git')
    if os.path.exists(full_path) and os.path.isdir(full_path):
        logging.info("Found git directory in: %s", dirname)
        execute(dirname, action, executor, formatter)
    else:
        for f in os.listdir(dirname):
            full_path = os.path.join(dirname, f)
            if os.path.isdir(full_path):
                logging.debug("Entering directory: %s", full_path)
                scan(full_path, action, executor, formatter)


def main_impl(argv):
    options = parser.parse_args(argv)
    os.environ['LANGUAGE'] = 'en_US:en'
    os.environ['LANG'] = 'en_US.UTF-8'
    formatter = ColorFormatter()
    verbosity = logging.WARNING
    if options.verbose:
        verbosity = logging.DEBUG
    executor = SubprocessExecutor()
    if options.dry:
        executor = DryRunExecutor()
    action = None
    if options.action == 'pull':
        action = PullAction(options.remote, executor, options)
    if options.action == 'push':
        action = Action("push", options.remote, executor)
    if options.action == 'fetch':
        action = Action("fetch", options.remote, executor)
    if options.action == 'status':
        action = StatusAction(options.remote, executor, options.summary)
    dirname = os.path.abspath(options.dirname)
    logging.basicConfig(format='[%(levelname)s]: %(message)s', level=verbosity)
    logging.debug("Options %s", options)
    formatter.print_header(HEADER)
    formatter.println("Scanning sub directories of {0}".format(dirname))
    scan(dirname, action, executor, formatter)
    return 0


def main(argv=None):
    try:
        return main_impl(argv)
    except (KeyboardInterrupt, SystemExit):
        sys.stdout.write("\n")
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))