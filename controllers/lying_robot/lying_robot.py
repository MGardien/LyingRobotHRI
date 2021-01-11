"""Rock, Paper, Scissors, the lying robot"""

# Bram Pol - s4815521
# Max Gardien - s4707931
# Britt van Gemert - s4555740
# Veronne Reinders - s4603478

from controller import Robot, Keyboard, Display, Motion, Motor, Speaker, ImageRef, LED
import numpy as np
import itertools

import pandas as pd
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
    def __init__(self):
        super(LyingRobot, self).__init__()

        self.timeStep = 32 # Milisecs to process the data (loop frequency) - Use int(self.getBasicTimeStep()) for default
        self.state = 0 # Idle starts for selecting different states

        self.step(self.timeStep) # Execute one step to get the initial position

        self.currentlyPlaying = True

        self.experimenter = 'pl'     # Edit your experimenter-signature here (mg/vr/bp/bvg)
        self.participant = '0'      # Edit the participant-number here

        self.playerPoints = 0   # Initialise player score
        self.robotPoints = 0    # Initialise robot score
 
        self.all_hints = []             # List to save all hints during the experiment
        self.all_player_moves = []      # List to save all player-moves during the experiment
        self.all_robot_moves = []       # List to save all robot-moves during the experiment
        self.all_outcomes = []          # List to save all outcomes during the experiment

        self.all_states = []            # List to look back at previous states during the experiment

        self.actionList = ['Rock', 'Paper', 'Scissors']             # Define possible actions for both robot and player
        self.lieList = ['True', 'Lie', 'Nothing']                   # Define possible strategies for the robot to influence the player
        self.hintList = ['Rock', 'Paper', 'Scissors', 'Nothing']    # Define possible hints that the robot might give
        self.choiceLock = False                                     # Create lock to prevent multiple keyboard hits

        self.onegame = [self.actionList, self.actionList, self.lieList]
        self.firstgame = list(itertools.product(*self.onegame))
        self.bothgames = [self.firstgame, self.firstgame]

        self.statespace = list(itertools.product(*self.bothgames))
        self.actionspace = list(itertools.product(*[self.lieList, self.actionList]))

        # Load the trained q-matrix
        file2 = open("qmatrix", "rb")
        self.qmatrix = np.load(file2)

        # Initialise arms and head
        self.unusedArm = self.getMotor('ArmUpperL')
        self.unusedArm.setPosition(1.5)
        self.shoulder = self.getMotor('ShoulderR')
        self.armupper = self.getMotor('ArmUpperR')
        self.armdown = self.getMotor('ArmLowerR')       
        self.shoulder.setVelocity(1)
        self.armupper.setVelocity(1)
        self.armdown.setVelocity(1)
        self.head = self.getMotor('Head')
        self.neck = self.getMotor('Neck')
        self.neck.setVelocity(1)
        self.head.setPosition(-0.4)
        
        # Define phrases for win, tie, lose and start
        self.winSpeak = ['I won', 'Yes, I won', 'I won, better luck next time']
        self.tieSpeak = ['Great minds think alike, its a tie', 'Its a tie', 'No one won, its a tie']
        self.lostSpeak = ['Well played, you won', 'Unfortunately for me, you won', 'You won']       

        self.speakList = ['I am going to play ', 'I made my choice, this time I will play ', 'This time I will play ', 'I choose ', 'I decided to play ']

        # Keyboard init
        self.keyboard.enable(self.timeStep)
        self.keyboard = self.getKeyboard()
        
        # LEDs init
        self.headLED = self.getLED("HeadLed")
        self.headLED.set(1)       
        self.bodyLED = self.getLED("BodyLed")
        self.bodyLED.set(1)

        # Speaker init
        self.speaker = self.getSpeaker("Speaker")
        self.speaker.getEngine()

        # Choice-motors init
        self.push_r = self.getMotor("push_rock")
        self.push_r.setPosition(float(2.47))
        self.push_p = self.getMotor("push_paper")
        self.push_p.setPosition(float(2.47))
        self.push_s = self.getMotor("push_scissors")
        self.push_s.setPosition(float(2.47))

        # Initial behaviour
        self.speaker.speak('Hi! Do you want to play, rock paper scissors, with me?', 1)
        print('Hi! Do you want to play rock paper scissors with me? (Y/N)')    
        self.moveLeftAndWave()
        while self.speaker.isSpeaking():
            self.step(1)
        self.moveLeft()
        self.playerAnswer()

    # Starting movement
    def moveLeftAndWave(self):
        self.head.setPosition(-0.5)
        self.neck.setPosition(-1)

        self.armupper.setPosition(1)
        
    # Pointing to the middle object
    def moveMiddle(self):
        self.head.setPosition(-0.5)
        self.neck.setPosition(-1)

        self.armdown.setPosition(0.5)
        self.shoulder.setPosition(1)
        self.armupper.setPosition(-0.5)

    # Pointing to the left object
    def moveLeft(self):
        self.head.setPosition(-0.5)
        self.neck.setPosition(-1.5)

        self.armdown.setPosition(0)
        self.shoulder.setPosition(0)
        self.armupper.setPosition(-0.5)

    # Pointing to the right object
    def moveRight(self):
        self.head.setPosition(-0.5)
        self.neck.setPosition(-0.5)

        self.armdown.setPosition(0)
        self.shoulder.setPosition(1)
        self.armupper.setPosition(-1.6)

    # Pointing to the image of Rock, Paper or Scissors
    def expressChoice(self,robotChoice):
        if robotChoice == 'Rock':
            self.moveLeft()
        elif robotChoice == 'Paper':
            self.moveMiddle()
        elif robotChoice == 'Scissors':
            self.moveRight()

    # Save data of experiment to excel file
    def saveExperimentData(self):
        df = pd.DataFrame({'hints':robot.all_hints,'player':robot.all_player_moves,'robot':robot.all_robot_moves,'outcome':robot.all_outcomes})
        df.to_excel('../../data/'+robot.experimenter+robot.participant+'.xlsx')

    # Determines the action when the robot is lying
    def hint_and_lie_to_action(self, hint):
        if hint == 'Rock':
            action = 'Scissors'
        if hint == 'Paper':
            action = 'Rock'
        if hint == 'Scissors':
            action = 'Paper'
        return action

    # Pick indication and action from q-matrix
    def getIndicationAndActionFromState(self, state):
        indication = self.actionspace[np.argmax(self.qmatrix[self.statespace.index(state)])][0]
        action = self.actionspace[np.argmax(self.qmatrix[self.statespace.index(state)])][1]
        return indication, action

    # Update q-matrix
    def learningStep(self, state, newstate, reward):
        alpha = 0.6
        gamma = 0.4
        epsilon = 0.1

        state_space_index = self.statespace.index(state)
        action_space_index = np.argmax(self.qmatrix[state_space_index])

        old_value = self.qmatrix[state_space_index, action_space_index]

        newindex = self.statespace.index(newstate)
        newmax = np.max(self.qmatrix[newindex])

        new_value = (1 - alpha) * old_value + alpha * (reward + gamma * newmax)

        self.qmatrix[state_space_index, action_space_index] = new_value

        print('Changed old val: ', old_value, ' to new val: ', new_value)
        self.saveToFile()

    # Opens and saves the updated q-matrix
    def saveToFile(self):
        file = open("qmatrix", "wb")
        np.save(file, self.qmatrix)
        file.close
        print('File saved')

    # Executes a game
    def playPipeline(self):
        if len(self.all_states)>0:
            state = self.all_states[-1]
        else:
            randomnumber = random.randint(0,len(self.statespace)-1)
            state = self.statespace[randomnumber]

        truthOfHint, robotChoice = self.getIndicationAndActionFromState(state)

        if truthOfHint == 'Lie':
            hint = self.hint_and_lie_to_action(robotChoice)
        if truthOfHint == 'True':
            hint = robotChoice
        if truthOfHint == 'Nothing':
            hint = 'Nothing'

        self.all_hints.append(truthOfHint)
        if truthOfHint == "Lie" or truthOfHint == "True":
            self.audioRobot(hint)
            while self.speaker.isSpeaking():
                self.step(1)
        self.speaker.speak('Please make your choice', 1)
        while self.speaker.isSpeaking():
            self.step(1)        
        print('Please make your choice: (R/P/S)')
        playerChoice = self.playerInput()
        self.all_player_moves.append(playerChoice)
        self.speaker.speak('Your choice was %s' % playerChoice, 1)
        while self.speaker.isSpeaking():
            self.step(1)    
        print('Your choice was: ', playerChoice)

        currentgame = (playerChoice, robotChoice, truthOfHint)
        newstate = (currentgame, state[0])
        self.all_states.append(newstate)

        self.all_robot_moves.append(robotChoice)
        self.expressChoice(robotChoice)
        self.speaker.speak('I chose %s' % robotChoice, 1)
        while self.speaker.isSpeaking():
            self.step(1)    
        print('Robot\'s Choice: ', robotChoice, '\n')
        self.whoWon(robotChoice, playerChoice)
        self.currentlyPlaying = True
        #reward = self.rewardfunc(playerChoice, robotChoice)
        #self.learningStep(state, newstate, reward)

        print('\n------------------------------\n\n')

    # Checks who won the game and rewards points
    def whoWon(self, robotChoice, playerChoice):
        if robotChoice == 'Paper' and playerChoice == 'Rock':
            self.speaker.speak(random.choice(self.winSpeak), 1)
            while self.speaker.isSpeaking():
                self.step(1)    
            print('I won!')
            self.all_outcomes.append('Robot won')
            self.robotPoints += 3
        elif robotChoice == 'Rock' and playerChoice == 'Scissors':
            self.speaker.speak(random.choice(self.winSpeak), 1)
            while self.speaker.isSpeaking():
                self.step(1)  
            print('I won!')
            self.all_outcomes.append('Robot won')
            self.robotPoints += 3
        elif robotChoice == 'Scissors' and playerChoice == 'Paper':
            self.speaker.speak(random.choice(self.winSpeak), 1)
            while self.speaker.isSpeaking():
                self.step(1)  
            print('I won!')
            self.all_outcomes.append('Robot won')
            self.robotPoints += 3
        elif robotChoice == playerChoice:
            self.speaker.speak(random.choice(self.tieSpeak), 1)
            while self.speaker.isSpeaking():
                self.step(1)  
            print('It\'s a tie!')
            self.all_outcomes.append('Tie')
            self.robotPoints += 1
            self.playerPoints += 1
        elif playerChoice == 'Paper' and robotChoice == 'Rock':
            self.speaker.speak(random.choice(self.lostSpeak), 1)
            while self.speaker.isSpeaking():
                self.step(1)  
            print('You won!')
            self.all_outcomes.append('Player wins')
            self.playerPoints += 3
        elif playerChoice == 'Rock' and robotChoice == 'Scissors':
            self.speaker.speak(random.choice(self.lostSpeak), 1)
            while self.speaker.isSpeaking():
                self.step(1)          
            print('You won!')
            self.all_outcomes.append('Player wins')
            self.playerPoints += 3
        elif playerChoice == 'Scissors' and robotChoice == 'Paper':
            self.speaker.speak(random.choice(self.lostSpeak), 1)
            while self.speaker.isSpeaking():
                self.step(1)          
            print('You won!')
            self.all_outcomes.append('Player wins')
            self.playerPoints += 3
        else:
            self.all_outcomes.append('No winner')

    # Keyboard-input for continuing
    def playerAnswer(self):
        while self.step(self.timeStep) != -1 and self.currentlyPlaying:
            key = self.keyboard.getKey()
            if(key == ord('Y')):
                self.speaker.speak('Great, lets start!', 1)
                while self.speaker.isSpeaking():
                    self.step(1)
                break
            elif(key == ord('N')):
                self.speaker.speak('Okay, bye', 1)
                while self.speaker.isSpeaking():
                    self.step(1)                
                self.saveExperimentData()
                sys.exit(0)

    # Keyboard-input for Rock, Paper or Scissors
    def playerInput(self):
        playerChoice = random.choice(self.actionList)
        while self.step(self.timeStep) != -1 and self.currentlyPlaying:
            key = self.keyboard.getKey()
            if not self.choiceLock:
                if key == ord('R'):
                    self.push_r.setPosition(float(2.485))
                    playerChoice = self.actionList[0]
                    self.choiceLock = True
                    self.currentlyPlaying = False
                    break
                elif key == ord('P'):
                    self.push_p.setPosition(float(2.48))
                    playerChoice = self.actionList[1]
                    self.choiceLock = True
                    self.currentlyPlaying = False
                    break
                elif key == ord('S'):
                    self.push_s.setPosition(float(2.48))
                    playerChoice = self.actionList[2]
                    self.choiceLock = True
                    self.currentlyPlaying = False
                    break
        return playerChoice

    # Execute speech
    def audioRobot(self, value):
        if value == "Paper":
            self.speaker.speak("%s paper" % random.choice(self.speakList), 1)
        elif value == "Rock":
            self.speaker.speak("%s rock" % random.choice(self.speakList), 1)
        else:
            self.speaker.speak("%s scissors" % random.choice(self.speakList), 1)

    # Reward function, 0 for tie, -1 for loss, 1 for win, might want to tune later
    def rewardfunc(self, playermove, robotmove):
        if playermove == 'Rock' and robotmove == 'Rock':
            return 0
        if playermove == 'Paper' and robotmove == 'Paper':
            return 0
        if playermove == 'Scissors' and robotmove == 'Scissors':
            return 0

        if playermove == 'Rock' and robotmove == 'Paper':
            return 1
        if playermove == 'Rock' and robotmove == 'Scissors':
            return -1

        if playermove == 'Paper' and robotmove == 'Scissors':
            return 1
        if playermove == 'Paper' and robotmove == 'Rock':
            return -1

        if playermove == 'Scissors' and robotmove == 'Rock':
            return 1
        if playermove == 'Scissors' and robotmove == 'Paper':
            return -1

robot = LyingRobot()        # Initialise the robot
nr_of_iterations = 20       # Define the number of games for each experiment or training session
count = 0
while count < nr_of_iterations:
    print('Iteration:', count,'/ '+str(nr_of_iterations)+'\n')
    if count > 0:
        robot.speaker.speak('Are you ready for the next game?', 1)
        while robot.speaker.isSpeaking():
            robot.step(1)
        print('Ready for the next game? (Y/N)')
        robot.playerAnswer()
    robot.playPipeline()
    robot.push_r.setPosition(float(2.47))
    robot.push_p.setPosition(float(2.47))
    robot.push_s.setPosition(float(2.47))
    robot.choiceLock = False
    count+=1
robot.saveExperimentData()
robot.speaker.speak('The end score is... %s points for me vs. %s points for you, which means...' % (robot.robotPoints, robot.playerPoints), 1)
print('[Endscore] Robot: '+str(robot.robotPoints)+' VS Player: '+str(robot.playerPoints))
while robot.speaker.isSpeaking():
    robot.step(1)
if robot.robotPoints > robot.playerPoints:
    robot.speaker.speak('I did beat you, better luck next time', 1)
    while robot.speaker.isSpeaking():
        robot.step(1)
elif robot.robotPoints < robot.playerPoints:
    robot.speaker.speak('Somehow you managed to beat me, well done', 1)
    while robot.speaker.isSpeaking():
        robot.step(1)
else:
    robot.speaker.speak('Looks like we both did equally good', 1)
    while robot.speaker.isSpeaking():
        robot.step(1)
robot.speaker.speak('Thank you for playing rock paper scissors with me! Bye!', 1)