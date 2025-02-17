#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SERVICE_NAME=$(basename $SCRIPT_DIR)

echo
echo "Restarting $SERVICE_NAME..."

pid=$(pgrep -f "python $SCRIPT_DIR/$SERVICE_NAME.py")
if [ -n "$pid" ]; then
    svc -t /service/$SERVICE_NAME
    pkill -f "python $SCRIPT_DIR/$SERVICE_NAME.py" > /dev/null 2>&1
    echo "done."
else
    echo "driver is not running!"
fi

echo
