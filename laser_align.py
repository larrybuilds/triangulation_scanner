#!/usr/bin/env python

import sys
import time
import random
import pigpio
import cv2
import imutils
import numpy as np
import math

class laser_align:
    
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
        self.print_px_color = False
        self.x = 0
        self.y = 0

        # Control variables for rotary motion
        self.width = 1863
        
        # Initialize the gpio class
        self.pi = pigpio.pi()
        if not self.pi.connected:
            exit()

        # Turn laser on
        self.pi.write(self.laser_pin,0)

        # Set laser to first position
        self.pi.set_servo_pulsewidth(self.servo_pin, self.width)
        time.sleep(1)

        self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH,1280)
        self.cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT,960)
        self.cam.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS,0.12)
        # Set video contrast
        self.cam.set(cv2.cv.CV_CAP_PROP_CONTRAST,0.235)
        # Set video saturation
        self.cam.set(cv2.cv.CV_CAP_PROP_SATURATION,1)
        # Set video gain
        self.cam.set(cv2.cv.CV_CAP_PROP_GAIN,0.04)

        cv2.startWindowThread()
        cv2.namedWindow("webcam")
        cv2.setMouseCallback("webcam",self.onMouse)

    def updateFrame(self):            
        ret_val, img = self.cam.read()
        
        lb = np.array([0,0,100])
        hb = np.array([100,100,255])
        redline = cv2.inRange(img,lb,hb)
        if self.print_px_color == True:
            print("X(%d) Y(%d) RGB(%d,%d,%d)"%(self.x,self.y,img[self.y,self.x,0],img[self.y,self.x,1],img[self.y,self.x,2]))
            self.print_px_color = False
        cv2.imshow("webcam",imutils.rotate(img,270))
        
        
    def onMouse(self,event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            self.print_px_color = True
            self.x = x
            self.y = y
            #print("X(%d) Y(%d)"%(x,y))

    def run(self):
        while True:
            try:
                # Grab next image and display it
                self.updateFrame()
                #time.sleep(0.5)
                #x = input("Angle set >>> ")
                #self.pi.set_servo_pulsewidth(self.servo_pin, x)
            except KeyboardInterrupt:
                break

        self.pi.set_servo_pulsewidth(self.servo_pin, 0)
        # Turn laser off
        self.pi.write(self.laser_pin,1)
        # Stop pigpio
        self.pi.stop()
        cv2.destroyAllWindows()
        
if __name__=='__main__':
    la = laser_align()
    la.run()

    

