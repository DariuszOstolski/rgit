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

###Status

Status is a very usefull subcommand that can give You very concise view over your git repositories

```
rgit.py status [-h] [-s]

optional arguments:
  -h, --help     show this help message and exit
  -s, --summary  Display summary for each subdirectory

```

Example summary output

```
daro@prince$ ./rgit/rgit.py status -s
-- Starting rgit...
Scanning sub directories of .
-- ./naszeleki/naszeleki                                  master : Changes (status)
-- ./rgit                                                 master : Changes (status)
-- ./os                                                   master : No Changes (status)
-- ./pylxc                                                master : No Changes (status)
-- ./cppformat                                            master : Changes (status)
-- ./courses                                              master : Changes (status)
-- ./filesystem                                           master : No Changes (status)
-- ./clamav-devel                                         master : Changes [ahead 1] (status)
```

Full output:
```
-- ./naszeleki/naszeleki                                  master : Changes (status)
   Changes not staged for commit:
      modified: ./naszeleki/naszeleki/.gitignore
      modified: ./naszeleki/naszeleki/apps/web/data/parser.py
      modified: ./naszeleki/naszeleki/apps/web/tests/test_parser.py
   Untracked files:
      ./naszeleki/naszeleki/apps/web/data-dev.sqlite
-- ./rgit                                                 master : Changes (status)
   Changes not staged for commit:
      modified: ./rgit/README.md
   Untracked files:
      ./rgit/.idea/
-- ./os                                                   master : No Changes (status)
-- ./pylxc                                                master : No Changes (status)
-- ./cppformat                                            master : Changes (status)
   Changes not staged for commit:
      modified: ./cppformat/.gitignore
   Untracked files:
      ./cppformat/nbproject/
-- ./courses                                              master : Changes (status)
   Changes to be committed:
      new file: ./courses/datascience/datasci_course_materials
   Changes not staged for commit:
      modified: ./courses/comp_investing/Week3/example-data.csv
   Untracked files:
      ./courses/comp_investing/Week8/
-- ./filesystem                                           master : No Changes (status)
-- ./clamav-devel                                         master : Changes [ahead 1] (status)
   Changes to be committed:
      modified: ./clamav-devel/BUGS
      new file: ./clamav-devel/COPYING.1
      renamed:  ./clamav-devel/COPYING.regex -> ./clamav-devel/COPYING.pcre
      renamed:  ./clamav-devel/etc/Makefile.am -> ./clamav-devel/etc1/Makefile.am
   Changes not staged for commit:
      modified: ./clamav-devel/AUTHORS
   Untracked files:
      ./clamav-devel/COPYING.zliba

```

###Pull

```
rgit.py pull [-h] [--all] [-r {false,true,preserve}]

optional arguments:
  -h, --help            show this help message and exit
  --all                 Fetch all remotes.
  -r {false,true,preserve}, --rebase {false,true,preserve}
                        When true, rebase the current branch on top of the
                        upstream branch after fetching. If there is a remote-
                        tracking branch corresponding to the upstream branch
                        and the upstream branch was rebased since last
                        fetched, the rebase uses that information to avoid
                        rebasing non-local changes. When preserve, also rebase
                        the current branch on top of the upstream branch, but
                        pass --preserve-merges along to git rebase so that
                        locally created merge commits will not be flattened.
                        When false, merge the current branch into the upstream
                        branch. See pull.rebase, branch.<name>.rebase and
                        branch.autosetuprebase in git-config(1) if you want to
                        make git pull always use --rebase instead of merging.
                        Note This is a potentially dangerous mode of
                        operation. It rewrites history, which does not bode
                        well when you published that history already. Do not
                        use this option unless you have read git-rebase(1)
                        carefully.
```