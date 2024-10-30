#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SERVICE_NAME=$(basename $SCRIPT_DIR)

pid=$(pgrep -f "python $SCRIPT_DIR/$SERVICE_NAME.py")
if [ -n "$pid" ]; then
    kill $pid
    echo "** Driver restarted **"
else
    echo "** Driver is not running **"
fi
