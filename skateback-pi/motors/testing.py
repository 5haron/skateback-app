import threading
from . import SkateBack
import time

def test_with_keyboard():
    with SkateBack.SkateBack() as sk:
        try:
            # Create threads for left and right wheels using keyboard control
            left_thread = threading.Thread(target=sk.keyboard_control, args=("L",))
            right_thread = threading.Thread(target=sk.keyboard_control, args=("R",))

            # Start both threads
            left_thread.start()
            right_thread.start()

            # Wait for both threads to complete
            left_thread.join()
            right_thread.join()

            print("Keyboard control threads have been terminated.")

        except KeyboardInterrupt:
            # Handle emergency stop on keyboard interrupt
            sk.emergency_stop()
            print("Emergency stop initiated due to KeyboardInterrupt.")

        except Exception as e:
            # Handle any other exceptions
            sk.emergency_stop()
            print(f"An error occurred: {e}")

def static_test():
    with SkateBack.SkateBack() as sk:
        try:
            # Define the duty cycle and duration
            duty_cycle_L = 0.1  # Set desired duty cycle between -1.0 and 1.0
            duty_cycle_R = -0.1  # Set desired duty cycle between -1.0 and 1.0

            # Create threads for left and right wheels
            left_thread = threading.Thread(target=sk.accelerate_to, args=("L", duty_cycle_L))
            right_thread = threading.Thread(target=sk.accelerate_to, args=("R", duty_cycle_R))

            # Start both threads
            left_thread.start()
            right_thread.start()

            # Wait for both threads to complete
            left_thread.join()
            right_thread.join()

            print("Both wheels have completed rotation.")

        except KeyboardInterrupt:
            # Handle emergency stop on keyboard interrupt
            sk.emergency_stop()
            print("Emergency stop initiated due to KeyboardInterrupt.")

        except Exception as e:
            # Handle any other exceptions
            sk.emergency_stop()
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    static_test()
    # test_with_keyboard()
    with SkateBack.SkateBack() as skateback:
        skateback.navigate_to((0.0, 0.0))