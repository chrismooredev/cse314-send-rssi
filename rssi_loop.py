
import os
import sys
import time
import struct
import socket
import bluetooth
# import bluetooth._bluetooth as bluez

# specify the BLE MAC to connect with
emac = '00:1B:10:60:4C:9E' # emac
# emac = 'e0:9f:2a:ea:db:a7'
# emac = '00:1B:10:60:4D:9E' # imac
port = 3 # not sure tbh

# setup our connection
s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
print('connecting...')
s.connect((emac, port))
print('connected')

# some initial messages to test with
# s.send(bytes("msg:Hel\x88lo\n", "UTF-8"))
s.send(bytes("msg:Hello\n", "UTF-8"))


# s = socket.socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
# s.connect((emac, port))
# s.send(bytes('hello!\n', 'UTF-8'))

while True:
    # send a heartbeat on every iteration
    s.send(bytes("msg:heartbeat\n", "UTF-8"))
    print('.', end='')
    try:
        # ask the user (index.js) for a value
        srssi = int(input('rssi: '))
        # send it to the bot
        s.send(bytes("rssi:%d\n" % srssi, "UTF-8"))
    except Exception as e:
        # don't crash if we didn't receive a numeric value to send
        print("couldn't parse rssi, didn't send", e)
    
    # print(device_inquiry_with_with_rssi(sock_dev))
    # time.sleep(4)

