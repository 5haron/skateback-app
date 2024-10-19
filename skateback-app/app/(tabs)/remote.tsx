import React, { useState } from 'react';
import { View, Text, Image, StyleSheet, TouchableOpacity, Switch } from 'react-native';
import { useLocalSearchParams } from 'expo-router';

export default function RemoteControlScreen() {
  const [isReverse, setIsReverse] = useState(false); 
  const [batteryPercentage, setBatteryPercentage] = useState(100); 
  const { skateboardName } = useLocalSearchParams(); 

  const renderBatteryRectangles = () => {
    const numberOfRectangles = Math.floor(batteryPercentage / 20);
    let rectangles = [];
    for (let i = 0; i < numberOfRectangles; i++) {
      rectangles.push(
        <View key={i} style={styles.batteryRectangle} />
      );
    }
    return rectangles;
  };

  return (
    <View style={styles.container}>
      <View style={styles.headerContainer}>
      <Text style={styles.title}>
        {skateboardName 
          ? (Array.isArray(skateboardName) 
              ? skateboardName.join(' ').replace(/skateboard/i, '').trim() 
              : skateboardName.replace(/skateboard/i, '').trim()) 
          : "Unknown's"}{'\n'}
        <Text>Skateboard</Text>
      </Text>
        <View style={styles.roundedBox}>
          <Image
            source={require('@skateback/assets/icons/skateboard.png')}
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
            source={require('@skateback/assets/icons/skate-battery.png')}
            style={styles.skateBatteryImage} 
            resizeMode="contain"
          />
          <Image
            source={require('@skateback/assets/icons/battery.png')}
            style={styles.batteryImage}
            resizeMode="contain"
          />
          <Text style={styles.batteryLabel}>{batteryPercentage}%</Text>

          <View style={styles.batteryRectangleContainer}>
            {renderBatteryRectangles()}
          </View>
        </View>
        
        <View style={styles.rightContainer}>
          <View style={styles.buttonContainer}>
            <Text style={styles.controlLabel}>Accelerate</Text>
            <TouchableOpacity style={styles.button}>
              <Text style={styles.buttonText}>+</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.buttonContainer}>
            <Text style={styles.controlLabel}>Decelerate</Text>
            <TouchableOpacity style={styles.button}>
              <Text style={styles.buttonText}>–</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.reverseContainer}>
            <Text style={styles.reverseText}>Reverse</Text>
            <Switch
              value={isReverse}
              onValueChange={(value) => setIsReverse(value)}
              trackColor={{ false: '#ccc', true: '#8ECAE6' }} 
              thumbColor={isReverse ? '#023047' : '#f4f3f4'} 
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
  },
  roundedBox: {
    backgroundColor: '#8ECAE6',
    borderRadius: 20,
    padding: 14,
    alignItems: 'center',
    justifyContent: 'center',
    width: 65,
  },
  roundedIcon: {
    width: 35,
    height: 35,
  },
  statBox: {
    alignItems: 'center',
    backgroundColor: '#E7F2F8',
    borderRadius: 20,
    padding: 40,
    marginTop: 20,
    width: 358,
    paddingHorizontal: 10,
    marginLeft: 20,
  },
  statLabel: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#023047',
    marginTop: -14,
    textAlign: 'center',
  },
  statValue: {
    fontSize: 90,
    fontWeight: 'bold',
    color: '#023047',
  },
  splitContainer: {
    flexDirection: 'row',
    marginTop: 20,
    paddingHorizontal: 20,
  },
  leftBox: {
    flex: 1,
    marginRight: 10,
    borderRadius: 20,
    position: 'relative', 
  },
  skateBatteryImage: {
    width: 410,
    height: 410,
    alignSelf: 'center', 
    marginTop: 5,
    marginLeft: -5
  },  
  batteryImage: {
    position: 'absolute',     
    top: 105,                 
    left: 9,               
    width: 160,            
    height: 160,
  },
  batteryLabel: {
    position: 'absolute',
    top: 275, 
    width: 185,
    textAlign: 'center',  
    fontSize: 28,
    color: 'white',
    fontWeight: 'bold',
  },
  batteryRectangleContainer: {
    position: 'absolute',
    top: 154,
    left: 61,
    width: 56,
    height: 100, 
    flexDirection: 'column',
    justifyContent: 'flex-end',
  },
  batteryRectangle: {
    width: '100%',
    height: 21,
    backgroundColor: 'white',
    marginBottom: 4, 
  },
  rightContainer: {
    flex: 1,
    justifyContent: 'space-between',
  },
  controlLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#023047',
    textAlign: 'center',
  },
  buttonContainer: {
    alignItems: 'center', 
    justifyContent: 'flex-start',
    marginBottom: 10,
  },
  button: {
    backgroundColor: '#E7F2F8',
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    paddingBottom: 10,
    marginVertical: 5,
    width: '100%', 
  },
  buttonText: {
    fontSize: 120,
    fontWeight: 'bold',
    color: '#023047',
  },
  reverseContainer: {
    flexDirection: 'row',
    justifyContent: 'flex-start', 
    alignItems: 'center',
  },
  reverseText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#023047',
    marginRight: 10,
    marginLeft: 25
  },
  switchWrapper: {
    flexDirection: 'row', 
    alignItems: 'center',
  },
  switch: {
    width: 60, 
  },
});
