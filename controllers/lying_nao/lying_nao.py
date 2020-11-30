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

class LyingNao(Robot):
    def __init__(self):
        super(LyingNao, self).__init__()
        print('> Starting robot controller')
        
        
robot = LyingNao()