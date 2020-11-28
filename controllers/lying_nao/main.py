"""tutoria2"""

# Britt van Gemert - s4555740
# Veronne Reinders - s4603478

from controller import Robot, Keyboard, Display, Motion, Motor, Camera
import numpy as np
import cv2
from io import BytesIO
import threading

class MyRobot(Robot):
    def __init__(self, ext_camera_flag, bottom_camera_flag):
        super(MyRobot, self).__init__()
        print('> Starting robot controller')
        
        self.currentlyPlaying = False
        
        self.timeStep = 32 # Milisecs to process the data (loop frequency) - Use int(self.getBasicTimeStep()) for default
        self.state = 0 # Idle starts for selecting different states
        
        self.load_motion_files()
        
        # Sensors init
        self.gps = self.getGPS('gps')
        self.gps.enable(self.timeStep)
        
        self.step(self.timeStep) # Execute one step to get the initial position
        
        # Internal camera
        self.bottom_camera = bottom_camera_flag
        self.displayCamBottom = self.getCamera('CameraBottom')    
        
        # External camera
        self.ext_camera = ext_camera_flag        
        self.displayCamExt = self.getDisplay('CameraExt')
        
        if self.ext_camera:
            self.cameraExt = cv2.VideoCapture(0)
        
        # Cascade for face recognition
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        
        self.hri_ball = 0
        self.hri_face = 0
                    
        # Keyboard
        self.keyboard.enable(self.timeStep)
        self.keyboard = self.getKeyboard()
        
        # Head Motors
        self.head_yaw_motor = self.getMotor('HeadYaw')
        self.head_pitch_motor = self.getMotor('HeadPitch')
        
    def load_motion_files(self):
        # Load all motions
        self.backwards = Motion('../../motions/Backwards.motion')
        self.forwards = Motion('../../motions/Forwards.motion')
        self.forwards50 = Motion('../../motions/Forwards50.motion')
        self.handWave = Motion('../../motions/HandWave.motion')
        self.shoot = Motion('../../motions/Shoot.motion')
        self.sideStepLeft = Motion('../../motions/SideStepLeft.motion')
        self.sideStepRight = Motion('../../motions/SideStepRight.motion')
        self.standUpFromFront = Motion('../../motions/StandUpFromFront.motion')
        self.turnLeft40 = Motion('../../motions/TurnLeft40.motion')
        self.turnLeft60 = Motion('../../motions/TurnLeft60.motion')
        self.turnLeft180 = Motion('../../motions/TurnLeft180.motion')
        self.turnRight40 = Motion('../../motions/TurnRight40.motion')
        self.turnRight60 = Motion('../../motions/TurnRight60.motion')

    def start_motion(self, motion):
        # Stop current motion if any is playing
        if self.currentlyPlaying:
            self.currentlyPlaying.stop()

        # Start the requested motion
        motion.play()
        motion.setLoop(True)
        self.currentlyPlaying = motion
        
    def camera_read_bottom(self):
    
        img_ball = []
        
        if self.bottom_camera:
        
            # Get the images from the internal bottom camera
            self.displayCamBottom.enable(1)
            cameraBottom = self.displayCamBottom.getImage()
            
            # Width and height of camera view   
            width = self.displayCamBottom.getWidth()
            height = self.displayCamBottom.getHeight()
            
            # Convert bytes to nparray 
            nparr = np.frombuffer(cameraBottom, np.uint8)
            img = nparr.reshape(height, width, 4)  
            
            # Transform BGR (RGB) to HSV         
            hsv_ball = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Image thresholding
            lower_green = np.array([36,0,0]) 
            upper_green = np.array([70,255,255])
            
            bw = cv2.inRange(hsv_ball, lower_green, upper_green)
            
            # Contours
            contours, hierarchy = cv2.findContours(bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            
            if contours:
                self.hri_ball += 1
                c_mass = cv2.moments(contours[0])
                
                if c_mass["m00"] != 0:
                    # Obtain centre of ball
                    cx = int(c_mass["m10"]/c_mass["m00"])
                    cy = int(c_mass["m01"]/c_mass["m00"])
                    
                    self.look_at(cx, cy, width, height, 'ball')
            else:
                self.hri_ball = 0
           
        return img
    
    # Captures the external camera frames 
    # Returns the image downsampled by 2   
    def camera_read_external(self):
        img = []
        if self.ext_camera:
            # Capture frame-by-frame
            ret, frame = self.cameraExt.read()
            # Our operations on the frame come here
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # From openCV BGR to RGB
            img = cv2.resize(img, None, fx=0.5, fy=0.5) # image downsampled by 2
            face = self.face_cascade.detectMultiScale(img, 1.3, 5)
            
            width = self.cameraExt.get(cv2.CAP_PROP_FRAME_WIDTH)  # float
            height = self.cameraExt.get(cv2.CAP_PROP_FRAME_HEIGHT)
            
            if len(face) > 0:
                self.hri_face += 1
                for (x,y,w,h) in face:                       
                    cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                    cv2.circle(img,(int(x+(w/2)),int(y+(h/2))), 2, (0,0,255), 4)
                    
                    # Devide width and height by 2 because the image was downsampled by 2
                    self.look_at(int(x+(w/2)), int(y+(h/2)), width/2, height/2, 'face')
            else:
                self.hri_face = 0
            
        return img
    
    def look_at(self, x_centre, y_centre, width, height, object):
        # Calculate the center of the view field (camera frame)
        cv_x_centre = width / 2
        cv_y_centre = height / 2
                
        # Calculate the position of the face with respect to the centre of the frame.
        # Devide by x because the head motor has a rotation limit 
        if object == 'face':
            w_to_cntr = (x_centre - cv_x_centre) / 200
            h_to_cntr = (y_centre - cv_y_centre) / 200
        elif object == 'ball':
            w_to_cntr = (cv_x_centre - x_centre) / 200
            h_to_cntr = (y_centre - cv_y_centre) / 200
    
        self.head_yaw_motor.setPosition(w_to_cntr)
        self.head_yaw_motor.setVelocity(1)
        self.head_pitch_motor.setPosition(h_to_cntr)
        self.head_pitch_motor.setVelocity(1)
        
            
    # Displays the image on the webots camera display interface
    def image_to_display(self, img):
        if self.ext_camera:
            height, width, channels = img.shape
            imageRef = self.displayCamExt.imageNew(cv2.transpose(img).tolist(), Display.RGB, width, height)
            self.displayCamExt.imagePaste(imageRef, 0, 0)
    
    def print_gps(self):
        gps_data = self.gps.getValues();
        print('----------gps----------')
        print(' [x y z] =  [' + str(gps_data[0]) + ',' + str(gps_data[1]) + ',' + str(gps_data[2]) + ']' )
        
    def printHelp(self):
        print(
            'Commands:\n'
            ' H for displaying the commands\n'
            ' G for print the gps\n'
        )
    
    def run_keyboard(self):
    
        self.printHelp()
        previous_message = ''

        # Main loop.
        while True:
            # Deal with the pressed keyboard key.
            k = self.keyboard.getKey()
            message = ''
            if k == ord('G'):
                self.print_gps() 
            elif k == ord('H'):
                self.printHelp()
            elif k == Keyboard.LEFT:
                self.head_yaw_motor.setPosition(float('inf'))
                self.head_yaw_motor.setVelocity(1.0)
            elif k == Keyboard.RIGHT:
                self.head_yaw_motor.setPosition(float('inf'))
                self.head_yaw_motor.setVelocity(-1.0)            
            elif k == Keyboard.UP:
                self.start_motion(self.forwards)
            elif k == Keyboard.DOWN:
                self.start_motion(self.backwards)
            elif k == ord('S'):
                self.head_yaw_motor.setVelocity(0)
                if self.currentlyPlaying:    
                    self.currentlyPlaying.stop()
                    
            # Perform a simulation step, quit the loop when
            # Webots is about to quit.
            if self.step(self.timeStep) == -1:
                break
                
        # finallize class. Destroy external camera.
        if self.ext_camera:
            self.cameraExt.release() 
                
    # Face following main function
    def run_face_follower(self):
        # main control loop: perform simulation steps of self.timeStep milliseconds
        # and leave the loop when the simulation is over

        while self.step(self.timeStep) != -1:
            self.image_to_display(self.camera_read_external())           
            
        # finallize class. Destroy external camera.
        if self.ext_camera:
            self.cameraExt.release() 

    # Ball following main function
    def run_ball_follower(self):  
        # main control loop: perform simulation steps of self.timeStep milliseconds
        # and leave the loop when the simulation is over
        while self.step(self.timeStep) != -1:
            img = self.image_to_display(self.camera_read_bottom())
                
        # Destory internal camera    
        if self.bottom_camera:
            self.cameraBottom.disable()

    # HRI behaviour main function
    def run_hri(self):
        # main control loop: perform simulation steps of self.timeStep milliseconds
        # and leave the loop when the simulation is over
        while self.step(self.timeStep) != -1:
            if self.hri_ball == 1:
                self.shoot.play()
            elif self.hri_face == 1:
                self.handWave.play()
                
# create the Robot instance and run the controller
robot = MyRobot(ext_camera_flag = True, bottom_camera_flag = True)
print('hello')
#robot.run_keyboard()
#robot.run_face_follower()
#robot.run_ball_follower()
t1 = threading.Thread(target=robot.run_face_follower, args=())
t1.start()
robot.run_hri()


