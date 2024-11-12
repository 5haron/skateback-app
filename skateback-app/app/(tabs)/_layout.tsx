import { Tabs } from "expo-router";
import React from "react";
import { Image } from "react-native";

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarShowLabel: false,
        tabBarStyle: {
          backgroundColor: "#fff",
          borderTopLeftRadius: 30,
          borderTopRightRadius: 30,
          height: 70,
          position: "absolute",
          bottom: -10,
          left: 0,
          right: 0,
          paddingBottom: 10,
          elevation: 0,
          shadowColor: "transparent",
        },
        tabBarIcon: ({ color }) => {
          let iconName;

          switch (route.name) {
            case "remote":
              iconName = require("@skateback/assets/icons/remote.png");
              break;
            case "return":
              iconName = require("@skateback/assets/icons/locations.png");
              break;
            case "stats":
              iconName = require("@skateback/assets/icons/graph.png");
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
        tabBarActiveTintColor: "#023047",
        tabBarInactiveTintColor: "#8ECAE6",
      })}
    >
      <Tabs.Screen
        name="remote"
        options={{
          tabBarIcon: ({ color }) => (
            <Image
              source={require("@skateback/assets/icons/remote.png")}
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
              source={require("@skateback/assets/icons/locations.png")}
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
              source={require("@skateback/assets/icons/graph.png")}
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
