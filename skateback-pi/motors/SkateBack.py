import serial
import time
import threading
import pyvesc
from pyvesc.VESC.messages import SetDutyCycle, SetCurrent, GetValues

ACC_STEP = 0.01    # Duty Cycle step for acceleration
DEC_STEP = 0.02    # Duty Cycle step for deceleration
BRK_STEP = 0.04    # Duty Cycle step for breaking
SERIAL_L = '/dev/ttyACM0'    # Serial Port for left motor
SERIAL_R = '/dev/ttyACM1'    # Serial Port for right motor
MAX_DUTY_CYCLE = 0.6    # Max duty cycle

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
            target_duty_cycle (float): Duty cycle to reach, between -MAX_DUTY_CYCLE and MAX_DUTY_CYCLE.

        Raises:
            ValueError: If target_duty_cycle is outside the valid range or invalid acceleration direction.
        """
        if not -MAX_DUTY_CYCLE <= target_duty_cycle <= MAX_DUTY_CYCLE:
            raise ValueError(f"Target duty cycle must be between {-MAX_DUTY_CYCLE} and {MAX_DUTY_CYCLE}")

        current_duty_cycle = self.get_duty_cycle(wheel)

        # Determine the direction of acceleration
        if target_duty_cycle > current_duty_cycle:
            # Accelerate forwards (positive duty cycle)
            step = ACC_STEP
        elif target_duty_cycle < current_duty_cycle:
            # Accelerate backwards (negative duty cycle)
            step = -ACC_STEP
        else:
            # Target duty cycle is equal to current; no action needed
            return

        # Accelerate towards target duty cycle without exceeding MAX_DUTY_CYCLE in magnitude
        while (step > 0 and current_duty_cycle < target_duty_cycle) or \
            (step < 0 and current_duty_cycle > target_duty_cycle):
            current_duty_cycle += step
            # Prevent overshooting the target duty cycle
            if (step > 0 and current_duty_cycle > target_duty_cycle) or \
            (step < 0 and current_duty_cycle < target_duty_cycle):
                current_duty_cycle = target_duty_cycle
            # Ensure duty cycle does not exceed MAX_DUTY_CYCLE in magnitude
            if abs(current_duty_cycle) > MAX_DUTY_CYCLE:
                current_duty_cycle = MAX_DUTY_CYCLE if current_duty_cycle > 0 else -MAX_DUTY_CYCLE
            self.set_duty_cycle(wheel, duration=0.1, duty_cycle=current_duty_cycle)

    def decelerate_to(self, wheel, target_duty_cycle):
        """
        Gradually decelerate a wheel to a target duty cycle.

        Args:
            wheel (str): 'L' for left, 'R' for right.
            target_duty_cycle (float): Duty cycle to reach, between -MAX_DUTY_CYCLE and MAX_DUTY_CYCLE.

        Raises:
            ValueError: If target_duty_cycle is outside the valid range or invalid deceleration direction.
        """
        if not -MAX_DUTY_CYCLE <= target_duty_cycle <= MAX_DUTY_CYCLE:
            raise ValueError(f"Target duty cycle must be between {-MAX_DUTY_CYCLE} and {MAX_DUTY_CYCLE}")

        current_duty_cycle = self.get_duty_cycle(wheel)

        # Determine the direction of deceleration
        if current_duty_cycle > target_duty_cycle:
            # Decelerate forwards (positive duty cycle towards zero or negative)
            step = -DEC_STEP
        elif current_duty_cycle < target_duty_cycle:
            # Decelerate backwards (negative duty cycle towards zero or positive)
            step = DEC_STEP
        else:
            # Target duty cycle is equal to current; no action needed
            return

        # Decelerate towards target duty cycle without exceeding MAX_DUTY_CYCLE in magnitude
        while (step < 0 and current_duty_cycle > target_duty_cycle) or \
            (step > 0 and current_duty_cycle < target_duty_cycle):
            current_duty_cycle += step
            # Prevent overshooting the target duty cycle
            if (step < 0 and current_duty_cycle < target_duty_cycle) or \
            (step > 0 and current_duty_cycle > target_duty_cycle):
                current_duty_cycle = target_duty_cycle
            # Ensure duty cycle does not exceed MAX_DUTY_CYCLE in magnitude
            if abs(current_duty_cycle) > MAX_DUTY_CYCLE:
                current_duty_cycle = MAX_DUTY_CYCLE if current_duty_cycle > 0 else -MAX_DUTY_CYCLE
            self.set_duty_cycle(wheel, duration=0.1, duty_cycle=current_duty_cycle)

    def brake(self, wheel):
        """
        Gradually bring the duty cycle of a wheel to zero.

        Args:
            wheel (str): 'L' for left, 'R' for right.
        """
        current_duty_cycle = self.get_duty_cycle(wheel)
        target_duty_cycle = 0.0  # Since we're braking to zero

        # Determine the direction of braking
        if current_duty_cycle > 0:
            step = -BRK_STEP  # Decrease duty cycle towards zero
        elif current_duty_cycle < 0:
            step = BRK_STEP   # Increase duty cycle towards zero
        else:
            # Duty cycle is already zero; no action needed
            return

        # Brake towards zero
        while current_duty_cycle != target_duty_cycle:
            current_duty_cycle += step
            # Prevent overshooting zero
            if (step < 0 and current_duty_cycle < target_duty_cycle) or \
            (step > 0 and current_duty_cycle > target_duty_cycle):
                current_duty_cycle = target_duty_cycle
            self.set_duty_cycle(wheel, duration=0.1, duty_cycle=current_duty_cycle)

    def emergency_stop(self):
        """
        Immediately stop both wheels by setting current to zero.
        """
        try:
            with self.lock_left:
                self.serial_left.write(pyvesc.encode(SetCurrent(0)))
                self.left_duty_cycle = 0.0
            with self.lock_right:
                self.serial_right.write(pyvesc.encode(SetCurrent(0)))
                self.right_duty_cycle = 0.0
        except Exception as e:
            print(f"An error occurred during emergency_stop: {e}")
            raise