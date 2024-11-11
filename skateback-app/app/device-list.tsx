import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  TouchableWithoutFeedback,
} from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";

export default function DeviceListPage() {
  const router = useRouter();
  const { devices } = useLocalSearchParams();
  const [selectedSkateboard, setSelectedSkateboard] = useState(null);
  const [isConnecting, setIsConnecting] = useState(false);

  const deviceNames = devices ? JSON.parse(devices) : [];

  useEffect(() => {
    if (!deviceNames.length) {
      router.push("/fail");
    }
  }, [deviceNames, router]);

  const handleSelectSkateboard = (skateboard) => {
    if (!isConnecting) {
      setSelectedSkateboard(
        selectedSkateboard === skateboard ? null : skateboard
      );
    }
  };

  const handleButtonClick = () => {
    if (isConnecting) {
      setIsConnecting(false);
      setSelectedSkateboard(null);
    } else {
      setIsConnecting(true);

      setTimeout(() => {
        router.push({
          pathname: "/success",
          params: { skateboard: selectedSkateboard },
        });
      }, 1000);
    }
  };

  const renderButtons = () => {
    return deviceNames.map((device, index) => {
      const isSelected = selectedSkateboard === device;
      const buttonColor = ["#8ECAE6", "#229EBC", "#FFB706", "#FB8500"][
        index % 4
      ];

      return (
        <TouchableOpacity
          key={device + index}
          style={[
            styles.deviceButton,
            {
              borderColor: isSelected
                ? buttonColor
                : selectedSkateboard
                  ? "#D9D9D9"
                  : buttonColor,
              backgroundColor: isSelected ? buttonColor : "#FFFFFF",
              opacity: selectedSkateboard && !isSelected ? 0.3 : 1,
            },
          ]}
          onPress={() => handleSelectSkateboard(device)}
        >
          <Image
            source={require("@skateback/assets/icons/skateboard.png")}
            style={styles.icon}
          />
          <Text style={styles.deviceButtonText}>{device}</Text>
          {isSelected && isConnecting && (
            <ActivityIndicator
              size="small"
              color="#000000"
              style={styles.loader}
            />
          )}
        </TouchableOpacity>
      );
    });
  };

  return (
    <TouchableWithoutFeedback onPress={() => setSelectedSkateboard(null)}>
      <View style={styles.container}>
        <View style={styles.progressBarContainer}>
          <View style={styles.progressBar} />
        </View>

        <View style={styles.absoluteTitleContainer}>
          <Text style={styles.title}>
            {isConnecting ? "Connecting..." : "Devices Found"}
          </Text>
        </View>

        <View style={styles.absoluteContentContainer}>
          <Text style={styles.instructionText}>
            {isConnecting
              ? "Hang tight! Connecting to your skateboard."
              : "Select your skateboard to connect."}
          </Text>
          <View style={styles.deviceButtonContainer}>{renderButtons()}</View>
        </View>

        {selectedSkateboard && (
          <View style={styles.absoluteButtonContainer}>
            <TouchableOpacity onPress={handleButtonClick} style={styles.button}>
              <Text style={styles.buttonText}>
                {isConnecting ? "Stop Connecting" : "Connect to Skateboard"}
              </Text>
            </TouchableOpacity>
          </View>
        )}
      </View>
    </TouchableWithoutFeedback>
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
  },
  progressBar: {
    width: "100%",
    height: "100%",
    backgroundColor: "#FC8500",
    borderRadius: 5,
  },
  checkedIcon: {
    position: "absolute",
    right: 0,
    top: 15,
    width: 18,
    height: 20,
    resizeMode: "contain",
  },
  absoluteTitleContainer: {
    position: "absolute",
    top: 80,
    left: 50,
  },
  absoluteContentContainer: {
    position: "absolute",
    top: 140,
    left: 50,
    right: 50,
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
  },
  instructionText: {
    fontSize: 16,
    fontFamily: "Inter",
    color: "#777777",
    lineHeight: 20,
    marginBottom: 20,
  },
  deviceButtonContainer: {
    flexDirection: "column",
    justifyContent: "space-between",
    marginTop: -10,
  },
  deviceButton: {
    flexDirection: "row",
    alignItems: "center",
    borderWidth: 2,
    padding: 10,
    width: "100%",
    marginBottom: 10,
    borderRadius: 0,
  },
  deviceButtonText: {
    fontSize: 17,
    fontFamily: "Inter",
    color: "#023047",
    marginLeft: 8,
  },
  icon: {
    width: 25,
    height: 25,
    resizeMode: "contain",
  },
  loader: {
    marginLeft: "auto",
    marginRight: 10,
  },
  button: {
    height: 57,
    width: 319,
    justifyContent: "center",
    alignItems: "center",
    borderRadius: 20,
    backgroundColor: "#FB8500",
    borderWidth: 0,
  },
  buttonText: {
    color: "#FFFFFF",
    fontSize: 20,
    fontWeight: "bold",
  },
});
