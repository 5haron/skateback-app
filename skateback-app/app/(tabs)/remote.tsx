import React, { useState } from "react";
import {
  View,
  Text,
  Image,
  StyleSheet,
  TouchableOpacity,
  Switch,
} from "react-native";
import axios from "axios";
import { useLocalSearchParams } from "expo-router";

const API_BASE_URL = "http://172.26.54.250:3000";

export default function RemoteControlScreen() {
  const [isReverse, setIsReverse] = useState(false);
  const [batteryPercentage, setBatteryPercentage] = useState(100);
  const { skateboardName } = useLocalSearchParams();

  const handleAccelerate = async () => {
    try {
      await axios.post(`${API_BASE_URL}/accelerate`);
    } catch (error) {
      console.error("Error accelerating", error);
    }
  };

  const handleDecelerate = async () => {
    try {
      await axios.post(`${API_BASE_URL}/decelerate`);
    } catch (error) {
      console.error("Error decelerating", error);
    }
  };

  const handleReverse = async (isReverse: boolean) => {
    try {
      await axios.post(`${API_BASE_URL}/reverse`, { reverse: isReverse });
      console.log(`Reverse ${isReverse ? "on" : "off"}`);
    } catch (error) {
      console.error("Error toggling reverse", error);
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
        <Text style={styles.statValue}>7</Text>
        <Text style={styles.statLabel}>mph</Text>
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
          {/* <Text style={styles.batteryLabel}>{batteryPercentage}%</Text> */}

          <View style={styles.batteryRectangleContainer}>
            {renderBatteryRectangles()}
          </View>
          <TouchableOpacity
            style={styles.stopBox}
            onPress={() => console.log("Stop button pressed")}
          >
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

          <View style={styles.reverseContainer}>
            <Text style={styles.reverseText}>Reverse</Text>
            <Switch
              value={isReverse}
              onValueChange={(value) => {
                setIsReverse(value);
                handleReverse(value);
              }}
              trackColor={{ false: "#ccc", true: "#8ECAE6" }}
              thumbColor={isReverse ? "#023047" : "#f4f3f4"}
            />
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
    paddingHorizontal: 10,
    marginLeft: 20,
  },
  statLabel: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#023047",
    marginTop: -14,
    textAlign: "center",
  },
  statValue: {
    fontSize: 90,
    fontWeight: "bold",
    color: "#023047",
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
  // batteryLabel: {
  //   position: "absolute",
  //   top: 270,
  //   width: 159,
  //   textAlign: "center",
  //   fontSize: 28,
  //   color: "white",
  //   fontWeight: "bold",
  // },
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
  },
  buttonText: {
    fontSize: 120,
    fontWeight: "bold",
    color: "#023047",
  },
  reverseContainer: {
    flexDirection: "row",
    justifyContent: "flex-start",
    alignItems: "center",
  },
  reverseText: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#023047",
    marginRight: 10,
    marginLeft: 25,
  },
  switchWrapper: {
    flexDirection: "row",
    alignItems: "center",
  },
  switch: {
    width: 60,
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
