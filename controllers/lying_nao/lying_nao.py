"""Rock, Paper, Scissors, the lying Nao"""

# Bram Pol - s4815521
# Max Gardien
# Britt van Gemert - s4555740
# Veronne Reinders - s4603478

from controller import Robot, Keyboard, Display, Motion, Motor, Camera
import numpy as np
import cv2
from io import BytesIO
import threading
# import ALProxy


class LyingNao(Robot):
    def __init__(self):
        super(LyingNao, self).__init__()

        print('> Starting robot controller')
        # self.motion = ALProxy("ALMotion")

        self.timeStep = 32 # Milisecs to process the data (loop frequency) - Use int(self.getBasicTimeStep()) for default

        self.state = 0 # Idle starts for selecting different states

        # Sensors init
        self.gps = self.getGPS('gps')
        self.gps.enable(self.timeStep)

        self.step(self.timeStep) # Execute one step to get the initial position

        # self.displayCamExt = self.getDisplay('CameraExt')


        self.cameraTop = self.getCamera("CameraTop")
        self.cameraBottom = self.getCamera("CameraBottom")
        self.cameraTop.enable(4 * self.timeStep)
        self.cameraBottom.enable(4 * self.timeStep)

        self.currentlyPlaying = False


        # self.initialize_hand()
        print('setting setStiffnesses')
        self.hand = self.getMotor('RHand')
        # self.motion.setStiffnesses("HeadYaw", 1)
        #
        # self.motion.setAngles("HeadYaw", -0.5, 0.05)
        #
        # self.motion.setStiffnesses("HeadYaw", 0)


        # self.hand.Open()
        # open = True
        # self.move_hand(open)

    def move_hand(self, open):
        if open:
            # self.hand.setVelocity(0.5)
            self.hand.Open()
            print('opened hand')
        if not open:
            # self.hand.setVelocity(0.5)
            self.hand.Close()
            print('closed hand')

    def initialize_hand(self):
        print('reached initialize_hand')
        self.hand = self.getMotor('RHand')
        # self.RHand.getPositionSensor().enable(1)
        print('rhand initialized')
        # sleep()

robot = LyingNao()
