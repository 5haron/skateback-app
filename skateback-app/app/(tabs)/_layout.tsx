import { Tabs } from 'expo-router';
import React from 'react';
import { Image } from 'react-native';

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarShowLabel: false,
        tabBarStyle: {
          backgroundColor: '#fff',  
          borderTopLeftRadius: 30,
          borderTopRightRadius: 30,
          height: 80,
          paddingBottom: 10,
          elevation: 10,
          shadowColor: '#000',
          shadowOffset: { width: 0, height: 6 },
          shadowOpacity: 0.1,
          shadowRadius: 8,
        },
        tabBarIcon: ({ color }) => {
          let iconName;

          switch (route.name) {
            case 'remote':
              iconName = require('@skateback/assets/icons/remote.png');
              break;
            case 'return':
              iconName = require('@skateback/assets/icons/locations.png');
              break;
            case 'stats':
              iconName = require('@skateback/assets/icons/graph.png');
              break;
          }

          return (
            <Image
              source={iconName}
              style={{
                width: 35,
                height: 35,
                tintColor: color,  
              }}
            />
          );
        },
        tabBarActiveTintColor: '#023047', 
        tabBarInactiveTintColor: '#8ECAE6', 
      })}
    >
      <Tabs.Screen
        name="remote"
        options={{
          tabBarIcon: ({ color }) => (
            <Image
              source={require('@skateback/assets/icons/remote.png')}
              style={{
                width: 35,
                height: 35,
                tintColor: color,
              }}
            />
          ),
        }}
      />
      <Tabs.Screen
        name="return"
        options={{
          tabBarIcon: ({ color }) => (
            <Image
              source={require('@skateback/assets/icons/locations.png')}
              style={{
                width: 35,
                height: 35,
                tintColor: color,
              }}
            />
          ),
        }}
      />
      <Tabs.Screen
        name="stats"
        options={{
          tabBarIcon: ({ color }) => (
            <Image
              source={require('@skateback/assets/icons/graph.png')}
              style={{
                width: 35,
                height: 35,
                tintColor: color,
              }}
            />
          ),
        }}
      />
    </Tabs>
  );
}

