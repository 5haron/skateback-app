import { Tabs } from 'expo-router';
import React from 'react';
import { Image } from 'react-native';

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarShowLabel: false,
        tabBarStyle: {
          backgroundColor: '#8ECAE6',  
          borderTopLeftRadius: 20,     
          borderTopRightRadius: 20,    
          height: 70,                   
          position: 'absolute',        
          bottom: 0,                    
          left: 0,
          right: 0,
          paddingBottom: 0,           
          paddingTop: 0,                
          elevation: 0,                
        },
      }}
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
