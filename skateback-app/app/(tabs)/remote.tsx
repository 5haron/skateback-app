import React, { useState } from 'react';
import { View, Text, Image, StyleSheet, TouchableOpacity, Switch } from 'react-native';

export default function RemoteControlScreen() {
  const [isReverse, setIsReverse] = useState(false); 

  return (
    <View style={styles.container}>
      <View style={styles.headerContainer}>
        <Text style={styles.title}>
          Sharon's{'\n'}
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
        <View style={styles.leftBox} />
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
    backgroundColor: '#E7F2F8',
    marginRight: 10,
    borderRadius: 20,
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
    alignItems: 'center', // Center the label and button
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
  },
  switchWrapper: {
    flexDirection: 'row', 
    alignItems: 'center',
  },
  switch: {
    width: 60, 
  },
});
