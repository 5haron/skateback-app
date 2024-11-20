import threading
import SkateBack
import SkateBackGPS
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
            duty_cycle_L = -0.1  # Set desired duty cycle between -1.0 and 1.0
            duty_cycle_R = 0.1  # Set desired duty cycle between -1.0 and 1.0

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

def turn_test():
    with SkateBack.SkateBack() as sk:
        try:
            # Turn left
            sk.turn_left(target_duty_cycle=0.1)

            # Turn right
            sk.turn_right(target_duty_cycle=0.1)

            print("Turn test completed.")

        except KeyboardInterrupt:
            sk.emergency_stop()
            print("Emergency stop initiated due to KeyboardInterrupt.")

        except Exception as e:
            sk.emergency_stop()
            print(f"An error occurred: {e}")

def direction_test():
    with SkateBack.SkateBack() as sk:
        try:
            print("Testing left wheel with positive duty cycle...")
            sk.set_duty_cycle("L", 0.1)
            time.sleep(2)
            sk.set_duty_cycle("L", 0.0)
            time.sleep(1)
            
            print("Testing left wheel with negative duty cycle...")
            sk.set_duty_cycle("L", -0.1)
            time.sleep(2)
            sk.set_duty_cycle("L", 0.0)
            time.sleep(1)
            
            print("Testing right wheel with positive duty cycle...")
            sk.set_duty_cycle("R", 0.1)
            time.sleep(2)
            sk.set_duty_cycle("R", 0.0)
            time.sleep(1)
            
            print("Testing right wheel with negative duty cycle...")
            sk.set_duty_cycle("R", -0.1)
            time.sleep(2)
            sk.set_duty_cycle("R", 0.0)
            
            print("Direction test completed.")
            
        except KeyboardInterrupt:
            sk.emergency_stop()
            print("Emergency stop initiated due to KeyboardInterrupt.")
        except Exception as e:
            sk.emergency_stop()
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    direction_test()
    # turn_test()
    # sk_gps = SkateBackGPS.SkateBackGPS()
    # sk_gps.get_location()
    # test_with_keyboard()