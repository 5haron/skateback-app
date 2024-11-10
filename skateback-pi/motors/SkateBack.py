import serial
import sys
import time
import threading
import pyvesc
from pyvesc.VESC.messages import SetDutyCycle, SetCurrent, GetValues
import keyboard  # Assuming you have this for keyboard control

# Constants
ACC_STEP = 0.005    # Duty Cycle step for acceleration
DEC_STEP = 0.02     # Duty Cycle step for deceleration
BRK_STEP = 0.04     # Duty Cycle step for braking
SERIAL_L = '/dev/ttyACM0'    # Serial Port for left motor
SERIAL_R = '/dev/ttyACM1'    # Serial Port for right motor
MAX_DUTY_CYCLE = 0.6         # Max duty cycle

# Constants for keyboard control
CONTROL_ACC_STEP = 0.02      # Control acceleration step
CONTROL_DEC_STEP = 0.02      # Control deceleration step

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

    def set_duty_cycle(self, wheel, duty_cycle, duration=None):
        """
        Set a motor to a given duty cycle. If duration is provided, maintain the duty cycle for that duration.
        If duration is omitted, maintain the duty cycle indefinitely.

        Args:
            wheel (str): 'L' for left, 'R' for right.
            duty_cycle (float): Duty cycle to set, must be between -MAX_DUTY_CYCLE and MAX_DUTY_CYCLE.
            duration (float, optional): Amount of time to maintain the duty cycle. If None, maintain indefinitely.

        Raises:
            ValueError: If duty_cycle is outside the valid range.
        """
        if not -MAX_DUTY_CYCLE <= duty_cycle <= MAX_DUTY_CYCLE:
            raise ValueError(f"Duty cycle must be between {-MAX_DUTY_CYCLE} and {MAX_DUTY_CYCLE}")

        # If duration is provided, create timer; else, define timer that always returns True
        if duration is not None:
            timer = self.create_timer(duration)
        else:
            # Timer that always returns True
            def timer():
                return True

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
                    time.sleep(0.05)

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
            self.set_duty_cycle(wheel, current_duty_cycle, duration=0.1)

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
            self.set_duty_cycle(wheel, current_duty_cycle, duration=0.1)

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
            self.set_duty_cycle(wheel, current_duty_cycle, duration=0.1)

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

    def accelerate(self):
        """
        Accelerate both wheels by increasing the duty cycle.
        """
        target_duty_cycle = min(self.left_duty_cycle + ACC_STEP, MAX_DUTY_CYCLE)
        left_thread = threading.Thread(target=self.accelerate_to, args=("L", 0.2))
        right_thread = threading.Thread(target=self.accelerate_to, args=("R", 0.2))

        # Start both threads at the same time
        left_thread.start()
        right_thread.start()

        # Wait for both to finish
        left_thread.join()
        right_thread.join()

    def decelerate(self):
        """
        Decelerate both wheels by decreasing the duty cycle.
        """
        target_duty_cycle = max(self.left_duty_cycle - DEC_STEP, -MAX_DUTY_CYCLE)
        left_thread = threading.Thread(target=self.decelerate_to, args=("L", target_duty_cycle))
        right_thread = threading.Thread(target=self.decelerate_to, args=("R", target_duty_cycle))

        # Start both threads at the same time
        left_thread.start()
        right_thread.start()

        # Wait for both to finish
        left_thread.join()
        right_thread.join()

    def stop(self):
        """
        Immediately stop both wheels by setting duty cycle to zero.
        """
        self.emergency_stop()
        print("Both wheels stopped.")

    def keyboard_control(self, wheel):
        """
        Control the duty cycle of a wheel using keyboard inputs.

        For the left wheel ('L'), 'W' increases acceleration and 'S' decreases it.
        For the right wheel ('R'), 'Up' increases acceleration and 'Down' decreases it.

        Args:
            wheel (str): 'L' for left, 'R' for right.
        """
        if wheel == 'L':
            key_increase = 'w'
            key_decrease = 's'
        elif wheel == 'R':
            key_increase = 'up'
            key_decrease = 'down'
        else:
            raise ValueError("Please specify 'L' or 'R' for wheel")

        try:
            # Start listening for key presses in the background
            keyboard.on_press(self._make_on_press(wheel, key_increase, key_decrease))

            # Keep the thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.emergency_stop()
            print(f"Emergency stop initiated due to KeyboardInterrupt in wheel {wheel}.")
        except Exception as e:
            self.emergency_stop()
            print(f"An error occurred in keyboard_control: {e}")

    def _make_on_press(self, wheel, key_increase, key_decrease):
        def on_press(event):
            try:
                key = event.name
                if key == key_increase:
                    current_duty_cycle = self.get_duty_cycle(wheel)
                    target_duty_cycle = current_duty_cycle + CONTROL_ACC_STEP
                    if target_duty_cycle > MAX_DUTY_CYCLE:
                        target_duty_cycle = MAX_DUTY_CYCLE
                    self.accelerate_to(wheel, target_duty_cycle)
                elif key == key_decrease:
                    current_duty_cycle = self.get_duty_cycle(wheel)
                    target_duty_cycle = current_duty_cycle - CONTROL_DEC_STEP
                    if target_duty_cycle < -MAX_DUTY_CYCLE:
                        target_duty_cycle = -MAX_DUTY_CYCLE
                    self.decelerate_to(wheel, target_duty_cycle)
            except Exception as e:
                print(f"Error in on_press handler: {e}")
        return on_press

if __name__ == "__main__":
    skateback = SkateBack()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        print(f"Executing command: {command}") 
        if command == "accelerate":
            skateback.accelerate()
        elif command == "decelerate":
            skateback.decelerate()
        elif command == "stop":
            skateback.stop()
        else:
            print(f"Unknown command: {command}")
    else:
        print("No command provided")
