import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, Animated } from 'react-native';
import { useRouter } from 'expo-router';
import { BleManager } from 'react-native-ble-plx';

export default function SearchingPage() {
  const router = useRouter();
  const manager = new BleManager({
    restoreStateIdentifier: 'skateback-bluetooth',
    restoreStateFunction: (restoredState) => {
      if (restoredState) {
        console.log('Restored state:', restoredState);
      }
    }
  });

  const progressWidth = useRef(new Animated.Value(0.05)).current;
  const scale1 = useRef(new Animated.Value(0)).current;
  const scale2 = useRef(new Animated.Value(0)).current;
  const scale3 = useRef(new Animated.Value(0)).current;

  const [deviceFound, setDeviceFound] = useState(false);
  const [animationDone, setAnimationDone] = useState(false);

  useEffect(() => {
    startScanning();

    // initial progress bar animation (15s)
    Animated.timing(progressWidth, {
      toValue: 1,
      duration: 15000,
      useNativeDriver: false,
    }).start();

    // circle animations
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

    // stop scanning after 15s if nothing is found
    const scanTimeout = setTimeout(() => {
      if (!deviceFound) {
        manager.stopDeviceScan();
        console.log("Scan timed out.");
        router.push('/fail'); 
      }
    }, 15000);  

    return () => {
      manager.stopDeviceScan();
      clearTimeout(scanTimeout);
    };
  }, [progressWidth, scale1, scale2, scale3]);

  const startScanning = () => {
    manager.onStateChange((state) => {
      if (state === 'PoweredOn') {
        console.log('Bluetooth is on, starting scan...');
        manager.startDeviceScan(null, null, (error, device) => {
          if (error) {
            console.error("Error while scanning:", error);
            return;
          }
          
          console.log('Device found:', device);  

          if (device && device.name && device.name.includes("mypi")) {
            console.log("Raspberry Pi found:", device.name); 
            setDeviceFound(true);
            speedUpProgressBar(); 
          }
        });
      } else {
        console.log('Bluetooth state:', state);
        if (state === 'PoweredOff') {
          alert("Please turn on Bluetooth to scan for devices.");
        }
      }
    }, true);
  };

  // speed up the progress bar when device is found
  const speedUpProgressBar = () => {
    Animated.timing(progressWidth, {
      toValue: 1,
      duration: 1500,  
      useNativeDriver: false,
    }).start(() => {
      setAnimationDone(true);
      
      setTimeout(() => {
        router.push({
          pathname: '/device-list',
          params: { devices: 'mypi' }, 
        });
      }, 900); 
    });
  };

  const handleCancelSearch = () => {
    manager.stopDeviceScan();  
    router.push('/instruction');  
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
                outputRange: ['2%', '100%'],
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
            source={require('@skateback/assets/icons/skateboard-search.png')}
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
    backgroundColor: '#fff',
  },
  progressBarContainer: {
    position: 'absolute',
    top: 50,
    left: 50,
    right: 50,
    height: 10,
    backgroundColor: '#D9D9D9',
    borderRadius: 5,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#FC8500',
    borderRadius: 5,
  },
  absoluteTitleContainer: {
    position: 'absolute',
    top: 80,
    left: 50,
    right: 50,
  },
  absoluteContentContainer: {
    position: 'absolute',
    top: 360,
    left: 50,
    right: 60,
    alignItems: 'center',
  },
  circleContainer: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  circle: {
    position: 'absolute',
    width: 600,
    height: 600,
    borderRadius: 300,
    backgroundColor: '#FFB706',
    opacity: 0.2,
  },
  image: {
    width: 297,
    height: 232,
    zIndex: 1,
  },
  absoluteButtonContainer: {
    position: 'absolute',
    bottom: 27,
    left: 0,
    right: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 38,
    fontWeight: 'bold',
    color: '#023047',
    textAlign: 'left',
  },
  button: {
    height: 57,
    width: 319,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 20,
    backgroundColor: '#FB8500',
  },
  buttonText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
});
