import React from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity, ImageBackground } from 'react-native';
import { useRouter } from 'expo-router';

export default function WelcomeScreen() {
  const router = useRouter(); 

  const handlePairSkateboard = () => {
    router.push('/remote');
  };

  return (
    <View style={styles.container}>
      <View style={styles.firstContainer}>
        <Text style={styles.subtitle}>Welcome to</Text>
        <Text style={styles.title}>SkateBack</Text>
        <Text style={styles.subtitle}>Ride Freely, Return Easily.</Text>
      </View>

      <View style={styles.secondContainer}>
        <View style={styles.rectangleContainer}>
          <View style={[styles.rectangle, styles.rectangle1]} />
          <View style={[styles.rectangle, styles.rectangle2]} />
          <View style={[styles.rectangle, styles.rectangle3]} />
          <View style={[styles.rectangle, styles.rectangle4]} />
          <View style={[styles.rectangle, styles.rectangle5]} />
        </View>
        <Image
          source={require('@skateback/assets/images/skateboarder.png')}
          style={styles.image}
        />
      </View>

      <View style={styles.thirdContainer}>
        <Text style={styles.description}>
          Easily <Text style={styles.boldText}>control</Text> your skateboard, 
          <Text style={styles.boldText}> track</Text> performance, and use the 
          <Text style={styles.boldText}> 'return to me'</Text> feature for quick retrieval.
        </Text>

        <TouchableOpacity onPress={handlePairSkateboard}>
          <ImageBackground
            source={require('@skateback/assets/images/button-color.png')} 
            style={styles.button}
            resizeMode="cover" 
            imageStyle={styles.buttonImage}
          >
            <Text style={styles.buttonText}>Pair Skateboard</Text>
          </ImageBackground>
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
  firstContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'flex-start',
    paddingLeft: 50,
    paddingTop: 25,
    paddingBottom: 10
  },
  secondContainer: {
    height: 468,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  rectangleContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    width: '100%',
    paddingHorizontal: 53, 
  },
  rectangle: {
    width: 60, 
    height: 500, 
  },
  rectangle1: {
    backgroundColor: '#8ECAE6',
  },
  rectangle2: {
    backgroundColor: '#219EBC',
  },
  rectangle3: {
    backgroundColor: '#023047',
  },
  rectangle4: {
    backgroundColor: '#FFB703',
  },
  rectangle5: {
    backgroundColor: '#FB8500',
  },
  title: {
    fontSize: 38, 
    fontWeight: 'bold',
    color: '#023047',
  },
  subtitle: {
    fontSize: 18,
    color: '#023047',
    marginBottom: 10,
  },
  image: {
    width: 382,     
    height: 436,      
    position: 'absolute', 
    left: 90,       
    top: 56,         
    zIndex: 1,      
  },
  thirdContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 12,
  },
  description: {
    paddingHorizontal: 48,
    textAlign: 'center',
    marginBottom: 40,
    fontSize: 12,
    color: '#818590'
  },
  boldText: {
    fontWeight: 'bold',
    color: '#818590', 
  },
  button: {
    height: 57,
    width: 319,
    justifyContent: 'center', 
    alignItems: 'center',
    borderRadius: 20, 
    overflow: 'hidden',
  },
  buttonImage: {
    borderRadius: 20, 
  },
  buttonText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold', 
  },
});
