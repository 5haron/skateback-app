import React, { useEffect, useRef, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  Animated,
  Alert,
} from "react-native";
import { useRouter } from "expo-router";
import { BleManager } from "react-native-ble-plx";

const log = (...args) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}]`, ...args);
};

export default function SearchingPage() {
  const router = useRouter();
  const [manager] = useState(() => new BleManager());
  const [isScanning, setIsScanning] = useState(false);
  const [availableDevices, setAvailableDevices] = useState([]);
  const [progressFast, setProgressFast] = useState(false);

  const progressWidth = useRef(new Animated.Value(0.05)).current;
  const scale1 = useRef(new Animated.Value(0)).current;
  const scale2 = useRef(new Animated.Value(0)).current;
  const scale3 = useRef(new Animated.Value(0)).current;

  const startScanning = async () => {
    try {
      const state = await manager.state();
      log("Current Bluetooth state:", state);

      if (state !== "PoweredOn") {
        Alert.alert(
          "Bluetooth Required",
          "Please enable Bluetooth to scan for devices"
        );
        return;
      }

      if (isScanning) {
        log("Already scanning...");
        return;
      }

      setIsScanning(true);
      log("Starting scan for devices...");

      // Start scanning for devices
      manager.startDeviceScan(
        null, // No UUID filter initially
        { allowDuplicates: false },
        (error, device) => {
          if (error) {
            log("Scanning error:", error);
            setIsScanning(false);
            return;
          }

          // Only add devices with the name "mypi" to the list
          if (device && device.name === "mypi") {
            log("Found device:", {
              name: device.name,
              id: device.id,
              serviceUUIDs: device.serviceUUIDs,
              localName: device.localName,
              rssi: device.rssi,
            });

            // Add only the name if it's unique
            setAvailableDevices((prevDevices) => {
              if (!prevDevices.includes(device.name)) {
                setProgressFast(true); // Trigger fast animation
                return [...prevDevices, device.name];
              }
              return prevDevices;
            });
          }
        }
      );
    } catch (error) {
      log("Error in startScanning:", error);
      setIsScanning(false);
    }
  };

  // Trigger navigation when availableDevices has entries
  useEffect(() => {
    if (availableDevices.length > 0) {
      manager.stopDeviceScan();
      setIsScanning(false);

      // Wait 3 seconds before navigating to device-list
      setTimeout(() => {
        router.push({
          pathname: "/device-list",
          params: { devices: JSON.stringify(availableDevices) },
        });
      }, 2000); // 3-second delay
    }
  }, [availableDevices, router, manager]);

  useEffect(() => {
    const subscription = manager.onStateChange((state) => {
      log("Bluetooth state changed:", state);
      if (state === "PoweredOn" && !isScanning) {
        startScanning();
      }
    }, true);

    // initial progress bar animation (10s)
    Animated.timing(progressWidth, {
      toValue: 1,
      duration: 10000,
      useNativeDriver: false,
    }).start();

    // Set timeout to stop scanning after 10 seconds if no devices are found
    const scanTimeout = setTimeout(() => {
      if (availableDevices.length === 0) {
        manager.stopDeviceScan();
        setIsScanning(false);
        router.push("/fail");
      }
    }, 10000);

    // Circle animations
    const animateCircle = (scale) => {
      Animated.loop(
        Animated.sequence([
          Animated.timing(scale, {
            toValue: 1,
            duration: 1500,
            useNativeDriver: true,
          }),
          Animated.timing(scale, {
            toValue: 0,
            duration: 1500,
            useNativeDriver: true,
          }),
        ])
      ).start();
    };

    animateCircle(scale1);
    animateCircle(scale2);
    setTimeout(() => animateCircle(scale3), 500);

    // Cleanup on unmount
    return () => {
      log("Cleaning up...");
      subscription.remove();
      manager.stopDeviceScan();
      clearTimeout(scanTimeout);
      manager.destroy();
    };
  }, []);

  // Trigger faster progress bar animation when mypi is found
  useEffect(() => {
    if (progressFast) {
      Animated.timing(progressWidth, {
        toValue: 1,
        duration: 3000, // Speed up to reach 100% in 3 seconds
        useNativeDriver: false,
      }).start();
    }
  }, [progressFast]);

  const handleCancelSearch = () => {
    manager.stopDeviceScan();
    setIsScanning(false);
    router.push("/instruction");
  };

  return (
    <View style={styles.container}>
      <View style={styles.progressBarContainer}>
        <Animated.View
          style={[
            styles.progressBar,
            {
              width: progressWidth.interpolate({
                inputRange: [0, 1],
                outputRange: ["2%", "100%"],
              }),
            },
          ]}
        />
      </View>

      <View style={styles.absoluteTitleContainer}>
        <Text style={styles.title}>Looking for Skateboards...</Text>
      </View>

      <View style={styles.absoluteContentContainer}>
        <View style={styles.circleContainer}>
          <Animated.View
            style={[styles.circle, { transform: [{ scale: scale1 }] }]}
          />
          <Animated.View
            style={[styles.circle, { transform: [{ scale: scale2 }] }]}
          />
          <Animated.View
            style={[styles.circle, { transform: [{ scale: scale3 }] }]}
          />
          <Image
            source={require("@skateback/assets/icons/skateboard-search.png")}
            style={styles.image}
          />
        </View>
      </View>

      <View style={styles.absoluteButtonContainer}>
        <TouchableOpacity onPress={handleCancelSearch} style={styles.button}>
          <Text style={styles.buttonText}>Cancel Search</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
  },
  progressBarContainer: {
    position: "absolute",
    top: 50,
    left: 50,
    right: 50,
    height: 10,
    backgroundColor: "#D9D9D9",
    borderRadius: 5,
    overflow: "hidden",
  },
  progressBar: {
    height: "100%",
    backgroundColor: "#FC8500",
    borderRadius: 5,
  },
  absoluteTitleContainer: {
    position: "absolute",
    top: 80,
    left: 50,
    right: 50,
  },
  absoluteContentContainer: {
    position: "absolute",
    top: 360,
    left: 50,
    right: 60,
    alignItems: "center",
  },
  circleContainer: {
    justifyContent: "center",
    alignItems: "center",
  },
  circle: {
    position: "absolute",
    width: 600,
    height: 600,
    borderRadius: 300,
    backgroundColor: "#FFB706",
    opacity: 0.2,
  },
  image: {
    width: 297,
    height: 232,
    zIndex: 1,
  },
  absoluteButtonContainer: {
    position: "absolute",
    bottom: 27,
    left: 0,
    right: 0,
    justifyContent: "center",
    alignItems: "center",
  },
  title: {
    fontSize: 38,
    fontWeight: "bold",
    color: "#023047",
    textAlign: "left",
  },
  button: {
    height: 57,
    width: 319,
    justifyContent: "center",
    alignItems: "center",
    borderRadius: 20,
    backgroundColor: "#FB8500",
  },
  buttonText: {
    color: "#fff",
    fontSize: 20,
    fontWeight: "bold",
  },
});
