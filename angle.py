import numpy as np
import cv2

def calculate_angle(a, b, c):
    #calculates angles between 3 points : a, b and c
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    #next we calculate the vectors between the points and then the angle using arctan2 function
    #https://stackoverflow.com/questions/58953047/issue-with-finding-angle-between-3-points-in-python
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    #ensure angle is between 0 and 180
    if angle > 180.0:
        angle = 360 - angle

    return angle