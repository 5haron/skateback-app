import serial
from . import world
from ublox_gps import UbloxGps

SERIAL_GPS = '/dev/gps'
BAUD_RATE = 115200
READS = 5

def average_coordinates(readings):
    """Calculate the average of a list of (lat, lon) tuples."""
    avg_lat = sum(r[0] for r in readings) / len(readings)
    avg_lon = sum(r[1] for r in readings) / len(readings)
    return (avg_lat, avg_lon)

def get_location():
    try:
        port = serial.Serial(SERIAL_GPS, baudrate=BAUD_RATE, timeout=5)
    except serial.SerialException as e:
        print(f"Error opening serial port {SERIAL_GPS}: {e}")
        exit(1)
    gps = UbloxGps(port)

    try:
        print("Listening for UBX Messages")
        readings = []

        while len(readings) < READS:
            try:
                geo = gps.geo_coords()
                
                if geo is not None:
                    lat, lon = geo.lat, geo.lon
                    if lat != 0 and lon != 0:  # Ensure non-zero coordinates
                        readings.append((lat, lon))
                        print(f"Reading {len(readings)}: Latitude = {lat}, Longitude = {lon}")
                    else:
                        print("Skipped empty reading.")
                else:
                    print("No GPS data received.")
            except (ValueError, IOError) as err:
                print("Error in Position Reading:", err)
        
        avg_coords = average_coordinates(readings)
        print(f"\nAverage Coordinates: Latitude = {avg_coords[0]:.6f}, Longitude = {avg_coords[1]:.6f}")
        utm_avg_coords = world.World.gps_to_world(avg_coords[0], avg_coords[1])
        print(f"\nAverage UTM Coordinates: Latitude = {utm_avg_coords[0]:.6f}, Longitude = {utm_avg_coords[1]:.6f}")

        return utm_avg_coords

    except KeyboardInterrupt:
        print("Exiting.")
    finally:
        port.close()

def get_heading():
    try:
        port = serial.Serial(SERIAL_GPS, baudrate=BAUD_RATE, timeout=5)
    except serial.SerialException as e:
        print(f"Error opening serial port {SERIAL_GPS}: {e}")
        exit(1)
    gps = UbloxGps(port)

    try:
        print("Listening for UBX Messages")
        readings = []

        while len(readings) < READS:
            try:
                veh = gps.veh_attitude()
                
                if veh is not None:
                    heading = veh.heading
                    if heading != 0.0:  # Ensure non-zero coordinates
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

        return avg_reading

    except KeyboardInterrupt:
        print("Exiting.")
    finally:
        port.close()

if __name__ == '__main__':
    get_location()
