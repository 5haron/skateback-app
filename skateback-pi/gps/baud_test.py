import serial

# Try different baud rates
baud_rates = [9600, 19200, 38400, 57600, 115200]

for baud in baud_rates:
    try:
        with serial.Serial('/dev/ttyACM0', baudrate=baud, timeout=2) as ser:
            # Send UBX-CFG-PRT command to query port configuration
            ser.write(b'\xB5\x62\x06\x00\x00\x00\x06\x18')
            response = ser.read(30)  # Adjust length based on expected response
            if response:
                print(f"Received response at baud rate {baud}: {response.hex()}")
            else:
                print(f"No response at baud rate {baud}")
    except serial.SerialException as e:
        print(f"Failed at baud {baud}: {e}")
