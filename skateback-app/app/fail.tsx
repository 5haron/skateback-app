import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image } from 'react-native';
import { useRouter } from 'expo-router';

export default function FailPage() {
  const router = useRouter();

  const handleRetrySearch = () => {
    router.push('/searching'); 
  };

  return (
    <View style={styles.container}>
      <View style={styles.progressBarContainer}>
        <View style={styles.progressBar} />
        <Image
          source={require('@skateback/assets/icons/remove.png')} 
          style={styles.removeIcon}
        />
      </View>

      <View style={styles.absoluteTitleContainer}>
        <Text style={styles.title}>No Devices Found</Text>
      </View>

      <View style={styles.absoluteContentContainer}>
        <Text style={styles.instructionText}>
          Make sure your skateboard is powered on and nearby. Check if Bluetooth is enabled on your phone.
        </Text>

        <Image
          source={require('@skateback/assets/images/fail.png')}
          style={styles.image}
        />
      </View>

      <View style={styles.absoluteButtonContainer}>
        <TouchableOpacity onPress={handleRetrySearch} style={styles.button}>
          <Text style={styles.buttonText}>Retry Search</Text>
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
  },
  progressBar: {
    width: '100%',
    height: '100%',
    backgroundColor: '#FC8500',
    borderRadius: 5,
  },
  removeIcon: {
    position: 'absolute',
    right: 0,
    top: 13,
    width: 17,
    height: 20,
    resizeMode: 'contain',
  },
  absoluteTitleContainer: {
    position: 'absolute',
    top: 80,
    left: 50,
  },
  absoluteContentContainer: {
    position: 'absolute',
    top: 140,
    left: 50,
    right: 50,
  },
  image: {
    width: 297,     
    height: 300,      
    position: 'absolute', 
    top: 150, 
    left: 20,
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
  },
  instructionText: {
    fontSize: 16,
    fontFamily: 'Inter',
    color: '#777777',
    lineHeight: 20,
    marginBottom: 20,
  },
  button: {
    height: 57,
    width: 319,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 20,
    backgroundColor: '#FB8500', 
    borderWidth: 0,
  },
  buttonText: {
    color: '#FFFFFF', 
    fontSize: 20,
    fontWeight: 'bold',
  },
});
