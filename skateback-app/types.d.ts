// types.d.ts
import { Device, Characteristic } from "react-native-ble-plx";

declare module "react-native-ble-plx" {
  interface Device {
    monitorCharacteristicForService(
      serviceUUID: string,
      characteristicUUID: string,
      listener: (
        error: Error | null,
        characteristic: Characteristic | null
      ) => void
    ): { remove: () => void };
  }
}
