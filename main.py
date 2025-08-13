import cv2
import mediapipe as mp
from angle import calculate_angle
import numpy as np

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

#this will load a pretrained neural network into memory

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
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        ear = [landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x, landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y]
        hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        
        #calculating the angle and displaying it
        neck_angle = calculate_angle(ear, shoulder, hip)
        
        #posture status
        if neck_angle < 150:
            posture_status = "SLOUCHING"
        else:
            posture_status = "GOOD"
        
        #displaying posture status
        cv2.rectangle(frame, (0, 0), (400, 70), (245, 117, 16), -1)
        cv2.putText(frame, 'POSTURE STATUS', (15, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, posture_status, (15, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)
        
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

