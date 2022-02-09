#!/bin/bash
# $1 = Prefix path
LOG_PATH="$1/drive_c/users/$USER/AppData/LocalLow/miHoYo/Genshin Impact/output_log.txt"
URL=$(grep -E "OnGetWebViewPageFinish.*log" "$LOG_PATH" | tail --lines 2 | head --lines 1 | sed 's#OnGetWebViewPageFinish:##')
if [[ -z $URL ]]; then
	echo "No URL found. Make sure to look at the wish history."
else
	echo "$URL"
fi