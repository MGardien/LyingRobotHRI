from controller import Robot, Keyboard, Display, Motion, Motor, Camera
import numpy as np
import cv2
from random import randrange


class NaoRobot(Robot):
    

    def __init__(self):
        super(NaoRobot, self).__init__()
        print('> Starting robot controller')
        
        self.timeStep = 32
        self.step(self.timeStep)
       
    def show_move(self):
        self.movements = ['rock', 'paper', 'scissors']
        self.move = self.movements[randrange(3)]
        
        if self.move == 0:
            print('rock')
            image = cv2.imread(r'rock.png')
        elif self.move == 1:
            print('paper')
            image = cv2.imread(r'paper.png')
        else:
            print('scissors')
            image = cv2.imread(r'scissors.png')
        
        cv2.imshow('HumanChoice', image)
        cv2.waitKey(0)
        #alernative: cv2.waitKey(0); cv2.destroyAllWindows(); cv2.waitKey(1)
   
robot = NaoRobot()


robot.show_move()