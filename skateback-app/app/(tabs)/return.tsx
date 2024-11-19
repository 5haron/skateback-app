import React, { useRef, useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  Animated,
  Platform,
} from "react-native";
import MapView, { Marker } from "react-native-maps";
import Icon from "react-native-vector-icons/FontAwesome";
import Geolocation from "react-native-geolocation-service";
import {
  PERMISSIONS,
  request,
  check,
  RESULTS,
  Permission,
} from "react-native-permissions";
import haversine from "haversine";

type Coordinates = {
  latitude: number;
  longitude: number;
  accuracy?: number;
};

// CMU coordinates
const cmuLat = 40.4435;
const cmuLon = -79.9437;

const destLat = 40.4435;
const destLon = -79.9436;

const calculateDistance = (
  startCoords: Coordinates,
  destCoords: Coordinates
): number => {
  return haversine(startCoords, destCoords, { unit: "meter" });
};

export default function ReturnToMeScreen() {
  const mapRef = useRef<MapView | null>(null);

  const distance = calculateDistance(
    { latitude: cmuLat, longitude: cmuLon },
    { latitude: cmuLat, longitude: destLon }
  );

   // return frontend
  const [returnStarted, setReturnStarted] = useState(false);
  const [eta, setEta] = useState(10);
  const [progress, setProgress] = useState(new Animated.Value(0));
  const [myLocation, setMyLocation] = useState<Coordinates | null>(null);

  // request location permission
  const requestLocationPermission = async () => {
    const permissionType = Platform.select({
      ios: PERMISSIONS.IOS.LOCATION_ALWAYS,
      android: PERMISSIONS.ANDROID.ACCESS_FINE_LOCATION,
    }) as Permission;

    if (!permissionType) {
      console.warn("Location permission type not supported");
      return false;
    }

    const permissionStatus = await check(permissionType);

    if (permissionStatus === RESULTS.GRANTED) {
      return true;
    }

    if (
      permissionStatus === RESULTS.DENIED ||
      permissionStatus === RESULTS.LIMITED
    ) {
      const result = await request(permissionType);
      return result === RESULTS.GRANTED;
    }

    console.warn("Location permission denied");
    return false;
  };

  useEffect(() => {
    const startWatchingLocation = async () => {
      const hasPermission = await requestLocationPermission();
      if (hasPermission) {
        const watchId = Geolocation.watchPosition(
          (position) => {
            const { latitude, longitude, accuracy } = position.coords;
            setMyLocation({
              latitude,
              longitude,
              accuracy,
            });

            // Log with accuracy
            console.log("Location update:", {
              accuracy: accuracy
                ? `${accuracy.toFixed(2)}m (${getAccuracyLevel(accuracy)})`
                : "unknown",
              coords: `${latitude}, ${longitude}`,
            });
          },
          (error) => console.error(error),
          {
            enableHighAccuracy: true,
            distanceFilter: 0,
            interval: 500,
            fastestInterval: 200,
          }
        );

        return () => Geolocation.clearWatch(watchId);
      }
    };

    startWatchingLocation();
  }, []);

  const getAccuracyLevel = (accuracy: number) => {
    if (accuracy <= 5) return "Excellent";
    if (accuracy <= 10) return "Very Good";
    if (accuracy <= 20) return "Good";
    if (accuracy <= 50) return "Moderate";
    return "Poor";
  };

  const getAccuracyColor = (accuracy: number) => {
    if (accuracy <= 5) return "#00C853"; // Green
    if (accuracy <= 10) return "#64DD17"; // Light Green
    if (accuracy <= 20) return "#FFD600"; // Yellow
    if (accuracy <= 50) return "#FF9100"; // Orange
    return "#FF1744"; // Red
  };

  useEffect(() => {
    let interval: any;

    if (returnStarted && eta > 0) {
      interval = setInterval(() => {
        setEta((prevEta) => {
          if (prevEta > 0) {
            return prevEta - 1;
          } else {
            clearInterval(interval);
            return 0;
          }
        });
      }, 1000);

      Animated.timing(progress, {
        toValue: 1,
        duration: eta * 1000,
        useNativeDriver: false,
      }).start();
    }

    return () => clearInterval(interval);
  }, [returnStarted, eta]);

  const handleReturnToggle = () => {
    if (returnStarted) {
      setReturnStarted(false);
      setEta(2);
      setProgress(new Animated.Value(0));
    } else {
      setReturnStarted(true);
    }
  };

  const calculateMidpoint = (coord1: Coordinates, coord2: Coordinates) => {
    return {
      latitude: (coord1.latitude + coord2.latitude) / 2,
      longitude: (coord1.longitude + coord2.longitude) / 2,
    };
  };

  const calculateDeltas = (coord1: Coordinates, coord2: Coordinates) => {
    const padding = 1.5; // Adds some padding around the pins
    const latDelta = Math.abs(coord1.latitude - coord2.latitude) * padding;
    const lonDelta = Math.abs(coord1.longitude - coord2.longitude) * padding;
    return {
      latitudeDelta: Math.max(latDelta, 0.0005), // Minimum zoom level
      longitudeDelta: Math.max(lonDelta, 0.0005), // Minimum zoom level
    };
  };

  const recenterMap = () => {
    if (mapRef.current) {
      const userLocation = myLocation || {
        latitude: cmuLat,
        longitude: cmuLon,
      };
      const skateboardLocation = { latitude: destLat, longitude: destLon };

      const center = calculateMidpoint(userLocation, skateboardLocation);
      const deltas = calculateDeltas(userLocation, skateboardLocation);

      mapRef.current.animateToRegion(
        {
          latitude: center.latitude,
          longitude: center.longitude,
          ...deltas,
        },
        1000
      );
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.headerContainer}>
        <Text style={styles.title}>Return to Me</Text>
      </View>

      <TouchableOpacity
        style={[styles.button, distance > 122 && styles.buttonDisabled]}
        onPress={handleReturnToggle}
        disabled={distance > 122}
      >
        <Text style={styles.buttonText}>
          {eta === 0
            ? "Return Successful!"
            : returnStarted
              ? "Cancel Return"
              : "Start Return"}
        </Text>
      </TouchableOpacity>

      <View style={styles.mapContainer}>
        {eta === 0 ? (
          <View style={styles.mapReplacement}>
            <Image
              source={require("@skateback/assets/images/success-return.png")}
              style={styles.successImage}
              resizeMode="contain"
            />
          </View>
        ) : (
          <MapView
            ref={mapRef}
            style={styles.map}
            initialRegion={{
              ...calculateMidpoint(
                { latitude: cmuLat, longitude: cmuLon },
                { latitude: destLat, longitude: destLon }
              ),
              ...calculateDeltas(
                { latitude: cmuLat, longitude: cmuLon },
                { latitude: destLat, longitude: destLon }
              ),
            }}
          >
            {myLocation && (
              <Marker
                coordinate={myLocation}
                title="My Location"
                description="Current position"
                pinColor="blue"
              />
            )}
            <Marker
              coordinate={{ latitude: destLat, longitude: destLon }}
              title="Skateboard"
              description="Skateboard location"
              pinColor="red"
            />
          </MapView>
        )}

        {eta !== 0 && (
          <TouchableOpacity style={styles.recenterButton} onPress={recenterMap}>
            <Icon name="location-arrow" size={25} color="#023047" />
          </TouchableOpacity>
        )}
      </View>

      {returnStarted && eta > 0 && (
        <View style={styles.progressBarContainer}>
          <Animated.View
            style={[
              styles.progressBar,
              {
                width: progress.interpolate({
                  inputRange: [0, 1],
                  outputRange: ["0%", "100%"],
                }),
              },
            ]}
          />
        </View>
      )}

      {eta === 0 && (
        <View style={styles.progressBarContainer}>
          <View style={styles.fullProgressBar} />
          <Image
            source={require("@skateback/assets/icons/checked-2.png")}
            style={styles.checkIcon}
            resizeMode="contain"
          />
        </View>
      )}

      {eta !== 0 && (
        <View style={styles.infoContainer}>
          <Text style={styles.infoText}>
            <Text style={styles.boldText}>Distance:</Text>
            <Text
              style={[styles.distanceText, distance > 122 && styles.redText]}
            >
              {" "}
              {distance.toFixed(2)} meters
            </Text>
          </Text>

          <Text style={styles.infoText}>
            <Text style={styles.boldText}>ETA:</Text> {eta} second
            {eta !== 1 ? "s" : ""}
          </Text>
          <Text style={styles.infoText}>
            <Text style={styles.boldText}>My Location:</Text>{" "}
            {myLocation
              ? `${myLocation.latitude}, ${myLocation.longitude}`
              : "Fetching..."}
          </Text>
          <Text style={styles.infoText}>
            <Text style={styles.boldText}>Accuracy:</Text>{" "}
            {myLocation?.accuracy ? (
              <Text
                style={[
                  styles.accuracyText,
                  { color: getAccuracyColor(myLocation.accuracy) },
                ]}
              >
                ±{myLocation.accuracy.toFixed(2)} meters (
                {getAccuracyLevel(myLocation.accuracy)})
              </Text>
            ) : (
              "Unknown"
            )}
          </Text>
          <Text style={styles.infoText}>
            <Text style={styles.boldText}>Skateboard Location:</Text>{" "}
            {skateboardLocation
              ? `${skateboardLocation.latitude}, ${skateboardLocation.longitude}`
              : "Connecting..."}
          </Text>
        </View>
      )}

      {distance > 122 && (
        <View style={styles.warningContainer}>
          <View style={styles.overlayRectangle} />
          <View style={styles.warningContent}>
            <View style={styles.warningRow}>
              <Image
                source={require("@skateback/assets/icons/warning.png")}
                style={styles.customIcon}
              />
              <Text style={styles.warningTitle}>Skateboard Out of Range</Text>
            </View>
            <Text style={styles.warningText}>
              The skateboard is too far away for the Return to Me feature to
              work. Please move closer or manually retrieve the skateboard.
            </Text>
          </View>
        </View>
      )}
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
    marginBottom: 16,
  },
  button: {
    backgroundColor: "#8ECAE6",
    borderRadius: 20,
    padding: 20,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 30,
    marginHorizontal: 20,
    marginTop: -5,
  },
  buttonDisabled: {
    backgroundColor: "#C1C1C1",
  },
  buttonText: {
    fontSize: 21,
    fontWeight: "bold",
    color: "#023047",
  },
  mapContainer: {
    height: 400,
    borderRadius: 20,
    overflow: "hidden",
    marginBottom: 16,
    marginHorizontal: 20,
  },
  map: {
    flex: 1,
  },
  mapReplacement: {
    flex: 1,
    backgroundColor: "#E8F4FA",
    justifyContent: "center",
    alignItems: "center",
  },
  successImage: {
    width: 350,
    height: 350,
  },
  recenterButton: {
    position: "absolute",
    bottom: 10,
    right: 10,
    backgroundColor: "transparent",
    borderRadius: 30,
    width: 40,
    height: 40,
    justifyContent: "center",
    alignItems: "center",
    elevation: 3,
  },
  progressBarContainer: {
    height: 20,
    width: "90%",
    backgroundColor: "#D9D9D9",
    borderRadius: 10,
    marginHorizontal: "5%",
    marginBottom: 15,
    marginTop: 5,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  progressBar: {
    height: "100%",
    backgroundColor: "#FFB706",
    borderRadius: 10,
  },
  fullProgressBar: {
    height: "100%",
    width: "100%",
    backgroundColor: "#FFB706",
    borderRadius: 10,
  },
  checkIcon: {
    width: 20,
    height: 20,
    position: "absolute",
    right: 0,
    top: 25,
  },
  infoContainer: {
    alignItems: "flex-end",
  },
  infoText: {
    fontSize: 16,
    color: "#023047",
    textAlign: "right",
    marginBottom: 2,
    marginHorizontal: 20,
  },
  boldText: {
    fontWeight: "bold",
  },
  distanceText: {
    color: "#023047",
  },
  redText: {
    color: "#FF0000",
    fontWeight: "bold",
  },
  warningContainer: {
    backgroundColor: "#E8F4FA",
    marginHorizontal: 20,
    marginTop: 10,
    position: "relative",
  },
  warningContent: {
    padding: 17,
    paddingLeft: 30,
    paddingRight: 15,
  },
  warningRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 4,
  },
  warningTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#023047",
    marginLeft: 8,
  },
  warningText: {
    fontSize: 14,
    color: "#023047",
  },
  overlayRectangle: {
    position: "absolute",
    left: 0,
    top: 0,
    width: 15,
    height: "100%",
    backgroundColor: "#BBDFF0",
  },
  customIcon: {
    width: 34,
    height: 34,
  },
  accuracyText: {
    fontWeight: "bold",
  },
});
