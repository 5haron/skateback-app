Our motors and motor control systems exhibit unique characteristics that necessitate special handling.

Under normal circumstances, we would accelerate by reading the current duty cycle and incrementally increasing it by a small step, repeating this process until we reach the desired acceleration.

However, due to issues with our Hall sensor, we cannot read the duty cycle from the VESC directly. Instead, we have opted to use internal state management within the SkateBack class. This approach is not without its flaws.

A single call to sk.accelerate_to(wheel, current_duty_cycle + CONTROL_ACC_STEP) sets the duty cycle of the corresponding wheel to current_duty_cycle + CONTROL_ACC_STEP for a duration of 0.1 seconds. The internal state management then updates our current duty cycle by CONTROL_ACC_STEP. However, if the duration expires and a new command is not received, the VESC stops the wheel from spinning. We cannot reset our internal state back to zero, because this would cause stuttering and prevent us from increasing speed. The duration parameter is necessary because, without it, we would need an infinite loop to maintain the duty cycle, but then we cannot accelerate because the process gets stuck in the acceleration increment loop.

To maintain speed, I propose that we send two signals—a 'W' and an 'S'—in quick succession. Due to our small CONTROL_ACC_STEP, this approach maintains approximately the same speed without the infinite loop issue. To increase acceleration, we send two 'W's and a single 'S'; to decrease, we send two 'S's and a single 'W'.

Note:
A 'W' is a signal to sk.accelerate_to(wheel, current_duty_cycle + CONTROL_ACC_STEP)
A 'S' is a signal to sk.decelerate_to(wheel, current_duty_cycle - CONTROL_DEC_STEP)
                    