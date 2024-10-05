import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import haversine from 'haversine';

// cmu coords
const cmuLat = 40.4435;
const cmuLon= -79.9437; 

const destLat = 40.4435; 
const destLon = -79.9436;

const calculateDistance = (startCoords, destCoords) => {
  return haversine(startCoords, destCoords, { unit: 'meter' });
};

export default function ReturnToMeScreen() {
  const distance = calculateDistance(
    { latitude: cmuLat, longitude: cmuLon },
    { latitude: cmuLat, longitude: destLon }
  ).toFixed(4);

  return (
    <View style={styles.container}>
        <View style={styles.headerContainer}>
          <Text style={styles.title}>Return to Me</Text>
        </View>
      
      <TouchableOpacity style={styles.button}>
        <Text style={styles.buttonText}>Start Return</Text>
      </TouchableOpacity>

      <View style={styles.mapContainer}>
        <MapView
          style={styles.map}
          initialRegion={{
            latitude: cmuLat,
            longitude: cmuLon,
            latitudeDelta: 0.0005, 
            longitudeDelta: 0.0005, 
          }}>
          <Marker coordinate={{ latitude: cmuLat, longitude: cmuLon }} />
          <Marker coordinate={{ latitude: destLat, longitude: destLon }} />
        </MapView>
      </View>

      <View style={styles.infoContainer}>
        <Text style={styles.infoText}>
          <Text style={styles.boldText}>Distance:</Text> {distance} meters
        </Text>
        <Text style={styles.infoText}>
          <Text style={styles.boldText}>ETA:</Text> 2 minutes
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff', 
    padding: 16,
  },
  headerContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 10,
  },
  title: {
    fontSize: 26,
    fontWeight: 'bold',
    color: '#023047',
    marginBottom: 16,
  },
  button: {
    backgroundColor: '#8ECAE6',
    borderRadius: 20,
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 30,
    marginHorizontal: 20,
    marginTop: -5
  },
  buttonText: {
    fontSize: 21,
    fontWeight: 'bold',
    color: '#023047',
  },
  mapContainer: {
    height: 400, 
    borderRadius: 20,
    overflow: 'hidden',
    marginBottom: 16,
    marginHorizontal: 20
  },
  map: {
    flex: 1,
  },
  infoContainer: {
    alignItems: 'flex-end',
  },
  infoText: {
    fontSize: 16,
    color: '#023047',
    textAlign: 'right', 
    marginBottom: 2, 
    marginHorizontal: 20,
  },
  boldText: {
    fontWeight: 'bold',
  }
});
