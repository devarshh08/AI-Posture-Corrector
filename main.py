import cv2
import mediapipe as mp
from angle import calculate_angle
import numpy as np
import time
import winsound
import threading

webcam = cv2.VideoCapture(0)

#getting default frame width and height
frame_width = int(webcam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(webcam.get(cv2.CAP_PROP_FRAME_HEIGHT))

#defining codec and creating an object
fourcc = cv2.VideoWriter_fourcc(*'mpv4')
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))

#we will be detecting pose with mediapipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

#implementing 8 seconds slouch timer
slouch_timer = None
grace_period = 5 
posture_status = "GOOD"
horizontal_distance_display = 0.0
last_beep_time = 0
beep_interval = 3  # Beep every 3 seconds while slouching

def play_beep():
    """Play a beep sound in a separate thread to avoid blocking"""
    try:
        winsound.Beep(1000, 500)  # 1000Hz frequency, 500ms duration
    except:
        # Fallback for systems where winsound doesn't work
        print('\a')  # System beep

while True:
    ret, frame = webcam.read()
    
    #mediapipe was trained on RGB, while opencv reads in BGR; so we convert each frame from BGR to RGB
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    #we will be processing the image to find the pose
    results = pose.process(image_rgb)

    #we will draw skeleton on frame before displaying it
    #drawing pose annotation on the original frame
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame, 
            results.pose_landmarks, 
            mp_pose.POSE_CONNECTIONS
        )
        
    #we will extract the landmarks for the particular joints we want to calculate angle of left elbow
    try:
        landmarks = results.pose_landmarks.landmark
        
        #getting coordinates for upper half
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
        
        #calculating the midpoint between the shoulders
        shoulder_midpoint_x = (left_shoulder.x + right_shoulder.x) / 2
        
        #we will be implementing a forward threshold for more or less sensitivity
        forward_threshold = 0.02
        
        #now we will calculate the angle/horizontal distance which is the absolute distance between the nose and shoulders
        horizontal_distance = abs(nose.x - shoulder_midpoint_x)
        
        is_slouching = horizontal_distance < forward_threshold
        
        #posture status
        if is_slouching:
            if slouch_timer is None:
                slouch_timer = time.time()
            
            elapsed_time = time.time() - slouch_timer
            if elapsed_time > grace_period:
                posture_status = "SLOUCHING"
                # Play beep sound if enough time has passed since last beep
                current_time = time.time()
                if current_time - last_beep_time > beep_interval:
                    threading.Thread(target=play_beep, daemon=True).start()
                    last_beep_time = current_time
        else:
            slouch_timer = None
            posture_status = "GOOD"
        
        #displaying posture status
        cv2.rectangle(frame, (0, 0), (400, 70), (245, 117, 16), -1)
        cv2.putText(frame, 'POSTURE STATUS', (15, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, posture_status, (15, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)
        
        cv2.putText(frame, f'DISTANCE: {round(horizontal_distance, 4)}', (15, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        
    except:
        continue

    #writing frame to output file
    out.write(frame)

    #displaying frame
    cv2.imshow('Camera', frame)

    #press 'q' to exit the loop 
    if cv2.waitKey(1) == ord('q'):
        break
    
webcam.release()
out.release()
cv2.destroyAllWindows()