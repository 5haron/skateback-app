import pyvesc
from pyvesc.VESC.messages import SetDutyCycle
import serial
import time
import curses
import threading

# Initialize duty cycles and acceleration steps
left_duty_cycle = 0.0
right_duty_cycle = 0.0
acceleration_step = 0.01  # Step for acceleration
normal_deceleration_step = 0.02  # Step for smooth deceleration
braking_deceleration_step = 0.04  # Larger step for faster deceleration (braking)

# Define the serial ports for the left and right motors
left_serial_port = '/dev/ttyACM0'
right_serial_port = '/dev/ttyACM1'

# Global flags for braking states
left_braking = False
right_braking = False

def set_motor_duty_cycle(serial_port, duty_cycle):
    """Set the motor to the given duty cycle."""
    with serial.Serial(serial_port, baudrate=115200, timeout=0.05) as ser:
        ser.write(pyvesc.encode(SetDutyCycle(duty_cycle)))

def control_left_motor(stdscr):
    global left_duty_cycle, left_braking
    while True:
        if left_braking:
            if left_duty_cycle > 0:
                left_duty_cycle -= braking_deceleration_step
                if left_duty_cycle < 0:
                    left_duty_cycle = 0
            else:
                left_braking = False
        else:
            if left_duty_cycle > 0:
                left_duty_cycle -= normal_deceleration_step
                if left_duty_cycle < 0:
                    left_duty_cycle = 0
        set_motor_duty_cycle(left_serial_port, left_duty_cycle)
        stdscr.addstr(0, 0, f"Left motor duty cycle: {left_duty_cycle}")
        stdscr.refresh()
        time.sleep(0.1)

def control_right_motor(stdscr):
    global right_duty_cycle, right_braking
    while True:
        if right_braking:
            if right_duty_cycle > 0:
                right_duty_cycle -= braking_deceleration_step
                if right_duty_cycle < 0:
                    right_duty_cycle = 0
            else:
                right_braking = False
        else:
            if right_duty_cycle > 0:
                right_duty_cycle -= normal_deceleration_step
                if right_duty_cycle < 0:
                    right_duty_cycle = 0
        set_motor_duty_cycle(right_serial_port, right_duty_cycle)
        stdscr.addstr(2, 0, f"Right motor duty cycle: {right_duty_cycle}")
        stdscr.refresh()
        time.sleep(0.1)

def handle_input(stdscr):
    global left_duty_cycle, right_duty_cycle, left_braking, right_braking
    stdscr.nodelay(True)  # Non-blocking key input

    while True:
        key = stdscr.getch()

        # Control Left Motor
        if key == ord('w'):  # Accelerate left motor
            left_duty_cycle += acceleration_step
            if left_duty_cycle > 1:
                left_duty_cycle = 1
            left_braking = False
            stdscr.addstr(1, 0, f"Left motor accelerating: {left_duty_cycle}")

        elif key == ord('s'):  # Decelerate left motor faster (braking)
            left_braking = True
            stdscr.addstr(1, 0, f"Left motor braking: {left_duty_cycle}")

        # Control Right Motor
        if key == curses.KEY_UP:  # Accelerate right motor
            right_duty_cycle += acceleration_step
            if right_duty_cycle > 1:
                right_duty_cycle = 1
            right_braking = False
            stdscr.addstr(3, 0, f"Right motor accelerating: {right_duty_cycle}")

        elif key == curses.KEY_DOWN:  # Decelerate right motor faster (braking)
            right_braking = True
            stdscr.addstr(3, 0, f"Right motor braking: {right_duty_cycle}")

        stdscr.refresh()
        time.sleep(0.05)

def control_motors(stdscr):
    # Start threads for each motor control
    left_thread = threading.Thread(target=control_left_motor, args=(stdscr,))
    right_thread = threading.Thread(target=control_right_motor, args=(stdscr,))
    input_thread = threading.Thread(target=handle_input, args=(stdscr,))

    # Start all threads
    left_thread.start()
    right_thread.start()
    input_thread.start()

    # Wait for threads to complete
    left_thread.join()
    right_thread.join()
    input_thread.join()

if __name__ == "__main__":
    curses.wrapper(control_motors)
