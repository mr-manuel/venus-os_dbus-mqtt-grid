#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SERVICE_NAME=$(basename $SCRIPT_DIR)

echo
echo "Installing $SERVICE_NAME..."

# set permissions for script files
echo "Setting permissions..."
chmod 755 $SCRIPT_DIR/*.py
chmod 755 $SCRIPT_DIR/*.sh
chmod 755 $SCRIPT_DIR/service/run
chmod 755 $SCRIPT_DIR/service/log/run

# check dependencies
python -c "import paho.mqtt.client"
if [ $? -gt 0 ]
then
    echo "Installing paho.mqtt.client..."
    # install paho.mqtt.client
    python -m pip install paho-mqtt
    if [ $? -gt 0 ]
    then
        # if pip command fails install pip and then try again
        opkg update && opkg install python3-pip
        python -m pip install paho-mqtt
    fi
fi

# create sym-link to run script in deamon
if [ ! -L /service/$SERVICE_NAME ]; then
    echo "Creating service..."
    ln -s $SCRIPT_DIR/service /service/$SERVICE_NAME
else
    echo "Service already exists."
fi

# add install-script to rc.local to be ready for firmware update
filename=/data/rc.local
if [ ! -f $filename ]
then
    touch $filename
    chmod 755 $filename
    echo "#!/bin/bash" >> $filename
    echo >> $filename
fi

# if not alreay added, then add to rc.local
grep -qxF "bash $SCRIPT_DIR/install.sh" $filename || echo "bash $SCRIPT_DIR/install.sh" >> $filename

echo
