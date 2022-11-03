#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SERVICE_NAME=$(basename $SCRIPT_DIR)

sed -i "/$SERVICE_NAME/d" /data/rc.local
rm /service/$SERVICE_NAME
kill $(pgrep -f "supervise $SERVICE_NAME")

$SCRIPT_DIR/restart.sh
