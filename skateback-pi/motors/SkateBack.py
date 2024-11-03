import serial
import time
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
        self.left_duty_cycle = 0.0
        self.right_duty_cycle = 0.0
        
    def __str__(self):
        return f"L: {self.left_duty_cycle}; R: {self.right_duty_cycle}"
        
    """
    Create a timer that returns true over a given duration
    [in] duration: amount of time to return true
    """
    def create_timer(self, duration):
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
    def set_duty_cycle(self, wheel, duration, duty_cycle):  
        # Set serialPort according to wheel parameter
        if wheel == "L":
            serialPort = SERIAL_L
        elif wheel == "R":
            serialPort = SERIAL_R
        else:
            raise Exception("Please specify L or R for wheel")
            
        # Create timer
        timer = self.create_timer(duration)
        
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

    """
    Get the current duty cycle for a motor
    [in] wheel: 'L' for left, 'R' for right, else throw error
    [out] duty_cycle: Current duty cycle for specified wheel
    """
    def get_duty_cycle(self, wheel):
        # Set serialPort according to wheel parameter
        if wheel == "L":
            serialPort = SERIAL_L
        elif wheel == "R":
            serialPort = SERIAL_R
        else:
            raise Exception("Please specify L or R for wheel")
        
        with serial.Serial(serialPort, baudrate=115200, timeout=0.05) as ser:
            while True:
                ser.write(pyvesc.encode_request(GetValues))
                if ser.in_waiting > 61:
                    (response, consumed) = pyvesc.decode(ser.read(61))

                    try:
                        return(response.duty_cycle_now)
                    except:
                        print("An error occured while waiting for a response")
                        pass

                # is this line necessary? it could stall what ever function calls set_duty_cycle
                time.sleep(0.1)

    """
    Accelerate a wheel using gradual increments of duty cycle
    [in] wheel: 'L' for left, 'R' for right, else throw error
    [in] target_duty_cycle: increment duty cycle until we reach this value
    """
    def accelerate_to(self, wheel, target_duty_cycle):
        current_duty_cycle = self.get_duty_cycle(wheel)

        while current_duty_cycle < target_duty_cycle <= MAX_DUTY_CYCLE:
            self.set_duty_cycle(wheel, duration=0.1, duty_cycle=current_duty_cycle)
            current_duty_cycle += ACC_STEP

    """
    Decelerate a wheel using gradual decrements of duty cycle
    [in] wheel: 'L' for left, 'R' for right, else throw error
    [in] target_duty_cycle: decrement duty cycle until we reach this value
    """
    def decelerate_to(self, wheel, target_duty_cycle):
        current_duty_cycle = self.get_duty_cycle(wheel)

        while current_duty_cycle > target_duty_cycle >= 0.0:
            self.set_duty_cycle(wheel, duration=0.1, duty_cycle=current_duty_cycle)
            current_duty_cycle -= DEC_STEP 

    """
    Bring duty cycle of a wheel to zero
    [in] wheel: 'L' for left, 'R' for right, else throw error
    """   
    def brake(self, wheel):
        current_duty_cycle = self.get_duty_cycle(wheel)

        while current_duty_cycle > 0.0:
            self.set_duty_cycle(wheel, duration=0.1, duty_cycle=current_duty_cycle)
            current_duty_cycle -= BRK_STEP

if __name__ == "__main__":
    sk = SkateBack()
    sk.accelerate_to("L", 0.5)
    sk.accelerate_to("R", 0.5)