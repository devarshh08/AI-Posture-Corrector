import cv2

webcam = cv2.VideoCapture(0)

#getting default frame width and height
frame_width = int(webcam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(webcam.get(cv2.CAP_PROP_FRAME_HEIGHT))

#defining codec and creating an object
fourcc = cv2.VideoWriter_fourcc(*'mpv4')
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))

while True:
    ret, frame = webcam.read()

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