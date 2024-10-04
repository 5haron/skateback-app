import React from "react";
import { Text, View } from "react-native";
import { appStyles } from "@skateback/styles/global";

export default function Index() {
  return (
    <View className="flex-1 justify-center items-center">
      {/* Using Tailwind for layout and custom styles for font */}
      <Text className="text-lg text-gray-800" style={appStyles.defaultText}>
        Edit app/index.tsx to edit this screen.
      </Text>
    </View>
  );
}
