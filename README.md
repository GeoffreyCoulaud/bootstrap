# Various scripts
A repository a various scripts that I use on Linux.

## `bootstrap/bootstrap.sh`
Installs **my** preferred apps on a fresh install of an Arch-based Linux distro.  
`$ bootstrap/bootstrap.sh`

## `multicompose.sh`
Small bash utility to manage multiple `docker compose` subdirectories.  
Allows for running the same command on any number of subdirs, in parallel.  
Adds convenience shortcuts, such as:

| `multicompose.sh <command>` | meaning |
| --------------------------- | ------- |
| start | `docker compose up -d` |
| stop  | `docker compose down` |
| restart | `docker compose restart` |
| rebuild | `stop` then `start` |
| update | `docker compose pull` |
| rebuild-update | `stop` then `update` then `start` |
| fullstop | `stop` then `docker compose rm` |

I use it to manage my containers, but it's not the best it could be, especially the argument parsing.

## `move-files-types.js`
Sort all file types in a directory's subdirs that match a prefix.  
It's useful to sort files backed up with `testdisk`.  
```
dir
	PREFIX_1
		file1.txt
		file2.js
		file3.pdf
		...
	PREFIX_2
		abcd.txt
		...
	...
```
becomes
```
dir
	PREFIX_1
	PREFIX_2
	...
	txt
		file1.txt
		abcd.txt
	js
		file2.js
	pdf
		file3.pdf
```
`$ node move-files-types.js "/path/to/dir" "PREFIX_"`