# Various scripts
A repository a various scripts that I use on Linux.

## `disable-ertm.sh` 
Disable bluetooth's `ertm` option, useful when you want to connect a Xbox One controller.  
`$ sudo ./disable-ertm.sh`

## `sync-theme-alacritty-vscodium.py`
Synchronizes vscodium's terminal color theme from alacritty.  
I use it to have a consistent terminal color across all my terminals.   
`$ python3 sync-theme-alacritty-vscodium.py` 

## `bootstrap/bootstrap.sh`
Installs **my** preferred apps on a fresh install of an Arch-based Linux distro.  
`$ bootstrap/bootstrap.sh`

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

## `genshin-linux-wish-url.sh`
Get the wish url for Genshin Impact on Linux.  
`$ genshin-linux-wish-url.sh "/path/to/game/prefix"`