from bluepy.btle import Scanner, DefaultDelegate
from collections import defaultdict
import time

# Used to filter the output
#  KNOWN_MACS = []
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
        if len(KNOWN_MACS) > 0 and dev.addr.upper() not in KNOWN_MACS:
            return

        # mark this entry as new
        d = self.found.setdefault(dev.addr,
            {"id": len(self.found), "rssi": None, "last_update": None }
        )

        # log a prefix
        last_seen = "new" if isNewData else "upd:%02.2fs" % (time.time() - d["last_update"])

        # set our rssi update string - empty if was no previous value
        rssi_upd8 = ""
        if d["rssi"] is not None:
            chg = dev.rssi - d["rssi"]
            rssi_upd8 = " (%+d)" % chg

        # log our update to the screen
        print("[%.02f][id=%d][%s] Device %s (%s), RSSI=%d dB%s" %
            (time.time(), d["id"], last_seen, dev.addr, dev.addrType, dev.rssi, rssi_upd8)
        )

        # update the update time and RSSI for the next iteration
        d["last_update"] = time.time()
        d["rssi"] = dev.rssi

# setup the scanners
scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(None)
print('done')

# for dev in devices:
#     print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
#     for (adtype, desc, value) in dev.getScanData():
#         print("  %s = %s" % (desc, value))


