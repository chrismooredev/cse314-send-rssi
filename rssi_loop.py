
import os
import sys
import time
import struct
import socket
import bluetooth
import bluetooth._bluetooth as bluez

emac = '00:1B:10:60:4C:9E' # emac
# emac = 'e0:9f:2a:ea:db:a7'
# emac = '00:1B:10:60:4D:9E' # imac
port = 3 # not sure tbh

s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
print('connecting...')
s.connect((emac, port))
print('connected')
s.send(bytes("msg:Hel\x88lo\n", "UTF-8"))
s.send(bytes("msg:Hello\n", "UTF-8"))


# s = socket.socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
# s.connect((emac, port))
# s.send(bytes('hello!\n', 'UTF-8'))

# https://github.com/karulis/pybluez/blob/master/examples/advanced/inquiry-with-rssi.py
def device_inquiry_with_with_rssi(sock):
    # save current filter
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    # perform a device inquiry on bluetooth device #0
    # The inquiry should last 8 * 1.28 = 10.24 seconds
    # before the inquiry is performed, bluez should flush its cache of
    # previously discovered devices
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )

    duration = 4
    max_responses = 255
    cmd_pkt = struct.pack("BBBBB", 0x33, 0x8b, 0x9e, duration, max_responses)
    bluez.hci_send_cmd(sock, bluez.OGF_LINK_CTL, bluez.OCF_INQUIRY, cmd_pkt)

    results = []

    done = False
    while not done:
        pkt = sock.recv(255)
        ptype, event, plen = struct.unpack("BBB", pkt[:3])
        if event == bluez.EVT_INQUIRY_RESULT_WITH_RSSI:
            pkt = pkt[3:]
            nrsp = bluetooth.get_byte(pkt[0])
            for i in range(nrsp):
                addr = bluez.ba2str( pkt[1+6*i:1+6*i+6] )
                rssi = bluetooth.byte_to_signed_int(
                        bluetooth.get_byte(pkt[1+13*nrsp+i]))
                results.append( ( addr, rssi ) )
                print("[%s] RSSI: [%d]" % (addr, rssi))
        elif event == bluez.EVT_INQUIRY_COMPLETE:
            done = True
        elif event == bluez.EVT_CMD_STATUS:
            status, ncmd, opcode = struct.unpack("BBH", pkt[3:7])
            if status != 0:
                print("uh oh...")
                printpacket(pkt[3:7])
                done = True
        elif event == bluez.EVT_INQUIRY_RESULT:
            pkt = pkt[3:]
            nrsp = bluetooth.get_byte(pkt[0])
            for i in range(nrsp):
                addr = bluez.ba2str( pkt[1+6*i:1+6*i+6] )
                results.append( ( addr, -1 ) )
                print("[%s] (no RRSI)" % addr)
        else:
            print("unrecognized packet type 0x%02x" % ptype)
        print("event %d (0x%02x)" % (event, event))


    # restore old filter
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )

    return results

sock_dev = bluez.hci_open_dev(0)

while True:
    s.send(bytes("msg:heartbeat\n", "UTF-8"))
    print('.', end='')
    # l = s.read()
    try:
        srssi = int(input('rssi: '))
        s.send(bytes("rssi:%d\n" % srssi, "UTF-8"))
    except Exception as e:
        print("couldn't parse rssi, didn't send", e)
    
    # print(device_inquiry_with_with_rssi(sock_dev))
    # time.sleep(4)

