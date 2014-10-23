rgit
====

rgit is a powerful python script to fetch, pull or push multiple repositories
recursively.

Usage
====

Usage: rgit.py [options]

Options:
  -h, --help            show this help message and exit
  -d DIRNAME, --dir=DIRNAME
                        The directory to parse sub dirs from
  -v, --verbose         Show the full detail of git status
  -r REMOTE, --remote=REMOTE
                        Set the remote name (remotename:branchname)
  --push                Do a 'git push' if you've set a remote with -r it will
                        push to there
  -p, --pull            Do a 'git pull' if you've set a remote with -r it will
                        pull from there
  -f, --fetch           Do a 'git fetch' if you've set a remote with -r it
                        will pull from there
  --dry-run             Don't execute anything actually. Just display executed
                        commands
