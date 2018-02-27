#!/usr/bin/env python

import sys
import time
import random
import pigpio
import cv2

# Define servo pin number
SERVO_PIN = 18

# Zero angle pulse width
MIN_WIDTH=550
# Max angle (180 deg) pulse width
MAX_WIDTH=2330

# Angle to pulse conversion
ANG_TO_PULSE = (MAX_WIDTH-MIN_WIDTH)/180
# Pulse to angle conversion
PULSE_TO_ANG = 1/ANG_TO_PULSE

# Define step as 1 degree (converting to pulse)
step = 1*ANG_TO_PULSE
# Initialize starting width
width = MIN_WIDTH

# Initialize pigpio
pi = pigpio.pi()

# Make sure pigpio initialization was successful
if not pi.connected:
   exit()

# Move servo to initial position
pi.set_servo_pulsewidth(SERVO_PIN, width)
time.sleep(0.5)

# Define camera object
cam = cv2.VideoCapture(0)

def updateFrame():
	ret_val, img = cam.read()
	cv2.imshow("webcam",img)

def incrementLaser():
	# Set servo pulse width
	pi.set_servo_pulsewidth(SERVO_PIN, width)
	# Increment pulse width
	width += step
	# Bound the pulse width within min/max and invert the step when boundary
	# reached
	if width < MIN_WIDTH or width > MAX_WIDTH:
		step = -step
		width += step

def run():
    while True:
        try:
            # Grab next image and display it
            updateFrame()
            # Move laser to next position
            incrementLaser()
            # Delay for next frame
            time.sleep(0.1)
        except KeyboardInterrupt:
    		break

    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    # Stop pigpio
    pi.stop()

if __name__='__main__':
    run()

'''
# Run until keyboard interrupt
while True:

	try:
		# Set servo pulse width
		pi.set_servo_pulsewidth(SERVO_PIN, width)
		# Increment pulse width
		width += step
		# Bound the pulse width within min/max and invert the step when boundary
		# reached
		if width < MIN_WIDTH or width > MAX_WIDTH:
			step = -step
			width += step
		# Delay to slow rotation
		time.sleep(0.1)

	except KeyboardInterrupt:
		break

# Set pulse width to zero
pi.set_servo_pulsewidth(SERVO_PIN, 0)
# Stop pigpio
pi.stop()
'''
