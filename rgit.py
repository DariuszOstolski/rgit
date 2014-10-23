#!/usr/bin/python

# @desc     Recursive git. This is simple python script 
#           to execute git pull/push and fetch recursively
#           on multiple repositories
#
# @author   Dariusz Ostolski 


import sys
import os
import glob
import commands
import logging
from optparse import OptionParser

parser = OptionParser(description="")
parser.add_option("-d", "--dir",
      dest    = "dirname",
      action  = "store",
      help    = "The directory to parse sub dirs from",
      default = os.path.abspath("./")
      )

parser.add_option("-v", "--verbose",
      action    = "store_true",
      dest      = "verbose",
      default   = False,
      help      = "Show the full detail of git status"
      )

parser.add_option("-r", "--remote",
    action      = "store",
    dest        = "remote",
    default     = "",
    help        = "Set the remote name (remotename:branchname)"
    )

parser.add_option("--push",
    action      = "store_true",
    dest        = "push",
    default     = False,
    help        = "Do a 'git push' if you've set a remote with -r it will push to there"
    )

parser.add_option("-p", "--pull",
    action      = "store_true",
    dest        = "pull",
    default     = False,
    help        = "Do a 'git pull' if you've set a remote with -r it will pull from there"
    )

parser.add_option("-f", "--fetch",
    action      = "store_true",
    dest        = "fetch",
    default     = False,
    help        = "Do a 'git fetch' if you've set a remote with -r it will pull from there"
    )

parser.add_option( "--dry-run",
    action      = "store_true",
    dest        = "dry",
    default     = False,
    help        = "Don't execute anything actually. Just display executed commands"
    )
"""
http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
"""
class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'

  def disable(self):
    self.HEADER = ''
    self.OKBLUE = ''
    self.OKGREEN = ''
    self.WARNING = ''
    self.FAIL = ''
    self.ENDC = ''

HEADER='-- Starting rgit...\n'

  
class Action:
  def __init__(self, action, remote):
    self._remote = remote
    self._action = action
    
  def format(self, directory):
    return "cd {0}; git {1} ".format(directory, self._action)+' '.join(self._remote.split(":")) 
  
  def get(self):
    return "({0})".format(self._action)

  def safe(self):
    return (self._action=='fetch')

class DryRunExecutor:
  def getoutput(self, command):
    logging.warning("Executing: %s", command)
    if command.find('git status')!=-1:
      return """On branch master
Your branch is up-to-date with 'origin/master'.

nothing to commit, working directory clean"""
    return ""

class CommandsExecutor:
  def getoutput(self, command):
    logging.debug("Executing: %s", command)
    return commands.getoutput(command)
  
ON_BRANCH = 'On branch'
def execute(dirname, action, executor):
  out = executor.getoutput("cd {0} ; git status ".format(dirname))
  logging.debug(out)
  branch_begin = out.find(ON_BRANCH);
  branch_end = out.find('\n', branch_begin);
  branch = out[branch_begin+len(ON_BRANCH)+1:branch_end];
  branchColor = bcolors.WARNING;
  
  if branch == 'master':
    branchColor = bcolors.OKGREEN
    
  no_changes = (-1!=out.find('nothing'))
  safe_to_execute_action = (action is not None and (action.safe() or no_changes))
  
  if no_changes:
    result = bcolors.OKGREEN + "No Changes" + bcolors.ENDC
  else:
    result = bcolors.FAIL + "Changes" + bcolors.ENDC
    
  # Execute requested action
  if safe_to_execute_action:
    push = executor.getoutput(action.format(dirname))
    result = result + " {0} \n".format(action.get()) + push    

  sys.stdout.write("--" + bcolors.OKBLUE + dirname.ljust(55) + bcolors.ENDC + branch + " : " + result +"\n")

def scan(dirname, action, executor):  
  full_path = os.path.join(dirname, '.git')
  if os.path.exists(full_path) and os.path.isdir(full_path):
      logging.info("Found git directory in: %s", dirname)
      execute(dirname, action, executor)
  else:
    for f in os.listdir(dirname):
      full_path = os.path.join(dirname, f)            
      if os.path.isdir(full_path):
	logging.debug("Entering directory: %s", full_path)
	scan(full_path, action, executor)

if __name__ == "__main__":
  (options, args) = parser.parse_args()
  os.environ['LANGUAGE'] = 'en_US:en';
  os.environ['LANG'] = 'en_US.UTF-8';

  verbosity = logging.WARNING
  if options.verbose:
    verbosity = logging.DEBUG
  executor = CommandsExecutor()
  if options.dry:
    executor = DryRunExecutor()
    
  action = None
  if options.pull:
    action = Action("pull", options.remote)
  if options.push:
    action = Action("push", options.remote)
  if options.fetch:
    action = Action("fetch", options.remote)
    
  dirname = os.path.abspath(options.dirname)
  logging.basicConfig(format='[%(levelname)s]: %(message)s', level=verbosity)
  os.system('clear')
  sys.stdout.write(HEADER)
  sys.stdout.write("Scanning sub directories of {0}\n".format(dirname))
  scan(dirname, action, executor)
    
    
