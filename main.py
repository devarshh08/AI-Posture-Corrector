import cv2
import mediapipe as mp

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
        
    #we will extract the landmarks
    try:
        landmarks = results.pose_landmarks.landmark
        print(landmarks)
    except:
        pass

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

