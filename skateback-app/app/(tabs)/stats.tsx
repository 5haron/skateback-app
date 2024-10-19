import React, { useState } from 'react';
import { View, Text, StyleSheet, Image } from 'react-native';

export default function StatsScreen() {
  const [milesTraveled, setMilesTraveled] = useState(5); 

  const co2PerMile = 0.404; 
  const co2Saved = (milesTraveled * co2PerMile).toFixed(2);

  return (
    <View style={styles.container}>
      <View style={styles.headerContainer}>
        <Text style={styles.title}>Skateboard{'\n'}Stats</Text>
        <View style={styles.roundedBox}>
          <Image
            source={require('@skateback/assets/icons/skateboard.png')}
            style={styles.roundedIcon}
          />
        </View>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statBox}>
          <Text style={styles.statDescription}>Top Speed</Text>
          <Text style={styles.statValue}>11</Text>
          <Text style={styles.statLabel}>miles</Text>
        </View>

        <View style={styles.statBox}>
          <Text style={styles.statDescription}>Traveled</Text>
          <Text style={styles.statValue}>{milesTraveled}</Text>
          <Text style={styles.statLabel}>miles</Text>
        </View>
      </View>

      <View style={styles.statBoxCarbon}>
        <View style={styles.co2Container}>
          <Image
            source={require('@skateback/assets/icons/leaf.png')}
            style={styles.icon}
          />
          <Text style={styles.carbonValue}>{co2Saved} kg</Text>
          <Text style={styles.statDescription}>CO<Text style={styles.subscript}>2</Text> {'\n'}saved
          </Text>
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
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 30,
    paddingHorizontal: 10,
  },
  statBox: {
    flex: 1,
    backgroundColor: '#E7F2F8',
    borderRadius: 20,
    padding: 24,
    marginHorizontal: 10,
    alignItems: 'center',
  },
  statDescription: {
    fontSize: 18,
    color: '#229EBC',
    fontWeight: 'bold',
    justifyContent: 'center',
    textAlign: 'center',
    lineHeight: 16,
    paddingVertical: 4,
    marginBottom: -10
  },
  statValue: {
    fontSize: 90,
    fontWeight: 'bold',
    color: '#023047',
  },
  carbonValue: {
    fontSize: 55,
    fontWeight: 'bold',
    color: '#023047',
  },
  statLabel: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#023047',
    marginTop: -14,
    textAlign: 'center'
  },
  icon: {
    width: 60,
    height: 60,
  },
  statBoxCarbon: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E7F2F8',
    borderRadius: 20,
    padding: 20, 
    marginTop: 20,
    width: 325,
    alignSelf: 'center', 
    justifyContent: 'center',
  },
  co2Container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    width: '100%',
  },
  subscript: {
    fontSize: 12,
    lineHeight: 12,
    fontWeight: 'bold',
  },
});
