#!/usr/bin/env python

# Camera settings
# Set with 'v4l2-ctl -d /dev/video0 -c <param_name>=<value>
# brightness = 1
# contrast   = 32
# saturation = 100
# gain       = 64
# exposure   = 166
# resolution = 1280x960

import sys
import time
import random
import pigpio
import cv2
import imutils
import numpy as np
import matplotlib as mpl
#mpl.use('Agg')
import matplotlib.pyplot as plt
class triangulation:
    
    def __init__(self):
        plt.ion()
	self.fig = plt.figure()
	plt.axis([-9,-20,-5,5])
	# Define system properties
        self.servo_pin = 18
        self.laser_pin = 16
        self.min_width = 550
        self.max_width = 2330
        self.perp_pulse = 1863
        self.baseline = 81.6
        self.focalx = 1366.921175795496
	self.focaly = 1368.015379553626
        self.ang2pulse = (self.max_width-self.min_width)/180.0
        self.pulse2ang = 1.0/self.ang2pulse
        self.low_ang = 1400
        self.hi_ang = 2100

	# Calibration parameters
        self.px = 623.9050374734363
        self.py = 503.4952444364909
        self.u1 = 351.0 - self.px
        self.u2 = 216.0 - self.px
        self.x1 = 17.0
        self.x2 = 11.0

	self.update_extrinsics() 

        # Control variables for rotary motion
        self.step = 2.0*self.ang2pulse
        self.width = self.perp_pulse# - 197.777777778

        # Initialize the gpio class
        self.pi = pigpio.pi()
        if not self.pi.connected:
            exit()

        # Turn laser on
        self.pi.write(self.laser_pin,0)

        # Set laser to first position
        self.pi.set_servo_pulsewidth(self.servo_pin, self.width)
        time.sleep(2)

        # Create video capture object
        self.cam = cv2.VideoCapture(0)
        # Set video resolution
        self.cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH,1280)
        self.cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT,960)

        # Video settings
        # v4l2-ctl -d /dev/video0 -c gain=10
        # v4l2-ctl -d /dev/video0 -c brightness=30
        # v4l2-ctl -d /dev/video0 -c contrast=60
        # v4l2-ctl -d /dev/video0 -c saturation=255
        # v4l2-ctl -d /dev/video0 -c exposure_auto=1
        # v4l2-ctl -d /dev/video0 -c exposure_absolute=200
        # Set video brightness
        self.cam.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS,0.12)
        # Set video contrast
        self.cam.set(cv2.cv.CV_CAP_PROP_CONTRAST,0.235)
        # Set video saturation
        self.cam.set(cv2.cv.CV_CAP_PROP_SATURATION,1)
        # Set video gain
        self.cam.set(cv2.cv.CV_CAP_PROP_GAIN,0.04)
        self.cam.set(cv2.cv.CV_CAP_PROP_FPS,30)

        # Create window to display image in
        #cv2.startWindowThread()
        #cv2.namedWindow("webcam")
        #cv2.setMouseCallback("webcam",self.onMouse)
        self.print_px_color = False

    def updateFrame(self):            
        ret_val, img = self.cam.read()
        
        #lb = np.array([0,0,200])
        #hb = np.array([150,150,255])
        #redline = cv2.inRange(img,lb,hb)
        maxCol = np.amax(img[:,:,2],axis=0)
        maxInd = np.argmax(img[:,:,2],axis=0)

        ind = []
        for idx, val in enumerate(maxCol):
            if val > 150:
                ind.append([float(idx),float(maxInd[idx])])
	#test	
	#ind[1:260] = [326.0]*(260-1)
	#ind[261:769] = [211.5]*(769-261)
	#ind[770:960] = [228.0]*(960-770)

        self.plotPoints(ind)
        #red = img[:,:,2] > 100
        #img[red] = [0,255,0]
        #cv2.imshow("webcam",imutils.rotate(img,270))
        if self.print_px_color == True:
            print("X(%d) Y(%d) RGB(%d,%d,%d)"%(self.x,self.y,img[self.y,self.x,0],img[self.y,self.x,1],img[self.y,self.x,2]))
            self.print_px_color = False

    def onMouse(self,event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            self.print_px_color = True
            self.x = x
            self.y = y
            #print("X(%d) Y(%d)"%(x,y))

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

    def plotPoints(self,ind):     
        x = []
        y = []
        for idx,i in enumerate(ind):
            xtemp = self.N/((i[1]-self.py)*self.d-self.k)
            ytemp = (i[0]-self.px)/(self.focalx)*xtemp

            if np.abs(xtemp) < 50 and np.abs(ytemp) < 50:
                x.append(xtemp)
                y.append(ytemp)
	#print(x)
	#print(y)
	plt.cla()
        plt.scatter(x,y,marker=".",color='r')
	plt.axis('equal')
	#plt.axis([-9,-15,-5,5])
	plt.xlabel('X(in)')
	plt.ylabel('Y(in)')
	plt.show()
	plt.pause(0.05)

    def update_extrinsics(self):
	self.d = self.x2-self.x1
        self.k = self.u2*self.x2 - self.u1*self.x1
        self.N = (self.u1-self.u2)*self.x1*self.x2

    def run(self):
        while True:
            try:
                #self.incrementLaser()
                # Delay for next frame
                time.sleep(0.1)
                # Grab next image and display it
                self.updateFrame()
                # Move laser to next position
                
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

    

