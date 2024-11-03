import pyvesc
from pyvesc.VESC.messages import SetDutyCycle
import serial
import time
import curses

# Initialize duty cycles and acceleration steps
left_duty_cycle = 0.0
right_duty_cycle = 0.0
acceleration_step = 0.01  # Step for acceleration
normal_deceleration_step = 0.02  # Step for smooth deceleration
braking_deceleration_step = 0.04  # Larger step for faster deceleration (braking)

# Define the serial ports for the left and right motors
left_serial_port = '/dev/ttyACM0'
right_serial_port = '/dev/ttyACM1'

def set_motor_duty_cycle(serial_port, duty_cycle):
    """Set the motor to the given duty cycle."""
    with serial.Serial(serial_port, baudrate=115200, timeout=0.05) as ser:
        ser.write(pyvesc.encode(SetDutyCycle(duty_cycle)))

def control_motors(stdscr):
    global left_duty_cycle, right_duty_cycle
    stdscr.nodelay(True)  # Non-blocking key input

    # Flags to track if keys are being held down
    left_motor_active = False
    right_motor_active = False
    left_braking = False
    right_braking = False

    try:
        while True:
            key = stdscr.getch()

            # Control Left Motor
            if key == ord('w'):  # Accelerate left motor
                left_duty_cycle += acceleration_step
                if left_duty_cycle > 1:
                    left_duty_cycle = 1
                left_motor_active = True
                left_braking = False
                stdscr.addstr(0, 0, f"Left motor accelerating: {left_duty_cycle}")

            elif key == ord('s'):  # Decelerate left motor faster (braking)
                left_braking = True
                left_motor_active = False
                stdscr.addstr(1, 0, f"Left motor braking: {left_duty_cycle}")

            else:
                left_motor_active = False

            # Control Right Motor
            if key == curses.KEY_UP:  # Accelerate right motor
                right_duty_cycle += acceleration_step
                if right_duty_cycle > 1:
                    right_duty_cycle = 1
                right_motor_active = True
                right_braking = False
                stdscr.addstr(2, 0, f"Right motor accelerating: {right_duty_cycle}")

            elif key == curses.KEY_DOWN:  # Decelerate right motor faster (braking)
                right_braking = True
                right_motor_active = False
                stdscr.addstr(3, 0, f"Right motor braking: {right_duty_cycle}")

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

            stdscr.refresh()
            time.sleep(0.1)

    except KeyboardInterrupt:
        # Stop motors if the script is interrupted
        set_motor_duty_cycle(left_serial_port, 0)
        set_motor_duty_cycle(right_serial_port, 0)
        stdscr.addstr(4, 0, "Motors stopped")
        stdscr.refresh()
        time.sleep(1)

if __name__ == "__main__":
    curses.wrapper(control_motors)
