
const cp = require('child_process');
const noble = require('@abandonware/noble');

const emac  = '00:1b:10:60:4c:9e' // external module addr to connect to
const emac2 = '00:1b:10:60:4d:9e' // external module, advertised until connected to
const imac  = 'e0:9f:2a:ea:db:a7' // internal, advertised, used to get RSSI
const serial_service_uuid = '00001101-0000-1000-8000-00805f9b34fb'

const UPDATE_FREQ_MS = 1000;

const addrMap = {
	[emac]: "OO >>>", // not used?
	[imac]: "II >>",
	[emac2]: "OO <<"
}

noble.on('stateChange', function (state) {
	if (state === 'poweredOn') {
		noble.startScanning([], true, e => {
			if(e) console.error("error starting bluetooth scan", e);
			else console.log("started scanning...");
		}) //allows duplicates while scanning
	} else {
		noble.stopScanning();
	}
});

let connecting = false;
let connected = false;

let pyproc = cp.spawn('python3', ['rssi_loop.py'])
function establishPyProc() {
	pyproc.stdout.on('data', d => {
		if(Buffer.isBuffer(d)) d = d.toString('ascii')
		// console.log('python: ' + d);
	})
	pyproc.stderr.on('data', d => {
		if(Buffer.isBuffer(d)) d = d.toString('ascii')
		console.error('python: ' + d);
	})
	pyproc.on("close", e => {
		pyproc = cp.spawn('python3', ['rssi_loop.py']);
		establishPyProc()
	})
}
establishPyProc()

let last_sent = Date.now();
let period = [];
function sendRssi(addr, rssi) {
	let now = Date.now();
	period.push(rssi);
	if(last_sent + UPDATE_FREQ_MS < now) {
		/** @type {number} */
		let smoothed = (period.reduce((p, c) => p + c)/period.length).toFixed(0);
		console.log(`rssi update: ${addr}, ${rssi} (smoothed: ${smoothed})`);
		period = [];

		pyproc.stdin.write(smoothed + '\n');
		last_sent = now;
	}
}

noble.on('discover', function (peripheral) {
	let bleAddr = peripheral.address;
	let bleRssi = peripheral.rssi;
	let bleName = (peripheral.advertisement.localName || '').padEnd(32, ' ')

	// console.error(`[${new Date().toLocaleTimeString()}] BLE update. MAC:${bleAddr}\tRSSI:${bleRssi}\tName:${bleName} (${addrMap[bleAddr] || "<unknown>"})`);

	// if(bleAddr == emac2.toLowerCase()) {
		// console.error(`[${bleAddr}] attempting to connect to ${bleName}\tRSSI:${bleRssi}`);
		// if(!connecting && !connected) {
		// 	connecting = true;
		// 	peripheral.connect(e => {
		// 		connecting = false;
		// 		if(e) {
		// 			console.error(`[${bleAddr}] error connecting to ${bleName}`, e)
		// 		} else {
		// 			connected = true;
		// 			console.error(`[${bleAddr}] connected to ${bleName}`);
		// 		}
		// 	});
		// 	peripheral.on('rssiUpdate', (rssi) => {
		// 		console.log(`[${bleAddr}] RSSI: ${rssi}`)
		// 	});
		// 	peripheral.updateRssi((e, rssi) => {
		// 		if(e) console.error(`[${bleAddr}] error updating rssi`, e);
		// 		else  console.log(`[${bleAddr}] rssi: ${rssi}`);
		// 	});
		// 	peripheral.discoverServices();
		// 	peripheral.on('servicesDiscover', s => {
		// 		console.log(`service discovered: ${s.uuid} :: ${s.type} :: ${s.name} :: ${s.includedServiceUuids.join(',')}`)
		// 		for(let c of s.characteristics) {
		// 			console.log(`\tcharacteristic: ${c.uuid} :: ${c.type} :: ${c.name} :: ${c.properties.join(',')}`)
		// 			for(let d of c.descriptors) {
		// 				console.log(`\t\tdescriptor: ${d.uuid} :: ${d.type} :: ${d.name}`)
		// 			}
		// 		}
		// 	});
		// }
	// } else if(!connected) {
		if(bleAddr in addrMap) {
			sendRssi(bleAddr, bleRssi);
		}
	// }
});

