import RPi.GPIO as gpio
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

#steering linear actuator driver pins
pwm = 19
steering_direction = 26

#steering linear actuator limit switch pins
left_limit = 23
right_limit = 24

#steering encoder (potentiometer) address
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
left_steering_encoder = AnalogIn(ads, ADS.P0)
right_steering_encoder = AnalogIn(ads, ADS.P1)
steering_tolerance = 0.05

def init():
    gpio.setmode(gpio.BCM)
    gpio.setup(steering_direction, gpio.OUT)
    gpio.output(steering_direction, False)
    gpio.setup(pwm, gpio.OUT)
    gpio.output(pwm, False)


    gpio.setup(left_limit, gpio.IN)
    gpio.setup(right_limit, gpio.IN)


#steer left = 1, steer right = -1, stop = 0
def set_motor_power(direction):
    if direction == -1:
        gpio.output(steering_direction, True)
        gpio.output(pwm, True)
        return
    elif direction == 1:
        gpio.output(steering_direction, False)
        gpio.output(pwm, True)
        return
    else:
        gpio.output(steering_direction, False)
        gpio.output(pwm, False)
        return


def read_steering_encoder(steering_encoder):
    if steering_encoder == 1:
        steering_encoder_val = left_steering_encoder.value
    else:
        steering_encoder_val = right_steering_encoder.value
    print(steering_encoder_val)
    return steering_encoder_val


#range for steering is max left = 1, max right = -1
def read_steering_encoder_angle(steering_encoder):
    if steering_encoder == 1:
        steering_encoder_val = left_steering_encoder.value
    else:
        steering_encoder_val = right_steering_encoder.value
    steering_encoder_val = (steering_encoder_val - steering_range / 2) / steering_range
    print(steering_encoder_val)
    return steering_encoder_val
    

def steer_to_angle(target_angle):
    current_angle = read_steering_encoder_angle(1)
    if abs(target_angle-current_angle)<steering_tolerance:
        return
    elif target_angle > current_angle:
        while not gpio.input(left_limit) or not abs(target_angle-current_angle)<steering_tolerance:
            set_motor_power(1)
            current_angle = read_steering_encoder_angle(1)
        set_motor_power(0)
    elif target_angle < current_angle:
        while not gpio.input(right_limit) or not abs(target_angle-current_angle)<steering_tolerance:
            set_motor_power(-1)
            current_angle = read_steering_encoder_angle(1)
        set_motor_power(0)
        


def steering_cal():
    global steering_range
    
    left_max_mean_left_encoder = 0
    right_max_mean_left_encoder = 0
    left_mean_right_encoder = 0
    right_mean_right_encoder = 0
    
    while not gpio.input(left_limit):
        set_motor_power(1)
    set_motor_power(0)
    for _ in range(10):
        reading = read_steering_encoder(1)
        left_max_mean_left_encoder += reading 
    left_max_mean_left_encoder /= 10
    #for _ in range(10):
    #    reading = read_steering_encoder(right_steering_encoder)
    #    left_max_mean_right_encoder += reading 
    #left_max_mean_right_encoder /= 10
    
    while not gpio.input(right_limit):
        set_motor_power(-1)
    set_motor_power(0)
    for _ in range(10):
        reading = read_steering_encoder(1)
        right_max_mean_left_encoder += reading
    right_max_mean_left_encoder /= 10
    #for _ in range(10):
    #    reading = read_steering_encoder(right_steering_encoder)
    #    right_max_mean_right_encoder += reading 
    #right_max_mean_right_encoder /= 10
    
    #mono-encoder steering
    steering_range = (left_max_mean_left_encoder - right_max_mean_left_encoder)
    print(f"steering_range: {steering_range}")
    steer_to_angle(0)
    print("Steering calibration complete")


if __name__ == "__main__":        
    init()
    steering_cal()
    print("done")
    gpio.cleanup()
    
    