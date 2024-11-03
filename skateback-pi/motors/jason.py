# server.py

import socket
import threading
import pyvesc
from pyvesc.VESC.messages import SetDutyCycle
import serial
import time

# Initialize duty cycles and acceleration steps
left_duty_cycle = 0.0
right_duty_cycle = 0.0
acceleration_step = 0.01  # Step for acceleration
normal_deceleration_step = 0.02  # Step for smooth deceleration
braking_deceleration_step = 0.04  # Larger step for faster deceleration (braking)

# Define the serial ports for the left and right motors
left_serial_port = '/dev/ttyACM0'   # Adjust as necessary
right_serial_port = '/dev/ttyACM1'  # Adjust as necessary

# Key state dictionary
key_states = {
    'w': False,         # Left motor accelerate
    's': False,         # Left motor brake
    'up': False,        # Right motor accelerate
    'down': False       # Right motor brake
}

# Lock for thread-safe operations
key_lock = threading.Lock()

def set_motor_duty_cycle(serial_port, duty_cycle):
    """Set the motor to the given duty cycle."""
    try:
        with serial.Serial(serial_port, baudrate=115200, timeout=0.05) as ser:
            ser.write(pyvesc.encode(SetDutyCycle(duty_cycle)))
    except serial.SerialException as e:
        print(f"Error setting motor duty cycle on {serial_port}: {e}")

def receive_key_states():
    """Thread function to receive key states from the client."""
    global key_states
    # Set up UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 5005))  # Listen on all interfaces on port 5005
    print("Server listening on port 5005...")

    while True:
        data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
        message = data.decode('utf-8')
        with key_lock:
            if message == 'w_down':
                key_states['w'] = True
            elif message == 'w_up':
                key_states['w'] = False
            elif message == 's_down':
                key_states['s'] = True
            elif message == 's_up':
                key_states['s'] = False
            elif message == 'up_down':
                key_states['up'] = True
            elif message == 'up_up':
                key_states['up'] = False
            elif message == 'down_down':
                key_states['down'] = True
            elif message == 'down_up':
                key_states['down'] = False
            elif message == 'exit':
                print("Exiting...")
                # Stop motors before exiting
                set_motor_duty_cycle(left_serial_port, 0)
                set_motor_duty_cycle(right_serial_port, 0)
                sock.close()
                exit(0)
            else:
                # Handle unknown messages
                print(f"Unknown message received: {message}")

def control_motors():
    """Main function to control the motors based on key_states."""
    global left_duty_cycle, right_duty_cycle
    left_braking = False
    right_braking = False

    try:
        while True:
            with key_lock:
                keys = key_states.copy()

            # Control Left Motor
            if keys['w']:  # Accelerate left motor
                left_duty_cycle += acceleration_step
                if left_duty_cycle > 1:
                    left_duty_cycle = 1
                left_motor_active = True
                left_braking = False
                print(f"Left motor accelerating: {left_duty_cycle:.2f}", end='\r')

            elif keys['s']:  # Decelerate left motor faster (braking)
                left_braking = True
                left_motor_active = False
                print(f"Left motor braking: {left_duty_cycle:.2f}    ", end='\r')

            else:
                left_motor_active = False

            # Control Right Motor
            if keys['up']:  # Accelerate right motor
                right_duty_cycle += acceleration_step
                if right_duty_cycle > 1:
                    right_duty_cycle = 1
                right_motor_active = True
                right_braking = False
                print(f"Right motor accelerating: {right_duty_cycle:.2f}", end='\r')

            elif keys['down']:  # Decelerate right motor faster (braking)
                right_braking = True
                right_motor_active = False
                print(f"Right motor braking: {right_duty_cycle:.2f}     ", end='\r')

            else:
                right_motor_active = False

            # Deceleration for Left Motor
            if not left_motor_active:
                if left_braking:
                    # Apply faster deceleration for braking
                    if left_duty_cycle > 0:
                        left_duty_cycle -= braking_deceleration_step
                        if left_duty_cycle < 0:
                            left_duty_cycle = 0
                else:
                    # Apply normal smooth deceleration
                    if left_duty_cycle > 0:
                        left_duty_cycle -= normal_deceleration_step
                        if left_duty_cycle < 0:
                            left_duty_cycle = 0

            # Deceleration for Right Motor
            if not right_motor_active:
                if right_braking:
                    # Apply faster deceleration for braking
                    if right_duty_cycle > 0:
                        right_duty_cycle -= braking_deceleration_step
                        if right_duty_cycle < 0:
                            right_duty_cycle = 0
                else:
                    # Apply normal smooth deceleration
                    if right_duty_cycle > 0:
                        right_duty_cycle -= normal_deceleration_step
                        if right_duty_cycle < 0:
                            right_duty_cycle = 0

            # Reset braking flags if duty cycle reaches zero
            if left_duty_cycle == 0:
                left_braking = False
            if right_duty_cycle == 0:
                right_braking = False

            # Continuously send the current duty cycle for both motors
            set_motor_duty_cycle(left_serial_port, left_duty_cycle)
            set_motor_duty_cycle(right_serial_port, right_duty_cycle)

            time.sleep(0.1)

    except KeyboardInterrupt:
        # Stop motors if the script is interrupted
        set_motor_duty_cycle(left_serial_port, 0)
        set_motor_duty_cycle(right_serial_port, 0)
        print("\nMotors stopped.")
        time.sleep(1)

if __name__ == "__main__":
    # Start the key receiving thread
    key_thread = threading.Thread(target=receive_key_states)
    key_thread.daemon = True
    key_thread.start()

    # Start the motor control loop
    control_motors()
