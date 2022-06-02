# CSE314 - RSSI Sender

Made up of two main scripts:
* `index.js`
    * Runs the main code - Samples the environment for an RSSI value, lightly smooths it for irregularity
    * Also runs the `rssi_loop.py` python script, which attaches to the Makebot and sends it RSSI values over bluetooth serial
* `rssi_loop.py`
    * Connects to the Makebot over Bluetooth LE and sends it RSSI values, provided by `index.js`
* `btle_scan.py` is used for debugging scanning available BLE devices. (eg: those that are advertising)

Needs python3 with packages:
* `bluetooth`

Needs nodejs with packages:
* `@abandonware/noble`

Needs some combination of apt packages:
* `libglib2.0-dev`
* `bluez-hcidump`
* `bluez-tools`
