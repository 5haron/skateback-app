#!/bin/bash

sudo btmgmt le on
sudo btmgmt advertising on

sudo hciconfig hci0 up
sudo hciconfig hci0 piscan

bluetoothctl << EOF
power on
agent on
default-agent
pairable on
discoverable on
EOF
