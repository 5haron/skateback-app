import pyvesc
from pyvesc.VESC.messages import SetDutyCycle
import serial
import time

ACC_STEP = 0.01    # Duty Cycle step for acceleration
DEC_STEP = 0.02    # Duty Cycle step for deceleration
BRK_STEP = 0.04    # Duty Cycle step for breaking
SERIAL_L = '/dev/ttyACM0'    # Serial Port for left motor
SERIAL_R = '/dev/ttyACM1'    # Serial Port for right motor
MAX_DUTY_CYCLE = 1.0    # Max duty cycle


class SkateBack:
    def __init__(self):
        self.left_duty_cycle = 0.0
        self.right_duty_cycle = 0.0
        
    def __str__(self):
        return f"L: {self.left_duty_cycle}; R: {self.right_duty_cycle}"
        
    """
    Create a timer that returns true over a given duration
    """
    def create_timer(duration):
        start_time = time.time()
        def time_check():
            return (time.time() - start_time) < duration
        return time_check

    """
    Set a motor to a given duty cycle for a given duration
    [in] wheel: 'L' for left, 'R' for right, else throw error
    [in] duration: amount of time to maintain duty cycle
    [in] dut_cycle: duty cycle to set wheel at, magnitude cannot exceed MAX_DUTY_CYCLE
    """
    def spin_motor(wheel, duration, duty_cycle):  
        # Set serialPort according to wheel parameter
        if wheel == "L":
            serialPort = SERIAL_L
        elif wheel == "R":
            serialPort = SERIAL_R
        else:
            error("Please specify L or R for wheel")
            
        # Create timer
        timer = create_timer(duration)
        
        with serial.Serial(serialPort, baudrate=115200, timeout=0.05) as ser:
            try:
                while timer():
                    # Use PyVESC to encode SetDutyCycle msg ...
                    # ... then write to a serial port
                    ser.write(pyvesc.encode(SetDutyCycle(duty_cycle)))
                    
                    # Sleep to avoid overwhelming VESC with commands
                    time.sleep(0.1)
            except KeyboardInterrupt:
                # Turn Off the VESC
                ser.write(pyvesc.encode(SetCurrent(0)))
            finally:
                # Close serial connection
                ser.close()

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
