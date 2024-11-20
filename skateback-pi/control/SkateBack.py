import serial
import socket
import sys
import time
import threading
import pyvesc
from pyvesc.VESC.messages import SetDutyCycle, SetCurrent, GetValues
import keyboard  # Assuming you have this for keyboard control
import SkateBackGPS

# Socket server config
HOST = 'localhost' 
PORT = 65432

# Constants
SERIAL_L = '/dev/ttyACM0'    # Serial Port for left motor
SERIAL_R = '/dev/ttyACM1'    # Serial Port for right motor
ACC_STEP = 0.02     # Increase initial acceleration step
DEC_STEP = 0.02     # Make deceleration match acceleration
BRK_STEP = 0.02     # Make braking smoother
MIN_DUTY_CYCLE = 0.05  # Minimum duty cycle to start movement
MAX_DUTY_CYCLE = 0.6   # Max duty cycle

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
        self.running = True  

        # Initialize serial connections for left and right wheels
        self.serial_left = serial.Serial(SERIAL_L, baudrate=115200, timeout=0.05)
        self.serial_right = serial.Serial(SERIAL_R, baudrate=115200, timeout=0.05)

        # Locks for thread safety when accessing serial ports
        self.lock_left = threading.Lock()
        self.lock_right = threading.Lock()

        # motor control threads
        self.left_thread = threading.Thread(target=self._motor_control_loop, args=("L",))
        self.right_thread = threading.Thread(target=self._motor_control_loop, args=("R",))
        self.left_thread.daemon = True
        self.right_thread.daemon = True
        self.left_thread.start()
        self.right_thread.start()

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

    def _motor_control_loop(self, wheel):
        """
        Continuous motor control loop that runs in a separate thread.
        """
        while self.running:
            try:
                if wheel == "L":
                    with self.lock_left:
                        duty_cycle = self.left_duty_cycle
                        self.serial_left.write(pyvesc.encode(SetDutyCycle(duty_cycle)))
                else:
                    with self.lock_right:
                        duty_cycle = self.right_duty_cycle
                        self.serial_right.write(pyvesc.encode(SetDutyCycle(duty_cycle)))
                time.sleep(0.05)  # 50ms update rate
            except Exception as e:
                print(f"Error in motor control loop for {wheel}: {e}")
                time.sleep(0.1)  # Wait before retrying

    def close(self):
        """
        Properly shut down the controller.
        """
        try:
            # Stop the motor control loops
            self.running = False
            time.sleep(0.1)  # Give threads time to stop
            
            # Emergency stop both motors
            self.emergency_stop()
            
            # Close serial connections
            if self.serial_left.is_open:
                self.serial_left.close()
            if self.serial_right.is_open:
                self.serial_right.close()
        except Exception as e:
            print(f"An error occurred while closing: {e}")

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
        Set a motor to a given duty cycle.
        """
        if not -MAX_DUTY_CYCLE <= duty_cycle <= MAX_DUTY_CYCLE:
            raise ValueError(f"Duty cycle must be between {-MAX_DUTY_CYCLE} and {MAX_DUTY_CYCLE}")

        try:
            if wheel == "L":
                with self.lock_left:
                    self.left_duty_cycle = duty_cycle
            elif wheel == "R":
                with self.lock_right:
                    self.right_duty_cycle = duty_cycle
            else:
                raise ValueError("Please specify 'L' or 'R' for wheel")

            if duration is not None:
                time.sleep(duration)

        except Exception as e:
            print(f"An error occurred in set_duty_cycle: {e}")
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
        try:
            # Start at MIN_DUTY_CYCLE if currently below it
            new_left_duty = max(MIN_DUTY_CYCLE, self.left_duty_cycle + ACC_STEP)
            new_right_duty = max(MIN_DUTY_CYCLE, self.right_duty_cycle + ACC_STEP)
            
            # Cap at MAX_DUTY_CYCLE
            new_left_duty = min(new_left_duty, MAX_DUTY_CYCLE)
            new_right_duty = min(new_right_duty, MAX_DUTY_CYCLE)
            
            self.set_duty_cycle("L", new_left_duty)
            self.set_duty_cycle("R", new_right_duty)
            
            print(f"New duty cycles - Left: {new_left_duty:.3f}, Right: {new_right_duty:.3f}")
        except Exception as e:
            print(f"Error in accelerate: {e}")
            self.emergency_stop()


    def decelerate(self):
        """
        Decelerate both wheels by decreasing the duty cycle. 
        Goes into negative duty cycle for reverse motion.
        """
        try:
            # Decrease by DEC_STEP, allowing negative values
            new_left_duty = self.left_duty_cycle - DEC_STEP
            new_right_duty = self.right_duty_cycle - DEC_STEP
            
            # Don't exceed negative MAX_DUTY_CYCLE
            new_left_duty = max(-MAX_DUTY_CYCLE, new_left_duty)
            new_right_duty = max(-MAX_DUTY_CYCLE, new_right_duty)
            
            # If magnitude is below MIN_DUTY_CYCLE but not zero, jump to next significant value
            if 0 > new_left_duty > -MIN_DUTY_CYCLE:
                new_left_duty = -MIN_DUTY_CYCLE
            if 0 > new_right_duty > -MIN_DUTY_CYCLE:
                new_right_duty = -MIN_DUTY_CYCLE
                
            self.set_duty_cycle("L", new_left_duty)
            self.set_duty_cycle("R", new_right_duty)
            
            print(f"New duty cycles - Left: {new_left_duty:.3f}, Right: {new_right_duty:.3f}")
        except Exception as e:
            print(f"Error in decelerate: {e}")
            self.emergency_stop()

    def stop(self):
        """
        Smoothly stop both wheels by gradually reducing duty cycle to zero.
        Handles both positive and negative duty cycles.
        """
        try:
            while abs(self.left_duty_cycle) > 0 or abs(self.right_duty_cycle) > 0:
                # Calculate new duty cycles
                if self.left_duty_cycle > 0:
                    new_left_duty = max(0, self.left_duty_cycle - BRK_STEP)
                else:
                    new_left_duty = min(0, self.left_duty_cycle + BRK_STEP)
                    
                if self.right_duty_cycle > 0:
                    new_right_duty = max(0, self.right_duty_cycle - BRK_STEP)
                else:
                    new_right_duty = min(0, self.right_duty_cycle + BRK_STEP)
                
                # If magnitude is below MIN_DUTY_CYCLE, go to 0
                if abs(new_left_duty) < MIN_DUTY_CYCLE:
                    new_left_duty = 0
                if abs(new_right_duty) < MIN_DUTY_CYCLE:
                    new_right_duty = 0
                
                # Set new duty cycles
                self.set_duty_cycle("L", new_left_duty)
                self.set_duty_cycle("R", new_right_duty)
                
                print(f"Stopping - Left: {new_left_duty:.3f}, Right: {new_right_duty:.3f}")
                time.sleep(0.05)  # Small delay for smooth deceleration
                
            print("Both wheels stopped smoothly.")
        except Exception as e:
            print(f"Error in stop: {e}")
            # If smooth stop fails, use emergency stop as fallback
            self.emergency_stop()

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
    
def socket_server(skateback):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f'Socket server listening on {HOST}:{PORT}')

        while True:
            conn, addr = s.accept()
            conn.settimeout(None)  # Make sure connection doesn't timeout
            print(f'Connected by {addr}')
            
            try:
                buffer = ""
                while True:
                    try:
                        data = conn.recv(1024).decode('utf-8')
                        if not data:
                            print("Client disconnected")
                            break
                        
                        buffer += data
                        
                        # Process any complete commands in buffer
                        while '\n' in buffer:
                            command, buffer = buffer.split('\n', 1)
                            command = command.strip()
                            
                            if command:
                                print(f'Received command: {command}')
                                try:
                                    response = handle_command(skateback, command)
                                    print(f'Command response: {response}')
                                    conn.sendall((response + '\n').encode('utf-8'))
                                except Exception as e:
                                    error_msg = f"Error executing command: {str(e)}\n"
                                    print(error_msg)
                                    conn.sendall(error_msg.encode('utf-8'))
                                    
                    except socket.error as e:
                        print(f"Socket error while receiving data: {e}")
                        break
                        
            except Exception as e:
                print(f"Error handling connection from {addr}: {e}")
            finally:
                try:
                    conn.close()
                    print(f"Connection with {addr} closed")
                except:
                    pass

# Update the handle_command function for better error handling
def handle_command(skateback, command):
    """
    Handle the received command by executing the corresponding action on the skateboard.
    """
    try:
        print(f"Executing command: {command}")  # Debug print
        if command == 'accelerate':
            skateback.accelerate()
            return "Successfully accelerated"
        elif command == 'decelerate':
            skateback.decelerate()
            return "Successfully decelerated"
        elif command == 'stop':
            skateback.stop()
            return "Successfully stopped"
        else:
            return f"Unknown command: {command}"
    except Exception as e:
        error_msg = f"Error executing command '{command}': {str(e)}"
        print(error_msg)  # Debug print
        return error_msg

if __name__ == "__main__":
    try:
        skateback = SkateBack()
        socket_server(skateback)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        print("Server stopped")