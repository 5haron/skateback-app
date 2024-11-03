import threading
import SkateBack
import time

if __name__ == "__main__":
    with SkateBack.SkateBack() as sk:
        try:
            # Define the duty cycle and duration
            duty_cycle_L = 0.2  # Set desired duty cycle between -1.0 and 1.0
            duty_cycle_R = -0.35  # Set desired duty cycle between -1.0 and 1.0

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
