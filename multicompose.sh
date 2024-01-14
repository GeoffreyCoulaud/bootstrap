#!/bin/bash

# TODO ideally, use a standard tool for argument parsing

subcommand=$1

# Early "help" subcommand
if [[ $subcommand = "help" ]]; then
	echo "Geoffrey Coulaud's multi docker-compose management script"
	echo "Shorthand for common docker-compose commands called for various subfolders"
	exit 0
fi

shift
groups=$@

# Group "all" alias
if [[ $groups = "all" ]]
then
	groups=./*/
fi

# Commands behaviour
# $1 is always the group subfolder
dc-start() {
	cd $1
	sudo docker compose up -d
}
dc-stop() {
	cd $1
	sudo docker compose down
}
dc-remove() {
	cd $1
	sudo docker compose rm
}
dc-restart(){
	cd $1
	sudo docker compose restart
}
dc-update() {
	cd $1
	sudo docker compose pull
}
dc-fullstop() {
	(dc-stop $1)
	(dc-remove $1)
}
dc-rebuild() {
	(dc-fullstop $1)
	(dc-start $1)
}
dc-rebuild-update() {
	(dc-fullstop $1)
	(dc-update $1)
	(dc-start $1)
}

# Kill all subprocesses with ctrl-c
trap 'kill 0' SIGINT

# Run the command for every group in parallel
for group in $groups; do
	
	# Check that the group exists
	if [[ ! -d $group ]]; then
		echo "Invalid group subdir: ${group}"
		continue
	fi

	# Run the appropriate subcommand
	echo "Running ${subcommand} for ${group}"
	if [[ "$subcommand" = "start" ]]; then
		dc-start $group &
	elif [[ "$subcommand" = "stop" ]]; then
		dc-stop $group &
	elif [[ "$subcommand" = "restart" ]]; then
		dc-restart $group &
	elif [[ $subcommand = "rebuild" ]]; then
		dc-rebuild $group &
	elif [[ $subcommand = "update" ]]; then
		dc-update $group &
	elif [[ $subcommand = "rebuild-update" ]]; then
		dc-rebuild-update $group &
	elif [[ $subcommand = "fullstop" ]]; then
		dc-fullstop $group &
	else
		# TODO ideally, move before the for loop
		echo "Invalid subcommand: $subcommand"
		exit 1
	fi

done

# Exit gracefully
wait
exit 0