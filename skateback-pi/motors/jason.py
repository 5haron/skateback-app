import pyvesc
from pyvesc.VESC.messages import SetDutyCycle
import serial
import time
import threading
import pygame

# Initialize duty cycles and acceleration steps
left_duty_cycle = 0.0
right_duty_cycle = 0.0
acceleration_step = 0.01  # Step for acceleration
normal_deceleration_step = 0.02  # Step for smooth deceleration
braking_deceleration_step = 0.04  # Larger step for faster deceleration (braking)

# Define the serial ports for the left and right motors
left_serial_port = '/dev/ttyACM0'
right_serial_port = '/dev/ttyACM1'

# Key state dictionary
key_states = {
    'w': False,         # Left motor accelerate
    's': False,         # Left motor brake
    'up': False,        # Right motor accelerate
    'down': False       # Right motor brake
}

# Locks for thread-safe operations
key_lock = threading.Lock()

def set_motor_duty_cycle(serial_port, duty_cycle):
    """Set the motor to the given duty cycle."""
    with serial.Serial(serial_port, baudrate=115200, timeout=0.05) as ser:
        ser.write(pyvesc.encode(SetDutyCycle(duty_cycle)))

def read_keys():
    """Thread function to read keys and update key_states."""
    global key_states
    pygame.init()
    screen = pygame.display.set_mode((100, 100))  # Small window to capture events
    pygame.display.set_caption('Motor Control')

    running = True
    while running:
        for event in pygame.event.get():
            with key_lock:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        key_states['w'] = True
                    elif event.key == pygame.K_s:
                        key_states['s'] = True
                    elif event.key == pygame.K_UP:
                        key_states['up'] = True
                    elif event.key == pygame.K_DOWN:
                        key_states['down'] = True
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        key_states['w'] = False
                    elif event.key == pygame.K_s:
                        key_states['s'] = False
                    elif event.key == pygame.K_UP:
                        key_states['up'] = False
                    elif event.key == pygame.K_DOWN:
                        key_states['down'] = False
                elif event.type == pygame.QUIT:
                    running = False
        time.sleep(0.01)

    pygame.quit()

def control_motors():
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
                print(f"Left motor accelerating: {left_duty_cycle:.2f}   ")

            elif keys['s']:  # Decelerate left motor faster (braking)
                left_braking = True
                left_motor_active = False
                print(f"Left motor braking: {left_duty_cycle:.2f}        ")

            else:
                left_motor_active = False

            # Control Right Motor
            if keys['up']:  # Accelerate right motor
                right_duty_cycle += acceleration_step
                if right_duty_cycle > 1:
                    right_duty_cycle = 1
                right_motor_active = True
                right_braking = False
                print(f"Right motor accelerating: {right_duty_cycle:.2f}  ")

            elif keys['down']:  # Decelerate right motor faster (braking)
                right_braking = True
                right_motor_active = False
                print(f"Right motor braking: {right_duty_cycle:.2f}       ")

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
                    elif left_duty_cycle < 0:
                        left_duty_cycle += braking_deceleration_step
                        if left_duty_cycle > 0:
                            left_duty_cycle = 0
                else:
                    # Apply normal smooth deceleration
                    if left_duty_cycle > 0:
                        left_duty_cycle -= normal_deceleration_step
                        if left_duty_cycle < 0:
                            left_duty_cycle = 0
                    elif left_duty_cycle < 0:
                        left_duty_cycle += normal_deceleration_step
                        if left_duty_cycle > 0:
                            left_duty_cycle = 0

            # Deceleration for Right Motor
            if not right_motor_active:
                if right_braking:
                    # Apply faster deceleration for braking
                    if right_duty_cycle > 0:
                        right_duty_cycle -= braking_deceleration_step
                        if right_duty_cycle < 0:
                            right_duty_cycle = 0
                    elif right_duty_cycle < 0:
                        right_duty_cycle += braking_deceleration_step
                        if right_duty_cycle > 0:
                            right_duty_cycle = 0
                else:
                    # Apply normal smooth deceleration
                    if right_duty_cycle > 0:
                        right_duty_cycle -= normal_deceleration_step
                        if right_duty_cycle < 0:
                            right_duty_cycle = 0
                    elif right_duty_cycle < 0:
                        right_duty_cycle += normal_deceleration_step
                        if right_duty_cycle > 0:
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
        print("Motors stopped")
        time.sleep(1)

if __name__ == "__main__":
    # Start the key reading thread
    key_thread = threading.Thread(target=read_keys)
    key_thread.daemon = True
    key_thread.start()

    control_motors()
