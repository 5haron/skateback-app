import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image } from 'react-native';
import { useRouter } from 'expo-router';

export default function SearchingPage() {
  const router = useRouter();

  const handleCancelSearch = () => {
    router.push('/device-list');
  };

  return (
    <View style={styles.container}>
      <View style={styles.progressBarContainer}>
        <View style={styles.progressBar} />
      </View>

      <View style={styles.absoluteTitleContainer}>
        <Text style={styles.title}>Looking for Skateboards...</Text>
      </View>

      <View style={styles.absoluteContentContainer}>
        <Image
          source={require('@skateback/assets/icons/skateboard-search.png')}
          style={styles.image}
        />
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
  },
  progressBar: {
    width: '30%', 
    height: '100%',
    backgroundColor: '#FC8500', 
    borderRadius: 5,
  },
  absoluteTitleContainer: {
    position: 'absolute',
    top: 80, 
    left: 50,
    right: 50
  },
  absoluteContentContainer: {
    position: 'absolute',
    top: 200,
    left: 50, 
    right: 70,
  },
  image: {
    width: 297,     
    height: 232,      
    position: 'absolute', 
    top: 170, 
    left: 10,
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
