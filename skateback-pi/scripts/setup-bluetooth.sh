#!/bin/bash

sudo btmgmt le on
sudo btmgmt advertising on

sudo hciconfig hci0 up
sudo hciconfig hci0 piscan

bluetoothctl << EOF
power on
agent NoInputNoOutput
default-agent
pairable on
discoverable on
EOF
