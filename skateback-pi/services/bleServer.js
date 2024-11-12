const bleno = require("@abandonware/bleno");
const net = require("net");

const SERVICE_UUID = "12345678-1234-5678-1234-56789ABCDEF0";
const CHARACTERISTIC_UUID = "ABCDEF01-1234-5678-1234-56789ABCDEF0";
const { exec } = require("child_process");

const SOCKET_HOST = "127.0.0.1";
const SOCKET_PORT = 65432;

// Configuration and state
let isAdvertising = false;
let currentSpeed = 0;
let isReverse = false;
let client = null;

// Add detailed logging
const log = (message, data = null) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${message}`);
  if (data) {
    console.dir(data, { depth: null });
  }
};

if (process.platform === "linux") {
  log("Running on Linux (Raspberry Pi)");
}

process.on("uncaughtException", (error) => {
  log("Uncaught Exception:", error);
});



const connectToServer = () => {
  if (client && !client.destroyed) return; // Avoid multiple connections

  client = new net.Socket();
  
  client.connect(SOCKET_PORT, SOCKET_HOST, () => {
    log("Connected to Python socket server");
  });

  client.on("data", (data) => {
    log(`Response from server: ${data.toString().trim()}`);
  });

  client.on("error", (err) => {
    log(`Socket error: ${err.message}`);
    client.destroy();
    setTimeout(connectToServer, 1000);
  });

  client.on("close", () => {
    log("Connection closed. Attempting to reconnect...");
    setTimeout(connectToServer, 1000);
  });
};

connectToServer();

// Handle sending command and waiting for server response
const handleCommand = (command) => {
  if (!client || client.destroyed) {
    log("Socket not connected, attempting to reconnect...");
    connectToServer();
    return;
  }

  try {
    // Add newline as delimiter for commands
    const commandWithDelimiter = command + '\n';
    client.write(commandWithDelimiter, (err) => {
      if (err) {
        log(`Error sending command: ${err.message}`);
        return;
      }
      log(`Sent command: ${command}`);
    });
  } catch (error) {
    log(`Error in handleCommand: ${error.message}`);
  }
};


// Persistent listener to capture all data responses from the server
client.on("data", (data) => {
  log(`Response from server: ${data.toString()}`);
});


// const handleCommand = (command) => {
//   log('Received command:', command);

//   switch(command) {
//     case 'accelerate':
//       currentSpeed += 1;
//       log('Accelerating. Current speed:', currentSpeed);
//       break;
//     case 'decelerate':
//       currentSpeed = Math.max(0, currentSpeed - 1);
//       log('Decelerating. Current speed:', currentSpeed);
//       break;
//     case 'reverse_on':
//       isReverse = true;
//       log('Reverse mode enabled');
//       break;
//     case 'reverse_off':
//       isReverse = false;
//       log('Reverse mode disabled');
//       break;
//     case 'stop':
//       currentSpeed = 0;
//       log('Stopping. Current speed:', currentSpeed);
//       break;
//     default:
//       log('Unknown command:', command);
//   }

//   return `Executed: ${command}`;
// };

const characteristic = new bleno.Characteristic({
  uuid: CHARACTERISTIC_UUID,
  properties: ["read", "write", "notify"],
  descriptors: [
    new bleno.Descriptor({
      uuid: "2901",
      value: "Skateboard Control",
    }),
  ],
  onReadRequest: (offset, callback) => {
    try {
      const status = {
        speed: currentSpeed,
        reverse: isReverse,
      };
      const data = Buffer.from(JSON.stringify(status));
      log("Read request handled", status);
      callback(bleno.Characteristic.RESULT_SUCCESS, data);
    } catch (error) {
      log("Read request error:", error);
      callback(bleno.Characteristic.RESULT_UNLIKELY_ERROR);
    }
  },
  onWriteRequest: (data, offset, withoutResponse, callback) => {
    try {
      const command = data.toString("utf-8"); // Decode as UTF-8
      log("Write request received:", command);
      const response = handleCommand(command);
      callback(bleno.Characteristic.RESULT_SUCCESS);
    } catch (error) {
      log("Write request error:", error);
      callback(bleno.Characteristic.RESULT_UNLIKELY_ERROR);
    }
  },
  onSubscribe: (maxValueSize, updateValueCallback) => {
    log("Client subscribed to notifications");
  },
  onUnsubscribe: () => {
    log("Client unsubscribed from notifications");
  },
});

const advertisingOptions = {
  manufacturerData: Buffer.from("SKB1"),
  localName: "mypi",
  txPowerLevel: 127,
  connectable: true,
};

bleno.on("stateChange", (state) => {
  log("Bluetooth state changed:", {
    state,
    advertising: isAdvertising,
    serviceUUID: SERVICE_UUID,
  });

  if (state === "poweredOn" && !isAdvertising) {
    // Start advertising with specific options for iOS
    bleno.startAdvertising(
      "mypi",
      [SERVICE_UUID],
      advertisingOptions,
      (error) => {
        if (error) {
          log("Failed to start advertising:", error);
        } else {
          isAdvertising = true;
          log("Started advertising with options:", {
            name: "mypi",
            serviceUUIDs: [SERVICE_UUID],
            options: advertisingOptions,
          });
        }
      }
    );
  } else if (state !== "poweredOn") {
    if (isAdvertising) {
      bleno.stopAdvertising(() => {
        isAdvertising = false;
        log("Stopped advertising");
      });
    }
  }
});

bleno.on("advertisingStart", (error) => {
  if (!error) {
    log("Setting up services...");
    bleno.setServices(
      [
        new bleno.PrimaryService({
          uuid: SERVICE_UUID,
          characteristics: [characteristic],
        }),
      ],
      (error) => {
        if (error) {
          log("Error setting services:", error);
        } else {
          log("Services set successfully", {
            serviceUUID: SERVICE_UUID,
            characteristicUUID: CHARACTERISTIC_UUID,
            properties: characteristic.properties,
          });
        }
      }
    );
  } else {
    log("Failed to start advertising:", error);
  }
});

bleno.on("accept", (clientAddress) => {
  log("Connection accepted:", clientAddress);
});

bleno.on("disconnect", (clientAddress) => {
  log("Client disconnected:", clientAddress);
  currentSpeed = 0;
  isReverse = false;
});

bleno.on("advertisingStop", () => {
  log("Advertising stopped");
});

bleno.on("servicesSet", (error) => {
  if (error) {
    log("Error setting services:", error);
  } else {
    log("Services set successfully");
  }
});

process.on("SIGINT", () => {
  log("Stopping BLE server...");
  bleno.stopAdvertising(() => {
    log("Stopped advertising");
    process.exit();
  });
});

// Add periodic status logging
setInterval(() => {
  if (isAdvertising) {
    log("Server status:", {
      advertising: isAdvertising,
      currentSpeed,
      isReverse,
      serviceUUID: SERVICE_UUID,
      characteristicUUID: CHARACTERISTIC_UUID,
    });
  }
}, 30000);

log("BLE server starting...");
