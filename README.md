rgit
====

rgit is a powerful python script to fetch, pull or push multiple repositories
recursively.

###Usage


```
usage: rgit.py [-h] [-v] [-d DIRNAME] [-r REMOTE] [--dry-run]
               {pull,push,fetch,status} ...

rgit execute git commands recursively

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose
  -d DIRNAME, --dir DIRNAME
                        The directory to scan sub dirs from. The default is
                        current working directory
  -r REMOTE, --remote REMOTE
                        Set the remote name (remotename:branchname)
  --dry-run             Don't execute anything actually. Just display executed
                        commands

Action:
  git action to execute: pull, push, fetch, status

  {pull,push,fetch,status}
                        git action to execute recursively

```