from machine import Pin, PWM
import math

MAX_DUTY = 65535

pwm = PWM(Pin(0)) 
pwm.freq(1000)

def set_pwm_from_float(float_value, pwm_object):
    """
    Converts a float from -1.0 to 1.0 into a 0-65535 PWM duty cycle 
    and sets the duty cycle on the given PWM object.
    """
    
    clamped_value = max(-1.0, min(1.0, float_value))

    # (clamped_value + 1.0) / 2.0 converts [-1.0, 1.0] to [0.0, 1.0]
    scaled_value = (clamped_value + 1.0) / 2.0
    
    # Map to the 0-65535 range
    duty_cycle_value = int(scaled_value * MAX_DUTY)
    
    pwm_object.duty_u16(duty_cycle_value)
    
    print(f"Float: {float_value: .2f} -> Duty: {duty_cycle_value}")
    return duty_cycle_value



# Full ON (100% duty cycle)
set_pwm_from_float(1.0, pwm) # Result should be 65535

# Half ON (50% duty cycle)
set_pwm_from_float(0.0, pwm) # Result should be 32767 (approx)

# 25% duty cycle
set_pwm_from_float(-0.5, pwm) # Result should be 16383 (approx)

# Full OFF (0% duty cycle)
set_pwm_from_float(-1.0, pwm) # Result should be 0

# pwm.deinit()