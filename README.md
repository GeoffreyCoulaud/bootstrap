# Various scripts
A list of utilities for Manjaro Linux that I sometimes use

# What / How

### `disable-ertm.sh` 
Disable bluetooth's `ertm` option, useful when you want to connect a Xbox One controller.  
Usage : `sudo ./disable-ertm.sh`

### `disable-onboard-keyboard.sh`
Disable integrated keyboard on an Asus laptop. This is useful for me when I have an external keyboard connected.   
*This will certainly not work if you have a laptop from another brand or if your external keyboard is from Asus.*  
Usage : `./disable-onboard-keyboard.sh`

### `enable-onboard-keyboard.sh`
Inverse of `disable-onboard-keyboard.sh`.  
Usage : `./enable-onboard-keyboard.sh`

### `restart-pulseaudio.sh`
Restart the audio server. This is useful if audio devices are not listed correctly or if there are severe audio bugs on all the desktop.
Usage : `./restart-pulseaudio.sh`

### `fullpath-to-filename.sh`
Gets the file name from a full path.  
Usage : `./fullpath-to-filepath.sh "/path/to/the/file.txt"`

### `fullpath-to-path.sh`
Gets the path from a full path.  
Usage : `./fullpath-to-path.sh "/path/to/the/file.txt"`

### `sync-theme-alacritty-vscodium.py`
Synchronizes vscodium's terminal color theme from alacritty.
I use it to have a consistent terminal color across all my terminals.   
Usage : `python3 sync-theme-alacritty-vscodium.py` 