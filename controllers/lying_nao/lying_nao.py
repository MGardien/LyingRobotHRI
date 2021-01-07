"""Rock, Paper, Scissors, the lying robot"""

# Bram Pol - s4815521
# Max Gardien - s4707931
# Britt van Gemert - s4555740
# Veronne Reinders - s4603478

from controller import Robot, Keyboard, Display, Motion, Motor, Camera, Speaker, ImageRef
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

        # Initialize arm joints
        # self.elbowyaw = self.getMotor('RElbowYaw')
        # self.elbowroll= self.getMotor('RElbowRoll')
        # self.shoulderpitch = self.getMotor('RShoulderPitch')
        #
        #
        # self.shoulderpitch.getPositionSensor().enable(1)
        # self.shoulderroll = self.getMotor('RShoulderRoll')
        # self.shoulderroll.getPositionSensor().enable(1)


        # self.headyaw = self.getMotor('HeadYaw')
        # self.headpitch = self.getMotor('HeadPitch')

        # self.rollmin, self.rollmax = -1.3260, 0.3140
        # self.pitchmin, self.pitchmax = -2.0850, 2.0850
        # self.shoulderroll.setVelocity(1)
        # self.shoulderpitch.setVelocity(1)

        # count = 0
        # while count<15:
        #     print('Iteration:', count,'\n')
        #     self.playPipeline()
        #     count+=1

        self.experimenter = 'mg_train'     #Edit your experimenter-signature here (mg/vr/bp/bvg)   !!!
        self.participant = '5'         #Edit the participant here  !!!

        self.all_hints = []
        self.all_player_moves = []
        self.all_robot_moves = []
        self.all_outcomes = []
        self.all_states = []

        self.actionList = ['Rock', 'Paper', 'Scissors']
        self.lieList = ['True', 'Lie', 'Nothing']
        self.hintList = ['Rock', 'Paper', 'Scissors', 'Nothing']
        self.choiceLock = False
        
        self.onegame = [self.actionList, self.actionList, self.lieList]
        self.firstgame = list(itertools.product(*self.onegame))
        self.bothgames = [self.firstgame, self.firstgame]

        self.statespace = list(itertools.product(*self.bothgames))
        self.actionspace = list(itertools.product(*[self.lieList, self.actionList]))
        
        file2 = open("qmatrix", "rb")
        self.qmatrix = np.load(file2)

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
        # self.neck.setPosition(-1)

        # self.moveMiddle()
        self.moveLeft()
        # self.moveRight()
        # self.moveBase()

        # self.moveBase()
        # sleep(10)
        # print('sleep is done')
        # self.moveLeft()
        # self.moveRight()

        self.speakList = ['I am going to play ', 'I made my choice, this time I will play ', 'This time I will play ', 'I choose ', 'I decided to play ']
        
        self.engine = pyttsx3.init()
        
        # Keyboard
        self.keyboard.enable(self.timeStep)
        self.keyboard = self.getKeyboard()
        
        # Speaker
        self.engine = pyttsx3.init()
        # self.engine = pyttsx3.init('sapi5')
        self.audio_fn = "output.mp3"
        self.speaker = self.getSpeaker("Speaker")
        self.speaker.getEngine()
        
        # Motors
        self.push_r = self.getMotor("push_rock")
        self.push_r.setPosition(float(2.47))
        self.push_p = self.getMotor("push_paper")
        self.push_p.setPosition(float(2.47))
        self.push_s = self.getMotor("push_scissors")
        self.push_s.setPosition(float(2.47))
        
        print('Hi! Do you want to play a game with me? (Y/N)')
        self.speaker.speak('Hi! Do you want to play a game with me?', 1)
        
        self.moveLeft()
        
        
        self.playerAnswer()

    def moveLeftAndWave(self):
        self.head.setPosition(-0.5)
        self.neck.setPosition(-1)
        
        self.armupper.setPosition(1) 
        #self.armupper.setPosition(-0.5)   

        #self.armdown.setPosition(0)
        #self.shoulder.setPosition(0)
        #self.armupper.setPosition(-0.5)

    def moveMiddle(self):
        self.head.setPosition(-0.5)
        self.neck.setPosition(-1)

        self.armdown.setPosition(0.5)
        self.shoulder.setPosition(1)
        self.armupper.setPosition(-0.5)

    def moveBase(self):
        self.head.setPosition(-0.1)
        self.neck.setPosition(-1)

        self.armdown.setPosition(0)
        self.shoulder.setPosition(0)
        self.armupper.setPosition(-1.5)

    def moveLeft(self):
        self.head.setPosition(-0.5)
        self.neck.setPosition(-1.5)

        self.armdown.setPosition(0)
        self.shoulder.setPosition(0)
        self.armupper.setPosition(-0.5)

    def moveRight(self):
        self.head.setPosition(-0.5)
        self.neck.setPosition(-0.5)

        self.armdown.setPosition(0)
        self.shoulder.setPosition(1)
        self.armupper.setPosition(-1.6)
        
    def expressChoice(self,robotChoice):
        if robotChoice == 'Rock':
            self.moveLeft()
        elif robotChoice == 'Paper':
            self.moveMiddle()
        elif robotChoice == 'Scissors':
            self.moveRight()
       
    def saveExperimentData(self):
        df = pd.DataFrame({'hints':robot.all_hints,'player':robot.all_player_moves,'robot':robot.all_robot_moves,'outcome':robot.all_outcomes})
        df.to_excel('../../data/'+robot.experimenter+robot.participant+'.xlsx') 

    def hint_and_lie_to_action(self, hint):
        if hint == 'Rock':
            action = 'Scissors'
        if hint == 'Paper':
            action = 'Rock'
        if hint == 'Scissors':
            action = 'Paper'
        return action
    
    def getIndicationAndActionFromState(self, state):
        # print(self.statespace.index(state))
        indication = self.actionspace[np.argmax(self.qmatrix[self.statespace.index(state)])][0]
        action = self.actionspace[np.argmax(self.qmatrix[self.statespace.index(state)])][1]
        return indication, action

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
        
        
    def saveToFile(self):
        file = open("qmatrix", "wb")
        np.save(file, self.qmatrix)
        file.close
        print('File saved')
        
        
        
        

    def playPipeline(self):
        # truthOfHint = self.truthLieOrNothing()
        if len(self.all_states)>0:
            state = self.all_states[-1]
            # print('actually loaded last state')
        else:
            randomnumber = random.randint(0,len(self.statespace)-1)
            state = self.statespace[randomnumber]
            # print('randomly sampled state: ', randomnumber)
            
        truthOfHint, robotChoice = self.getIndicationAndActionFromState(state)
        
        # print(self.all_states)
        if truthOfHint == 'Lie':
            hint = self.hint_and_lie_to_action(robotChoice)
        if truthOfHint == 'True':
            hint = robotChoice
        if truthOfHint == 'Nothing':
            hint = 'Nothing'
            
            
        self.all_hints.append(truthOfHint)
        #print('truthOfHint (hidden) ', truthOfHint)
        # hint = self.giveHint(truthOfHint)
        if truthOfHint == "Lie" or truthOfHint == "True":
            self.audioRobot(hint)
        print('Please make your choice: (R/P/S)')
        playerChoice = self.playerInput()
        self.all_player_moves.append(playerChoice)
        print('Your choice was: ', playerChoice)
        # robotChoice = self.chooseOption(truthOfHint, hint)
        
        currentgame = (playerChoice, robotChoice, truthOfHint)
        newstate = (currentgame, state[0])
        self.all_states.append(newstate)

        self.all_robot_moves.append(robotChoice)
        self.expressChoice(robotChoice)
        print('Robot\'s Choice: ', robotChoice, '\n')
#       playerChoice = self.playerChooses(hint)
        self.whoWon(robotChoice, playerChoice)
        self.currentlyPlaying = True
        reward = self.rewardfunc(playerChoice, robotChoice)
        self.learningStep(state, newstate, reward)
        


        print('\n------------------------------\n\n')

    def whoWon(self, robotChoice, playerChoice):
        print(self.speaker.isSpeaking())
        if robotChoice == 'Paper' and playerChoice == 'Rock':
            self.speaker.speak('I won what a fun', 1)
            print('I won!')
            self.all_outcomes.append('Robot won')
        elif robotChoice == 'Rock' and playerChoice == 'Scissors':
            self.speaker.speak('I won', 1)
            print('I won!')
            self.all_outcomes.append('Robot won')
        elif robotChoice == 'Scissors' and playerChoice == 'Paper':
            self.speaker.speak('I won', 1)        
            print('I won!')
            self.all_outcomes.append('Robot won')
        elif robotChoice == playerChoice:
            print('It\'s a tie!')
            self.all_outcomes.append('Tie')
        elif playerChoice == 'Paper' and robotChoice == 'Rock':
            print('You won!')
            self.all_outcomes.append('Player wins')
        elif playerChoice == 'Rock' and robotChoice == 'Scissors':
            print('You won!')
            self.all_outcomes.append('Player wins')
        elif playerChoice == 'Scissors' and robotChoice == 'Paper':
            print('You won!')
            self.all_outcomes.append('Player wins')
        else:
            self.all_outcomes.append('No winner')

    def playerChooses(self, hint):
        # Player chooses best move and always trusts the hint
        playerChoice = self.bestMove(hint)
        print('Player choice: ', playerChoice)

    def playerAnswer(self):
        while self.step(self.timeStep) != -1 and self.currentlyPlaying:
            key = self.keyboard.getKey()
            if(key == ord('Y')):
                self.speaker.speak('Great, lets start!', 1)
                print('Great, let\'s start!')
                break
            elif(key == ord('N')):
                self.speaker.speak('Okay, bye', 1)
                print('Bye!')
                self.saveExperimentData()
                sys.exit(0)
                
    def playerInput(self):
        playerChoice = random.choice(self.actionList)
        
        while self.step(self.timeStep) != -1 and self.currentlyPlaying:
            key = self.keyboard.getKey()
            if not self.choiceLock: 
                if key == ord('R'):
                    self.push_r.setPosition(float(2.485))
                    #print('You choose Rock')
                    playerChoice = self.actionList[0]
                    self.choiceLock = True
                    self.currentlyPlaying = False
                    break
                elif key == ord('P'):  
                    self.push_p.setPosition(float(2.48))
                    #print('You choose Paper')         
                    playerChoice = self.actionList[1]
                    self.choiceLock = True
                    self.currentlyPlaying = False
                    break
                elif key == ord('S'):  
                    self.push_s.setPosition(float(2.48))
                    #print('You choose Scissors')       
                    playerChoice = self.actionList[2]
                    self.choiceLock = True
                    self.currentlyPlaying = False
                    break
        return playerChoice
            
    # def playerChooses(self, hint):
    #    Player chooses best move and always trusts the hint
        # playerChoice = self.bestMove(hint)
        # print('Player choice: ', playerChoice)
        # return playerChoice


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
        
    # Return the move that would have been the winning move considering the previous robot's choice
    def repeatPreviousWin(self, previousChoice):
        if previousChoice == 'Rock':
            bestMove = 'Paper'
        if previousChoice == 'Paper':
            bestMove = 'Scissors'
        if previousChoice == 'Scissors':
            bestMove = 'Rock'
        if previousChoice == 'Nothing':
            bestMove = random.choice(self.actionList)
        return bestMove
    
    
    # Decide how the simulated player will choose an action based on the current state
    def player_algorithm(self, state):
        epsilon = 0.3
        if random.uniform(0, 1) < epsilon:    
            playermove = self.actionList[random.randint(0,len(self.actionList)-1)]
        else:
            if random.uniform(0, 1) < 0.7:
                playermove = state[0][0]
            else:
                playermove = state[1][0]

        return playermove
    
    # def nextstatefunc(state, action):
    #     playermove = player_algorithm(state)
    #     robotmove = extract_action(action)
    #     hint = extract_hint(action)
        
    #     reward = rewardfunc(playermove, robotmove)
        
    #     # First game in state tuple is most recent
    #     # Therefore first index old state becomes second index new state
    #     # And the current game becomes the first index of new state
    #     currentgame = (playermove, robotmove, hint)
    #     nextstate = (currentgame ,state[0])
    #     return nextstate, reward
          
        
    def extract_action(action):
        return action[1]
        
    def extract_hint(action):
        return action[0]
    
    
robot = LyingRobot(camera = False)
count = 0
while count<50:
    print('Iteration:', count,'/50 \n')
    if count > 0:    
        robot.speaker.speak('Are you ready for the next game?', 1)
        print('Ready for the next game? (Y/N)')
        robot.playerAnswer()
    robot.playPipeline()
    robot.push_r.setPosition(float(2.47))
    robot.push_p.setPosition(float(2.47))
    robot.push_s.setPosition(float(2.47))
    robot.choiceLock = False
    count+=1
robot.saveExperimentData()
print('Session Finished')

