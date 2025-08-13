# AI Posture corrector

The goal/idea of this project is to build an AI posture corrector which will scan through the webcam of your laptop and give you suggestions based on your posture, as to what to do.

### Phase 1: Getting video feed

#### 1. We first start by installing python libraries such as opencv for getting the video

How to capture a video:
- Use cv2.VideoCapture() to create a video capture object for the camera.
- Create a VideoWriter object to save captured frames as a video in the computer.
- Set up an infinite while loop and use the read() method to read the frames using the above created object.
- Use cv2.imshow() method to show the frames in the video.
- Breaks the loop when the user clicks a specific key.