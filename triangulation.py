#!/usr/bin/env python

import sys
import time
import random
import pigpio
import cv2
import imutils

class triangulation:
    
    def __init__(self):
        # Define system properties
        self.servo_pin = 18
        self.laser_pin = 16
        self.min_width = 550
        self.max_width = 2330
        self.ang2pulse = (self.max_width-self.min_width)/180.0
        self.pulse2ang = 1.0/self.ang2pulse
        self.low_ang = 1650
        self.hi_ang = 1950

        # Control variables for rotary motion
        self.step = 1.0*self.ang2pulse
        self.width = self.low_ang
        
        # Initialize the gpio class
        self.pi = pigpio.pi()
        if not self.pi.connected:
            exit()

        # Turn laser on
        self.pi.write(self.laser_pin,0)

        # Set laser to first position
        self.pi.set_servo_pulsewidth(self.servo_pin, self.width)
        time.sleep(5)

        self.cam = cv2.VideoCapture(0)
        cv2.startWindowThread()
        cv2.namedWindow("webcam")

    def updateFrame(self):            
        ret_val, img = self.cam.read()
        cv2.imshow("webcam",imutils.rotate(img,270))

    def incrementLaser(self):
        # Set servo pulse width
        self.pi.set_servo_pulsewidth(self.servo_pin, self.width)
        # Increment pulse width
        self.width += self.step
        # Bound the pulse width within min/max and invert the step when boundary
        # reached
        if self.width < self.low_ang or self.width > self.hi_ang:
            self.step = -self.step
            self.width += self.step

        print self.width

    def run(self):
        while True:
            try:
                # Grab next image and display it
                self.updateFrame()
                # Move laser to next position
                self.incrementLaser()
                # Delay for next frame
                time.sleep(0.25)
            except KeyboardInterrupt:
                break

        self.pi.set_servo_pulsewidth(self.servo_pin, 0)
        # Turn laser off
        self.pi.write(self.laser_pin,1)
        # Stop pigpio
        self.pi.stop()
        cv2.destroyAllWindows()
        
if __name__=='__main__':
    tr = triangulation()
    tr.run()

    

