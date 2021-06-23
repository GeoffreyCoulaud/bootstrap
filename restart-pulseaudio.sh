#!/bin/zsh
systemctl --user restart pulseaudio.socket
systemctl --user restart pulseaudio.service
