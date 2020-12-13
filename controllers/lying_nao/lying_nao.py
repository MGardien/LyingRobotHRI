"""Rock, Paper, Scissors, the lying Nao"""

# Bram Pol - s4815521
# Max Gardien
# Britt van Gemert - s4555740
# Veronne Reinders - s4603478

from controller import Robot, Keyboard, Display, Motion, Motor, Camera, Speaker
import numpy as np
import cv2
from io import BytesIO
import threading
import random
import time
import pyttsx3
import sys
from gtts import gTTS
import os

class LyingRobot(Robot):
    def __init__(self, camera):
        super(LyingRobot, self).__init__()
        
        # From the tutorial2_controller file
        # timeStep and state init
        self.timeStep = 32 # Milisecs to process the data (loop frequency) - Use int(self.getBasicTimeStep()) for default
        self.state = 0 # Idle starts for selecting different states

        self.step(self.timeStep) # Execute one step to get the initial position

        self.cameraOP3 = self.getCamera("Camera")
        if camera:
            self.cameraOP3.enable(1)

        self.currentlyPlaying = True

        self.actionList = ['Rock', 'Paper', 'Scissors']
        self.lieList = ['True', 'Lie', 'Nothing']
        self.hintList = ['Rock', 'Paper', 'Scissors', 'Nothing']
        
        self.speakList = ['I am going to play ', 'I made my choice, this time I will play ', 'This time I will play ', 'I choose ', 'I decided to play ']
        
        self.engine = pyttsx3.init()
        
        # Keyboard
        self.keyboard.enable(self.timeStep)
        self.keyboard = self.getKeyboard()
        
        # Speaker
        self.engine = pyttsx3.init()
        self.audio_fn = "output.mp3"
        self.speaker = self.getSpeaker("Speaker")
        
        print('Hi! Do you want to play a game with me? (Y/N)')
        
        self.playerAnswer()

    def playPipeline(self):
        truthOfHint = self.truthLieOrNothing()
        #print('truthOfHint (hidden) ', truthOfHint)
        hint = self.giveHint(truthOfHint)
        if truthOfHint == "Lie" or truthOfHint == "True":
            self.audioNao(hint)
        print('Please make your choice:')
        playerChoice = self.playerInput()
        print('Your choice was: ', playerChoice)
        naoChoice = self.chooseOption(truthOfHint, hint)
        print('Nao\'s Choice: ', naoChoice, '\n')
#       playerChoice = self.playerChooses(hint)
        self.whoWon(naoChoice, playerChoice)
        self.currentlyPlaying = True

        print('\n------------------------------\n\n')

    def whoWon(self, naoChoice, playerChoice):
        if naoChoice == 'Paper' and playerChoice == 'Rock':
            print('I won!')
        if naoChoice == 'Rock' and playerChoice == 'Scissors':
            print('I won!')
        if naoChoice == 'Scissors' and playerChoice == 'Paper':
            print('I won!')
        if naoChoice == playerChoice:
            print('It\'s a tie!')
        if playerChoice == 'Paper' and naoChoice == 'Rock':
            print('You won!')
        if playerChoice == 'Rock' and naoChoice == 'Scissors':
            print('You won!')
        if playerChoice == 'Scissors' and naoChoice == 'Paper':
            print('You won!')

    def playerAnswer(self):
        while self.step(self.timeStep) != -1 and self.currentlyPlaying:
            key = self.keyboard.getKey()
            if(key == 89 or key == 65625):
                print('Great, let\'s start!')
                break;
            elif(key == 78 or key == 65614):
                print('Bye!')
                #saveExperimentData()
                sys.exit(0)
                
    def playerInput(self):
        playerChoice = random.choice(self.actionList)
        
        while self.step(self.timeStep) != -1 and self.currentlyPlaying:
            keypress = self.keyboard.getKey()
            # #ASCII character numbers of 'r'/'R','p'/'P' and 's'/'S'
            # #(using arrows all returned value 0)    
            if keypress == 82:# or keypress == 114:
                #image = cv2.imread(r'..\..\img\rock.png')
                #cv2.imshow('Your choice', image)
                #cv2.waitKey(5)
                playerChoice = self.actionList[0]
                self.currentlyPlaying = False
                break
            elif keypress == 80:# or keypress == 112:
                #image = cv2.imread(r'..\..\img\paper.png')
                #cv2.imshow('Your choice', image)
                #cv2.waitKey(5)
                playerChoice = self.actionList[1]
                self.currentlyPlaying = False
                break
            elif keypress == 83:# or keypress == 115:
                #image = cv2.imread(r'..\..\img\scissors.png')
                #cv2.imshow('Your choice', image)
                #cv2.waitKey(5)
                playerChoice = self.actionList[2]
                self.currentlyPlaying = False
                break
                
        return playerChoice
            
    # def playerChooses(self, hint):
    #    Player chooses best move and always trusts the hint
        # playerChoice = self.bestMove(hint)
        # print('Player choice: ', playerChoice)
        # return playerChoice


    def chooseOption(self, truthOfHint, hint):
        if truthOfHint == 'Truth':
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
       
    def audioNao(self, value):
        if value == "Paper":
            self.speaker.speak("%s paper" % random.choice(self.speakList), 1)
        elif value == "Rock":
            self.speaker.speak("%s rock" % random.choice(self.speakList), 1)
        else:
            self.speaker.speak("%s scissors" % random.choice(self.speakList), 1)
    
robot = LyingRobot(camera = False)
count = 0
while count<15:
    print('Iteration:', count,'\n')
    robot.playPipeline()
    count+=1

print('finished')

