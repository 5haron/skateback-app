import serial
import world
from ublox_gps import UbloxGps
import threading
import time

SERIAL_GPS = '/dev/gps'
BAUD_RATE = 115200
READS = 5

class SkateBackGPS:
    def __init__(self):
        self.location = None    # Last location obtained from calling self.get_location()
        self.heading = None     # Last heading obtained from calling self.get_heading()

        try:
            self.port = serial.Serial(SERIAL_GPS, baudrate=BAUD_RATE, timeout=5)
            self.gps = UbloxGps(self.port)
        except serial.SerialException as e:
           print(f"Error opening serial port {SERIAL_GPS}: {e}")
           exit(1)

    def __enter__(self):
        """
        Enable use of the 'with' statement for resource management.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Ensure serial connections are closed when exiting the 'with' block.
        """
        self.close() 

    def close(self):
        """
        Properly shut down the controller.
        """
        try:            
            # Close serial connections
            if self.port.is_open:
                self.port.close()
        except Exception as e:
            print(f"An error occurred while closing: {e}")
     
    def average_coordinates(self, readings):
        """Calculate the average of a list of (lat, lon) tuples."""
        avg_lat = sum(r[0] for r in readings) / len(readings)
        avg_lon = sum(r[1] for r in readings) / len(readings)
        return (avg_lat, avg_lon)

    def get_location(self):           
        print("Listening for UBX Messages")
        readings = []
        while len(readings) < READS:
            try:
                geo = self.gps.geo_coords()
                if geo is not None:
                    lat, lon = geo.lat, geo.lon
                    if lat != 0 and lon != 0:
                        readings.append((lat, lon))
                        print(f"Reading {len(readings)}: Latitude = {lat}, Longitude = {lon}")
                    else:
                        print("Skipped empty reading. Waiting for position lock...")
                else:
                    print("No GPS data received.")
            except (ValueError, IOError) as err:
                print("Error in Position Reading:", err)
        
        avg_coords = self.average_coordinates(readings)
        print(f"\nAverage Coordinates: Latitude = {avg_coords[0]:.6f}, Longitude = {avg_coords[1]:.6f}")
        utm_avg_coords = world.World.gps_to_world(avg_coords[0], avg_coords[1])
        print(f"\nAverage UTM Coordinates: Latitude = {utm_avg_coords[0]:.6f}, Longitude = {utm_avg_coords[1]:.6f}")
        
        self.location = {
            "latitude": utm_avg_coords[0],
            "longitude": utm_avg_coords[1]
        }
        return self.location

    def get_heading(self):            
        print("Listening for UBX Messages")
        readings = []
        while len(readings) < READS:
            try:
                veh = self.gps.veh_attitude()
                if veh is not None:
                    heading = veh.heading
                    if heading != 0.0:
                        readings.append(heading)
                        print(f"Reading {len(readings)}: Heading of Motion = {heading}")
                    else:
                        print("Skipped empty reading. Waiting for heading information...")
                else:
                    print("No GPS data received.")
            except (ValueError, IOError) as err:
                print("Error in Heading of Motion Reading:", err)
        
        avg_reading = sum(readings)/len(readings)
        print(f"\nAverage Reading: Heading of Motion = {avg_reading:.6f}")
        self.heading = avg_reading
        return self.heading

if __name__ == '__main__':
   sk_gps = SkateBackGPS()
   sk_gps.get_heading()
   sk_gps.get_location()