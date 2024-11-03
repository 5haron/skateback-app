import serial
import time
import threading
import pyvesc
from pyvesc import SetDutyCycle, SetCurrent, GetValues

ACC_STEP = 0.01    # Duty Cycle step for acceleration
DEC_STEP = 0.02    # Duty Cycle step for deceleration
BRK_STEP = 0.04    # Duty Cycle step for breaking
SERIAL_L = '/dev/ttyACM0'    # Serial Port for left motor
SERIAL_R = '/dev/ttyACM1'    # Serial Port for right motor
MAX_DUTY_CYCLE = 1.0    # Max duty cycle

class SkateBack:
    def __init__(self):
        """
        Initialize the SkateBack controller.

        Sets up duty cycles and opens serial connections for the left and right wheels.
        """
        self.left_duty_cycle = 0.0
        self.right_duty_cycle = 0.0

        # Initialize serial connections for left and right wheels
        self.serial_left = serial.Serial(SERIAL_L, baudrate=115200, timeout=0.05)
        self.serial_right = serial.Serial(SERIAL_R, baudrate=115200, timeout=0.05)

        # Locks for thread safety when accessing serial ports
        self.lock_left = threading.Lock()
        self.lock_right = threading.Lock()

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
        
    def __str__(self):
        """
        Return a string representation of the current duty cycles.
        """
        return f"L: {self.left_duty_cycle}; R: {self.right_duty_cycle}"
    
    def close(self):
        """
        Close the serial connections for both wheels.
        """
        try:
            if self.serial_left.is_open:
                self.serial_left.close()
            if self.serial_right.is_open:
                self.serial_right.close()
        except Exception as e:
            print(f"An error occurred while closing serial connections: {e}")
        
    def create_timer(self, duration):
        """
        Create a timer function that returns True for a given duration.

        Args:
            duration (float): Amount of time to return True.

        Returns:
            function: A function that returns True until the duration has elapsed.
        """
        start_time = time.time()
        def time_check():
            return (time.time() - start_time) < duration
        return time_check

    def set_duty_cycle(self, wheel, duration, duty_cycle):  
        """
        Set a motor to a given duty cycle for a specified duration.

        Args:
            wheel (str): 'L' for left, 'R' for right.
            duration (float): Amount of time to maintain the duty cycle.
            duty_cycle (float): Duty cycle to set, must be between -MAX_DUTY_CYCLE and MAX_DUTY_CYCLE.

        Raises:
            ValueError: If duty_cycle is outside the valid range.
        """
        if not -MAX_DUTY_CYCLE <= duty_cycle <= MAX_DUTY_CYCLE:
            raise ValueError(f"Duty cycle must be between {-MAX_DUTY_CYCLE} and {MAX_DUTY_CYCLE}")

        # Create timer
        timer = self.create_timer(duration)

        try:
            if wheel == "L":
                serial_port = self.serial_left
                lock = self.lock_left
            elif wheel == "R":
                serial_port = self.serial_right
                lock = self.lock_right
            else:
                raise ValueError("Please specify 'L' or 'R' for wheel")

            with lock:
                while timer():
                    # Encode and send SetDutyCycle command
                    serial_port.write(pyvesc.encode(SetDutyCycle(duty_cycle)))
                    # Update duty cycle state
                    if wheel == "L":
                        self.left_duty_cycle = duty_cycle
                    else:
                        self.right_duty_cycle = duty_cycle
                    # Sleep to prevent overwhelming the VESC
                    time.sleep(0.1)

        except KeyboardInterrupt:
            # Stop the motor immediately
            serial_port.write(pyvesc.encode(SetCurrent(0)))
            raise
        except Exception as e:
            print(f"An error occurred in set_duty_cycle: {e}")
            serial_port.write(pyvesc.encode(SetCurrent(0)))
            raise

    def get_duty_cycle(self, wheel):
        """
        Get the current duty cycle for a motor from internal state.

        Args:
            wheel (str): 'L' for left, 'R' for right.

        Returns:
            float: Current duty cycle for the specified wheel.
        """
        if wheel == "L":
            with self.lock_left:
                return self.left_duty_cycle
        elif wheel == "R":
            with self.lock_right:
                return self.right_duty_cycle
        else:
            raise ValueError("Please specify 'L' or 'R' for wheel")

    def accelerate_to(self, wheel, target_duty_cycle):
        """
        Gradually accelerate a wheel to a target duty cycle.

        Args:
            wheel (str): 'L' for left, 'R' for right.
            target_duty_cycle (float): Duty cycle to reach, between 0.0 and MAX_DUTY_CYCLE.

        Raises:
            ValueError: If target_duty_cycle is outside the valid range.
        """
        if not 0.0 <= target_duty_cycle <= MAX_DUTY_CYCLE:
            raise ValueError(f"Target duty cycle must be between 0.0 and {MAX_DUTY_CYCLE}")

        current_duty_cycle = self.get_duty_cycle(wheel)
        while current_duty_cycle < target_duty_cycle:
            current_duty_cycle += ACC_STEP
            if current_duty_cycle > target_duty_cycle:
                current_duty_cycle = target_duty_cycle
            self.set_duty_cycle(wheel, duration=0.1, duty_cycle=current_duty_cycle)

    def decelerate_to(self, wheel, target_duty_cycle):
        """
        Gradually decelerate a wheel to a target duty cycle.

        Args:
            wheel (str): 'L' for left, 'R' for right.
            target_duty_cycle (float): Duty cycle to reach, between 0.0 and MAX_DUTY_CYCLE.

        Raises:
            ValueError: If target_duty_cycle is outside the valid range.
        """
        if not 0.0 <= target_duty_cycle <= MAX_DUTY_CYCLE:
            raise ValueError(f"Target duty cycle must be between 0.0 and {MAX_DUTY_CYCLE}")

        current_duty_cycle = self.get_duty_cycle(wheel)
        while current_duty_cycle > target_duty_cycle:
            current_duty_cycle -= DEC_STEP
            if current_duty_cycle < target_duty_cycle:
                current_duty_cycle = target_duty_cycle
            self.set_duty_cycle(wheel, duration=0.1, duty_cycle=current_duty_cycle)
    
    def brake(self, wheel):
        """
        Gradually bring the duty cycle of a wheel to zero.

        Args:
            wheel (str): 'L' for left, 'R' for right.
        """
        current_duty_cycle = self.get_duty_cycle(wheel)
        target_duty_cycle = 0.0  # Since we're braking to zero

        while current_duty_cycle != target_duty_cycle:
            if current_duty_cycle > target_duty_cycle:
                current_duty_cycle -= BRK_STEP
                # Prevent overshooting the target
                if current_duty_cycle < target_duty_cycle:
                    current_duty_cycle = target_duty_cycle
            elif current_duty_cycle < target_duty_cycle:
                current_duty_cycle += BRK_STEP
                if current_duty_cycle > target_duty_cycle:
                    current_duty_cycle = target_duty_cycle
            else:
                # Duty cycle is already at target; exit loop
                break

            self.set_duty_cycle(wheel, duration=0.1, duty_cycle=current_duty_cycle)
