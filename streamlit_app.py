import streamlit as st
import cv2
import mediapipe as mp
from angle import calculate_angle
import numpy as np
import time
from PIL import Image
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration

# Set page configuration
st.set_page_config(
    page_title="AI Posture Corrector",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize MediaPipe
@st.cache_resource
def load_pose_model():
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    mp_drawing = mp.solutions.drawing_utils
    return mp_pose, pose, mp_drawing

mp_pose, pose, mp_drawing = load_pose_model()

# --- App State and Session State ---
if 'slouch_timer' not in st.session_state:
    st.session_state.slouch_timer = None
if 'last_beep_time' not in st.session_state:
    st.session_state.last_beep_time = 0
if 'posture_status' not in st.session_state:
    st.session_state.posture_status = "GOOD"

# RTC Configuration for deployment
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

class PostureTransformer(VideoTransformerBase):
    def __init__(self, sensitivity, grace_period, beep_interval):
        self.sensitivity = sensitivity
        self.grace_period = grace_period
        self.beep_interval = beep_interval

    def transform(self, frame):
        image = frame.to_ndarray(format="bgr24")

        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image to find pose
        results = pose.process(image_rgb)
        
        # Draw pose landmarks
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )
            
            # Extract landmarks
            try:
                landmarks = results.pose_landmarks.landmark
                
                # Get coordinates for upper half
                left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
                
                # Calculate midpoint between shoulders
                shoulder_midpoint_x = (left_shoulder.x + right_shoulder.x) / 2
                
                # Calculate horizontal distance
                horizontal_distance = abs(nose.x - shoulder_midpoint_x)
                
                is_slouching = horizontal_distance < self.sensitivity
                
                current_time = time.time()
                
                if is_slouching:
                    if st.session_state.slouch_timer is None:
                        st.session_state.slouch_timer = current_time
                    
                    elapsed_time = current_time - st.session_state.slouch_timer
                    if elapsed_time > self.grace_period:
                        st.session_state.posture_status = "SLOUCHING"
                        # Beep logic would go here if we could trigger server-side sounds reliably
                else:
                    st.session_state.slouch_timer = None
                    st.session_state.posture_status = "GOOD"

            except Exception as e:
                print(f"Error in landmark processing: {e}") # Log error for debugging
                st.session_state.posture_status = "ERROR"
        
        # Add status overlay
        status_color = (0, 0, 255) if st.session_state.posture_status == "SLOUCHING" else (0, 255, 0)
        cv2.rectangle(image, (0, 0), (400, 70), (245, 117, 16), -1)
        cv2.putText(image, 'POSTURE STATUS', (15, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(image, st.session_state.posture_status, (15, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, status_color, 2, cv2.LINE_AA)
        
        return image

def main():
    st.title("🏃‍♂️ AI Posture Corrector")
    st.markdown("**Real-time posture monitoring with AI-powered feedback**")
    
    # Sidebar controls
    st.sidebar.header("Settings")
    grace_period = st.sidebar.slider("Grace Period (seconds)", 1, 10, 5, 
                                    help="Time before alerting about slouching")
    beep_interval = st.sidebar.slider("Beep Interval (seconds)", 1, 5, 3)
    sensitivity = st.sidebar.slider("Sensitivity", 0.01, 0.05, 0.02, 0.005,
                                   help="Lower values = more sensitive")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Instructions")
    st.sidebar.markdown("""
    1. Click **START** to begin the live feed.
    2. Allow camera access when prompted.
    3. The app will monitor your posture in real-time.
    4. Your posture status will be displayed on the video.
    """)
    
    webrtc_streamer(
        key="posture-analysis",
        video_transformer_factory=lambda: PostureTransformer(sensitivity, grace_period, beep_interval),
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

if __name__ == "__main__":
    main()