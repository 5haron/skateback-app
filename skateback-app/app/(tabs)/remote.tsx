import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  Image,
  StyleSheet,
  TouchableOpacity,
  Switch,
  Alert,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { BleManager, Device } from "react-native-ble-plx";
import { Buffer } from "buffer";

const SERVICE_UUID = "12345678-1234-5678-1234-56789ABCDEF0";
const CHARACTERISTIC_UUID = "ABCDEF01-1234-5678-1234-56789ABCDEF0";
const DOUBLE_PRESS_INTERVAL = 2000;

const SpeedLevelIndicator = ({
  currentSegment,
  dutyCycle,
}: {
  currentSegment: number;
  dutyCycle: number;
}) => {
  const totalSegments = 25;
  const centerSegment = 12;

  const renderSegments = () => {
    const segments = [];
    for (let i = 0; i < totalSegments; i++) {
      const isActive = i === currentSegment;

      let backgroundColor;
      if (i < centerSegment) {
        // Reverse/Decelerate (red)
        backgroundColor = isActive ? "#FF0000" : "rgba(255, 0, 0, 0.2)";
      } else if (i > centerSegment) {
        // Forward/Accelerate (green)
        backgroundColor = isActive ? "#00FF00" : "rgba(0, 255, 0, 0.2)";
      } else {
        // Center
        backgroundColor = isActive ? "#023047" : "#E7F2F8";
      }

      segments.push(
        <View
          key={i}
          style={[
            styles.segment,
            {
              backgroundColor,
            },
          ]}
        />
      );
    }
    return segments;
  };

  return (
    <View style={styles.speedIndicator}>
      <Text style={styles.speedValue}>{Math.abs(dutyCycle).toFixed(2)}</Text>
      <View style={styles.labelContainer}>
        <Text style={styles.speedLabel}>duty cycle</Text>
      </View>
      <View style={styles.segmentsContainer}>{renderSegments()}</View>
    </View>
  );
};

export default function RemoteControlScreen() {
  const [batteryPercentage, setBatteryPercentage] = useState(100);
  const [dutyCycle, setDutyCycle] = useState(0);
  const [currentSegment, setCurrentSegment] = useState(12);
  const [bleManager] = useState(() => new BleManager());
  const [connectedDevice, setConnectedDevice] = useState<Device | null>(null);
  const [firstStopPressTime, setFirstStopPressTime] = useState<number | null>(
    null
  );
  const { skateboardName } = useLocalSearchParams();
  const router = useRouter();

  useEffect(() => {
    connectToDevice();
    return () => {
      if (connectedDevice) {
        connectedDevice.cancelConnection();
      }
    };
  }, []);

  const handleConnectionError = (message: string) => {
    Alert.alert("Connection Error", message, [
      {
        text: "OK",
        onPress: () => {
          router.push("/searching");
        },
      },
    ]);
  };

  const connectToDevice = async () => {
    try {
      let device: Device | null = (
        await bleManager.connectedDevices([SERVICE_UUID])
      )[0];

      if (!device) {
        device = await new Promise<Device>((resolve, reject) => {
          bleManager.startDeviceScan(
            [SERVICE_UUID],
            null,
            (error, scannedDevice) => {
              if (error) {
                reject(error);
                return;
              }
              if (scannedDevice && scannedDevice.name === "mypi") {
                bleManager.stopDeviceScan();
                resolve(scannedDevice);
              }
            }
          );

          setTimeout(() => {
            bleManager.stopDeviceScan();
            reject(new Error("Device scan timeout"));
          }, 10000);
        });

        device = await device.connect();
      }

      if (!device.isConnected) {
        throw new Error("Device is not connected after connect call");
      }

      await device.discoverAllServicesAndCharacteristics();
      setConnectedDevice(device);
      console.log("Connected to device:", device.name);
    } catch (error) {
      console.error("Connection error:", error);
      handleConnectionError(
        "Failed to connect to the skateboard. Please reconnect to skateboard again."
      );
    }
  };

  const sendCommand = async (command: string) => {
    if (!connectedDevice) {
      console.log("No device connected");
      return;
    }

    try {
      const services = await connectedDevice.services();
      const service = services.find(
        (s) => s.uuid.toLowerCase() === SERVICE_UUID.toLowerCase()
      );
      if (!service) {
        console.error("Service not found");
        handleConnectionError(
          "Failed to send command to the skateboard. Service not available."
        );
        return;
      }

      const characteristics = await service.characteristics();
      const characteristic = characteristics.find(
        (c) => c.uuid.toLowerCase() === CHARACTERISTIC_UUID.toLowerCase()
      );

      if (!characteristic) {
        console.error("Characteristic not found");
        handleConnectionError(
          "Failed to send command to the skateboard. Characteristic not available."
        );
        return;
      }

      await characteristic.writeWithResponse(
        Buffer.from(command).toString("base64")
      );
      console.log("Command sent:", command);
    } catch (error) {
      console.error("Error sending command:", error);
      handleConnectionError(
        "Failed to send command to the skateboard. Please try reconnecting."
      );
    }
  };

  const handleAccelerate = async () => {
    let newDutyCycle;
    let newSegment = currentSegment;

    if (dutyCycle === 0) {
      // Initial acceleration from 0
      newDutyCycle = 0.05;
      newSegment = 13; // Move one segment right from center
    } else if (dutyCycle === -0.05) {
      // Special case: stepping up from -0.05 to 0
      newDutyCycle = 0;
      newSegment = 12; // Back to center
    } else {
      // Regular acceleration step
      newDutyCycle = Math.min(0.6, dutyCycle + 0.02);
      newSegment = Math.min(24, currentSegment + 1); // Move one segment right, max at 24
    }

    setDutyCycle(newDutyCycle);
    setCurrentSegment(newSegment);
    await sendCommand("accelerate");
  };

  const handleDecelerate = async () => {
    let newDutyCycle;
    let newSegment = currentSegment;

    if (dutyCycle === 0) {
      // Initial deceleration from 0
      newDutyCycle = -0.05;
      newSegment = 11; // Move one segment left from center
    } else if (dutyCycle === 0.05) {
      // Special case: stepping down from 0.05 to 0
      newDutyCycle = 0;
      newSegment = 12; // Back to center
    } else {
      // Regular deceleration step
      newDutyCycle = Math.max(-0.6, dutyCycle - 0.02);
      newSegment = Math.max(0, currentSegment - 1); // Move one segment left, min at 0
    }

    setDutyCycle(newDutyCycle);
    setCurrentSegment(newSegment);
    await sendCommand("decelerate");
  };

  const handleStopPress = async () => {
    const now = Date.now();

    if (
      firstStopPressTime &&
      now - firstStopPressTime <= DOUBLE_PRESS_INTERVAL
    ) {
      setDutyCycle(0);
      setCurrentSegment(12); // Reset to center segment
      await sendCommand("stop");
      setFirstStopPressTime(null);
    } else {
      setFirstStopPressTime(now);
      setTimeout(() => {
        if (Date.now() - firstStopPressTime! >= DOUBLE_PRESS_INTERVAL) {
          setFirstStopPressTime(null);
        }
      }, DOUBLE_PRESS_INTERVAL);
    }
  };

  const renderBatteryRectangles = () => {
    const numberOfRectangles = Math.floor(batteryPercentage / 20);
    let rectangles = [];
    for (let i = 0; i < numberOfRectangles; i++) {
      rectangles.push(<View key={i} style={styles.batteryRectangle} />);
    }
    return rectangles;
  };

  return (
    <View style={styles.container}>
      <View style={styles.headerContainer}>
        <Text style={styles.title}>
          {skateboardName
            ? Array.isArray(skateboardName)
              ? skateboardName
                  .join(" ")
                  .replace(/skateboard/i, "")
                  .trim()
              : skateboardName.replace(/skateboard/i, "").trim()
            : "Unknown's"}
          {"\n"}
          <Text>Skateboard</Text>
        </Text>
        <View style={styles.roundedBox}>
          <Image
            source={require("@skateback/assets/icons/skateboard.png")}
            style={styles.roundedIcon}
          />
        </View>
      </View>

      <View style={styles.statBox}>
        <SpeedLevelIndicator
          currentSegment={currentSegment}
          dutyCycle={dutyCycle}
        />
      </View>

      <View style={styles.splitContainer}>
        <View style={styles.leftBox}>
          <Image
            source={require("@skateback/assets/icons/skate-battery.png")}
            style={styles.skateBatteryImage}
            resizeMode="contain"
          />
          <Image
            source={require("@skateback/assets/icons/battery.png")}
            style={styles.batteryImage}
            resizeMode="contain"
          />
          <View style={styles.batteryRectangleContainer}>
            {renderBatteryRectangles()}
          </View>
          <TouchableOpacity style={styles.stopBox} onPress={handleStopPress}>
            <Text style={styles.stopTextDes}>Press twice to</Text>
            <Text style={styles.stopText}>STOP</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.rightContainer}>
          <View style={styles.buttonContainer}>
            <Text style={styles.controlLabel}>Accelerate</Text>
            <TouchableOpacity style={styles.button} onPress={handleAccelerate}>
              <Text style={styles.buttonText}>+</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.buttonContainer}>
            <Text style={styles.controlLabel}>Decelerate</Text>
            <TouchableOpacity style={styles.button} onPress={handleDecelerate}>
              <Text style={styles.buttonText}>–</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
    padding: 16,
  },
  headerContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingTop: 10,
  },
  title: {
    fontSize: 26,
    fontWeight: "bold",
    color: "#023047",
  },
  roundedBox: {
    backgroundColor: "#8ECAE6",
    borderRadius: 20,
    padding: 14,
    alignItems: "center",
    justifyContent: "center",
    width: 65,
  },
  roundedIcon: {
    width: 35,
    height: 35,
  },
  statBox: {
    alignItems: "center",
    backgroundColor: "#E7F2F8",
    borderRadius: 20,
    padding: 40,
    marginTop: 20,
    width: 320,
    marginLeft: 20,
    height: 180,
    justifyContent: "center",
  },
  speedIndicator: {
    width: "100%",
    alignItems: "center",
    justifyContent: "center",
    height: "100%",
  },
  speedValue: {
    fontSize: 90,
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 0,
    color: "#023047",
  },
  segmentsContainer: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    height: 25,
    width: "110%",
    marginTop: 2,
    gap: 3,
  },
  segment: {
    flex: 1,
    height: "100%",
    borderRadius: 6,
  },
  labelContainer: {
    alignItems: "center",
    justifyContent: "center",
    marginTop: -12,
    marginBottom: 10,
  },
  speedLabel: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#023047",
    marginTop: 0,
  },
  splitContainer: {
    flexDirection: "row",
    marginTop: 20,
    paddingHorizontal: 20,
    width: 360,
    height: 300,
  },
  leftBox: {
    flex: 1,
    marginRight: 10,
    borderRadius: 20,
    position: "relative",
    height: 300,
  },
  skateBatteryImage: {
    width: 160,
    height: 500,
    alignSelf: "center",
    marginTop: -164,
    marginLeft: -10,
  },
  batteryImage: {
    position: "absolute",
    top: 6,
    left: 52,
    width: 43,
    height: 160,
    transform: [{ rotate: "90deg" }],
  },
  batteryRectangleContainer: {
    position: "absolute",
    top: 40,
    left: 46,
    width: 32,
    height: 92,
    flexDirection: "column",
    justifyContent: "flex-end",
    transform: [{ rotate: "-90deg" }],
  },
  batteryRectangle: {
    width: "100%",
    height: 10,
    backgroundColor: "white",
    marginBottom: 4,
  },
  rightContainer: {
    flex: 1,
    justifyContent: "space-between",
  },
  controlLabel: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#023047",
    textAlign: "center",
  },
  buttonContainer: {
    alignItems: "center",
    justifyContent: "flex-start",
    marginBottom: 10,
  },
  button: {
    backgroundColor: "#E7F2F8",
    borderRadius: 20,
    alignItems: "center",
    justifyContent: "center",
    paddingBottom: 10,
    marginVertical: 5,
    width: "100%",
    height: 152,
  },
  buttonText: {
    fontSize: 120,
    fontWeight: "bold",
    color: "#023047",
  },
  stopBox: {
    backgroundColor: "#FBCBCB",
    padding: 20,
    borderRadius: 20,
    marginTop: -160,
    alignSelf: "center",
    width: 147,
    height: 185,
    left: -4,
    justifyContent: "center",
    alignItems: "center",
  },
  stopTextDes: {
    color: "#F67D7D",
    fontSize: 16,
    fontWeight: "medium",
    textAlign: "center",
  },
  stopText: {
    color: "#F02F2F",
    fontSize: 50,
    fontWeight: "700",
    textAlign: "center",
    marginTop: -5,
  },
});
