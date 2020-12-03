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
import random
from time import sleep as sleep

class LyingNao(Robot):
    def __init__(self):
        super(LyingNao, self).__init__()

        print('> Starting robot controller')

        # From the tutorial2_controller file
        # timeStep and state init
        self.timeStep = 32 # Milisecs to process the data (loop frequency) - Use int(self.getBasicTimeStep()) for default
        self.state = 0 # Idle starts for selecting different states

        # Sensors init
        self.gps = self.getGPS('gps')
        self.gps.enable(self.timeStep)

        self.step(self.timeStep) # Execute one step to get the initial position

        self.cameraTop = self.getCamera("CameraTop")
        self.cameraBottom = self.getCamera("CameraBottom")
        self.cameraTop.enable(4 * self.timeStep)
        self.cameraBottom.enable(4 * self.timeStep)

        self.currentlyPlaying = True

        # Initialize arm joints
        self.elbowyaw = self.getMotor('RElbowYaw')
        self.elbowroll= self.getMotor('RElbowRoll')
        self.shoulderpitch = self.getMotor('RShoulderPitch')
        self.shoulderpitch.getPositionSensor().enable(1)
        self.shoulderroll = self.getMotor('RShoulderRoll')
        self.shoulderroll.getPositionSensor().enable(1)
        self.headyaw = self.getMotor('HeadYaw')
        self.headpitch = self.getMotor('HeadPitch')


        self.actionList = ['Rock', 'Paper', 'Scissors']
        self.lieList = ['True', 'Lie', 'Nothing']
        self.hintList = ['Rock', 'Paper', 'Scissors', 'Nothing']

        # count = 0
        # while count<15:
        #     print('Iteration:', count,'\n')
        #     self.playPipeline()
        #     count+=1

        self.rollmin, self.rollmax = -1.3260, 0.3140
        self.pitchmin, self.pitchmax = -2.0850, 2.0850
        self.shoulderroll.setVelocity(1)
        self.shoulderpitch.setVelocity(1)

        self.basePosition()
        self.turn_head()

        self.straightenArm()
        # self.moveArmRight()
        # self.moveArmLeft()


    def turn_head(self):
        self.headyaw.setVelocity(1)
        self.headyaw.setPosition(-0.6)

    def basePosition(self):
        print('base position')
        self.shoulderroll.setPosition(0)
        self.shoulderpitch.setPosition(0.5*self.pitchmax)

    def moveArmRight(self):
        print('move arm right')
        self.shoulderroll.setPosition(0.5*self.rollmin)
        self.shoulderpitch.setPosition(0.7*self.pitchmax)
        # self

    def moveArmLeft(self):
        print('move arm left')
        self.shoulderroll.setPosition(self.rollmax)
        self.shoulderpitch.setPosition(0.3*self.pitchmax)


    def straightenArm(self):
        print("Straighten Arm")
        rolmin = 0.0345
        self.elbowroll.setPosition(rolmin)
        self.elbowroll.setVelocity(1)

    def playPipeline(self):
        truthOfHint = self.truthLieOrNothing()
        print('truthOfHint, ', truthOfHint)
        hint = self.giveHint(truthOfHint)
        print('hint, ', hint)
        naoChoice = self.chooseOption(truthOfHint, hint)
        print('Nao\'s Choice: ', naoChoice, '\n')

        playerChoice = self.playerChooses(hint)
        self.whoWon(naoChoice, playerChoice)

        print('\n------------------------------\n\n')

    def whoWon(self, naoChoice, playerChoice):
        if naoChoice == 'Paper' and playerChoice == 'Rock':
            print('Nao won!')
        if naoChoice == 'Rock' and playerChoice == 'Scissors':
            print('Nao won!')
        if naoChoice == 'Scissors' and playerChoice == 'Paper':
            print('Nao won!')
        if naoChoice == playerChoice:
            print('It\'s a tie!')
        if playerChoice == 'Paper' and naoChoice == 'Rock':
            print('Player won!')
        if playerChoice == 'Rock' and naoChoice == 'Scissors':
            print('Player won!')
        if playerChoice == 'Scissors' and naoChoice == 'Paper':
            print('Player won!')


    def playerChooses(self, hint):
        # Player chooses best move and always trusts the hint
        playerChoice = self.bestMove(hint)
        print('Player choice: ', playerChoice)
        return playerChoice


    def chooseOption(self, truthOfHint, hint):
        if truthOfHint == 'True':
            return hint
        if truthOfHint == 'Lie':
            return self.bestLieMove(hint)
        if truthOfHint == 'Nothing':
            return random.choice(self.actionList)

    def bestLieMove(self, lie):
        if lie == 'Rock':
            return 'Scissors'
        if lie == 'Paper':
            return 'Rock'
        if lie == 'Scissors':
            return 'Paper'

    def bestMove(self, playerChoice):
        if playerChoice == 'Rock':
            bestMove = 'Paper'
        if playerChoice == 'Paper':
            bestMove = 'Scissors'
        if playerChoice == 'Scissors':
            bestMove = 'Rock'
        if playerChoice == 'Nothing':
            bestMove = random.choice(self.actionList)
        return bestMove

    def giveHint(self, truthOfHint):
        if truthOfHint == 'Nothing':
            return 'Nothing'
        else:
            return random.choice(self.actionList)

    def truthLieOrNothing(self):
        return random.choice(self.lieList)


robot = LyingNao()
