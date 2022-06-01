from bluepy.btle import Scanner, DefaultDelegate
from collections import defaultdict
import time

KNOWN_MACS = [
    '00:1B:10:60:4D:9E',
    '00:1B:10:60:4C:9E',
    'E0:9F:2A:EA:DB:A7',
]

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        self.found = dict()

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if dev.addr.upper() not in KNOWN_MACS:
            return

        d = self.found.get(dev.addr)
        if d is None:
            d = {"id": len(self.found), "rssi": None, "last_update": None }
            self.found[dev.addr] = d

        if isNewData:
            last_seen = "new"
        else:
            last_seen = "upd:%02.2fs" % (time.time() - d["last_update"])

        if d["rssi"] is None:
            rssi_upd8 = ""
        else:
            chg = dev.rssi - d["rssi"]
            rssi_upd8 = " (%+d)" % chg

        print("[%.02f][id=%d][%s] Device %s (%s), RSSI=%d dB%s" % (time.time(), d["id"], last_seen, dev.addr, dev.addrType, dev.rssi, rssi_upd8))

        d["last_update"] = time.time()
        d["rssi"] = dev.rssi
        # if isNewDev:
        #     print("Discovered device", dev.addr)
        # elif isNewData:
        #     print("Received new data from", dev.addr)

scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(None)
print('done')

# for dev in devices:
#     print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
#     for (adtype, desc, value) in dev.getScanData():
#         print("  %s = %s" % (desc, value))


