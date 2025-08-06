# bootstrap

Personal linux desktop setup script for Arch-based distros.  

## Generating the flatpak list

```sh
flatpak list --columns=origin,application --app > flatpak.txt
```