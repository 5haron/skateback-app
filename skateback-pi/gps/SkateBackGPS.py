import serial
import world
from ublox_gps import UbloxGps
import asyncio
import websockets
import json
import threading
import time

SERIAL_GPS = '/dev/gps'
BAUD_RATE = 115200
READS = 5
WS_HOST = 'localhost'
WS_PORT = 8765

class GPSServer:
   def __init__(self):
       self.location = None
       self.heading = None
       self.running = True
       
   def average_coordinates(self, readings):
       """Calculate the average of a list of (lat, lon) tuples."""
       avg_lat = sum(r[0] for r in readings) / len(readings)
       avg_lon = sum(r[1] for r in readings) / len(readings)
       return (avg_lat, avg_lon)

   def get_location(self):
       try:
           port = serial.Serial(SERIAL_GPS, baudrate=BAUD_RATE, timeout=5)
           gps = UbloxGps(port)
           
           print("Listening for UBX Messages")
           readings = []
           while len(readings) < READS:
               try:
                   geo = gps.geo_coords()
                   if geo is not None:
                       lat, lon = geo.lat, geo.lon
                       if lat != 0 and lon != 0:
                           readings.append((lat, lon))
                           print(f"Reading {len(readings)}: Latitude = {lat}, Longitude = {lon}")
                       else:
                           print("Skipped empty reading.")
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
       except serial.SerialException as e:
           print(f"Error opening serial port {SERIAL_GPS}: {e}")
           exit(1)
       finally:
           port.close()

   def get_heading(self):
       try:
           port = serial.Serial(SERIAL_GPS, baudrate=BAUD_RATE, timeout=5)
           gps = UbloxGps(port)
           
           print("Listening for UBX Messages")
           readings = []
           while len(readings) < READS:
               try:
                   veh = gps.veh_attitude()
                   if veh is not None:
                       heading = veh.heading
                       if heading != 0.0:
                           readings.append(heading)
                           print(f"Reading {len(readings)}: Heading of Motion = {heading}")
                       else:
                           print("Skipped empty reading.")
                   else:
                       print("No GPS data received.")
               except (ValueError, IOError) as err:
                   print("Error in Heading of Motion Reading:", err)
           
           avg_reading = sum(readings)/len(readings)
           print(f"\nAverage Reading: Heading of Motion = {avg_reading:.6f}")
           self.heading = avg_reading
           return self.heading
       except serial.SerialException as e:
           print(f"Error opening serial port {SERIAL_GPS}: {e}")
           exit(1)
       finally:
           port.close()

   async def gps_update_loop(self):
       """Continuously update GPS data"""
       while self.running:
           try:
               self.get_location()
               self.get_heading()
               await asyncio.sleep(1)  # Update every second
           except Exception as e:
               print(f"Error in GPS update loop: {e}")
               await asyncio.sleep(1)

   async def handle_client(self, websocket):
       """Handle individual client connections"""
       try:
           while self.running:
               if self.location and self.heading is not None:
                   data = {
                       "location": self.location,
                       "heading": self.heading,
                       "timestamp": time.time()
                   }
                   await websocket.send(json.dumps(data))
               await asyncio.sleep(1)
       except websockets.exceptions.ConnectionClosed:
           print("Client disconnected")
       except Exception as e:
           print(f"Error handling client: {e}")

   async def start_server(self):
       """Start the WebSocket server"""
       async with websockets.serve(self.handle_client, WS_HOST, WS_PORT):
           print(f"GPS WebSocket server running on ws://{WS_HOST}:{WS_PORT}")
           # Start GPS update loop
           update_task = asyncio.create_task(self.gps_update_loop())
           # Keep the server running
           await asyncio.Future()  # run forever

def start_gps_server():
   """Function to start the GPS server"""
   server = GPSServer()
   asyncio.run(server.start_server())

if __name__ == '__main__':
   start_gps_server()