import React, { useEffect, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  ImageBackground,
} from "react-native";
import { useRouter } from "expo-router";

export default function WelcomeScreen() {
  const router = useRouter();

  const textPositionY = useRef(new Animated.Value(300)).current;
  const rectangleOpacities = [
    useRef(new Animated.Value(0)).current,
    useRef(new Animated.Value(0)).current,
    useRef(new Animated.Value(0)).current,
    useRef(new Animated.Value(0)).current,
    useRef(new Animated.Value(0)).current,
  ];
  const imageX = useRef(new Animated.Value(500)).current;
  const descriptionOpacity = useRef(new Animated.Value(0)).current;
  const buttonOpacity = useRef(new Animated.Value(0)).current;

  const handlePairSkateboard = () => {
    router.push("/instruction");
  };

  useEffect(() => {
    // 1: slide up headers
    Animated.timing(textPositionY, {
      toValue: 0,
      duration: 1000,
      useNativeDriver: true,
    }).start(() => {
      // 2: fade in rectangles after
      Animated.stagger(
        200,
        rectangleOpacities.map((opacity) =>
          Animated.timing(opacity, {
            toValue: 1,
            duration: 500,
            useNativeDriver: true,
          })
        )
      ).start();

      // 3: slide skateboarder from right
      Animated.timing(imageX, {
        toValue: 0,
        duration: 1000,
        delay: 500,
        useNativeDriver: true,
      }).start();

      // 4: fade in description and button
      Animated.timing(descriptionOpacity, {
        toValue: 1,
        duration: 500,
        delay: 1000,
        useNativeDriver: true,
      }).start();

      Animated.timing(buttonOpacity, {
        toValue: 1,
        duration: 500,
        delay: 1000,
        useNativeDriver: true,
      }).start();
    });
  }, [
    textPositionY,
    rectangleOpacities,
    imageX,
    descriptionOpacity,
    buttonOpacity,
  ]);

  return (
    <View style={styles.container}>
      <Animated.View
        style={[
          styles.firstContainer,
          { transform: [{ translateY: textPositionY }] },
        ]}
      >
        <Text style={styles.subtitle}>Welcome to</Text>
        <Text style={styles.title}>SkateBack</Text>
        <Text style={styles.subtitle}>Ride Freely, Return Easily.</Text>
      </Animated.View>

      <View style={styles.secondContainer}>
        <View style={styles.rectangleContainer}>
          {rectangleOpacities.map((opacity, index) => (
            <Animated.View
              key={index}
              style={[
                styles.rectangle,
                styles[`rectangle${index + 1}`],
                { opacity, marginHorizontal: 2.5 },
              ]}
            />
          ))}
        </View>

        <Animated.Image
          source={require("@skateback/assets/images/skateboarder.png")}
          style={[styles.image, { transform: [{ translateX: imageX }] }]}
        />
      </View>

      <View style={styles.thirdContainer}>
        <Animated.Text
          style={[styles.description, { opacity: descriptionOpacity }]}
        >
          Easily <Text style={styles.boldText}>control</Text> your skateboard,
          <Text style={styles.boldText}> track</Text> performance, and use the
          <Text style={styles.boldText}> 'return to me'</Text> feature for quick
          retrieval.
        </Animated.Text>

        <Animated.View style={{ opacity: buttonOpacity }}>
          <TouchableOpacity onPress={handlePairSkateboard}>
            <ImageBackground
              source={require("@skateback/assets/images/button-color.png")}
              style={styles.button}
              resizeMode="cover"
              imageStyle={styles.buttonImage}
            >
              <Text style={styles.buttonText}>Pair Skateboard</Text>
            </ImageBackground>
          </TouchableOpacity>
        </Animated.View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
  },
  firstContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "flex-start",
    paddingLeft: 50,
    paddingTop: 25,
    paddingBottom: 10,
  },
  secondContainer: {
    height: 468,
    justifyContent: "center",
    alignItems: "center",
    position: "relative",
  },
  rectangleContainer: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    width: "100%",
  },
  rectangle: {
    width: 55,
    height: 500,
  },
  rectangle1: {
    backgroundColor: "#8ECAE6",
  },
  rectangle2: {
    backgroundColor: "#219EBC",
  },
  rectangle3: {
    backgroundColor: "#023047",
  },
  rectangle4: {
    backgroundColor: "#FFB703",
  },
  rectangle5: {
    backgroundColor: "#FB8500",
  },
  title: {
    fontSize: 38,
    fontWeight: "bold",
    color: "#023047",
  },
  subtitle: {
    fontSize: 18,
    color: "#023047",
    marginBottom: 10,
  },
  image: {
    width: 372,
    height: 426,
    position: "absolute",
    left: 78,
    top: 56,
    zIndex: 1,
  },
  thirdContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 12,
    paddingBottom: 10,
  },
  description: {
    paddingHorizontal: 48,
    textAlign: "center",
    marginTop: 5,
    marginBottom: 5,
    fontSize: 12,
    color: "#818590",
  },
  boldText: {
    fontWeight: "bold",
    color: "#818590",
  },
  button: {
    height: 57,
    width: 319,
    justifyContent: "center",
    alignItems: "center",
    borderRadius: 20,
    overflow: "hidden",
  },
  buttonImage: {
    borderRadius: 20,
  },
  buttonText: {
    color: "#fff",
    fontSize: 20,
    fontWeight: "bold",
  },
});
