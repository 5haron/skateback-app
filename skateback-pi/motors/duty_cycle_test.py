import pyvesc
from pyvesc.VESC.messages import GetValues, SetRPM, SetDutyCycle, SetCurrent, SetRotorPositionMode, GetRotorPosition
import serial
import time

# Notes: 
# Duty cycle ranges from 1e5 to -1e5
# It seems that negative duty cycle moves the board forward

def create_timer(duration):
    start_time = time.time()
    def time_check():
        return (time.time() - start_time) < duration
    return time_check

def spin_motor(wheel, duration=3, duty_cycle=0.1):
    # Assign serialPort according to wheel param
    if wheel == "L":
        serialPort = '/dev/ttyACM0'
    elif wheel == "R":
        serialPort = '/dev/ttyACM1'
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


if __name__ == "__main__":
    duty_cycle = 0.1
    while duty_cycle < 0.5:
        spin_motor("R", duration=0.1, duty_cycle=duty_cycle)
        duty_cycle += 0.01
        
    duty_cycle = 0.1
    while duty_cycle < 0.5:
        spin_motor("L", duration=0.1, duty_cycle=duty_cycle)
        duty_cycle += 0.01
        
    spin_motor("R", 3, -0.3)
    time.sleep(2)
    spin_motor("R", 3, 0.3)
