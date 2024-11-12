import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, Image } from "react-native";
import { useRouter } from "expo-router";

export default function InstructionPage() {
  const router = useRouter();

  const handleStartSearch = () => {
    router.push("/searching");
  };

  const instructions = [
    "Make sure Bluetooth is enabled.",
    "Turn on your skateboard and stay within a meter of your skateboard.",
    "Click 'Start Search' to find your device.",
  ];

  return (
    <View style={styles.container}>
      <View style={styles.progressBarContainer}>
        <View style={styles.progressBar} />
      </View>

      <View style={styles.absoluteTitleContainer}>
        <Text style={styles.title}>Connect Your Skateboard</Text>
      </View>

      <View style={styles.absoluteInstructionsContainer}>
        {instructions.map((instruction, index) => (
          <View key={index} style={styles.instructionContainer}>
            <Text style={styles.instructionNumber}>{index + 1}.</Text>
            <Text style={styles.instructionText}>{instruction}</Text>
          </View>
        ))}
        <Image
          source={require("@skateback/assets/icons/skateboard-search.png")}
          style={styles.image}
        />
      </View>

      <View style={styles.absoluteButtonContainer}>
        <TouchableOpacity onPress={handleStartSearch} style={styles.button}>
          <Text style={styles.buttonText}>Start Search</Text>
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
  },
  progressBar: {
    width: "5%",
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
  absoluteInstructionsContainer: {
    position: "absolute",
    top: 200,
    left: 50,
    right: 70,
  },
  instructionContainer: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginBottom: 13,
  },
  instructionNumber: {
    fontSize: 15,
    fontFamily: "Inter",
    color: "#777777",
    lineHeight: 20,
    marginRight: 8,
  },
  instructionText: {
    fontSize: 16,
    fontFamily: "Inter",
    color: "#777777",
    lineHeight: 20,
  },
  image: {
    width: 297,
    height: 232,
    position: "absolute",
    top: 170,
    left: 10,
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
