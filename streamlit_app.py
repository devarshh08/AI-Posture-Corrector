import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import time
from PIL import Image
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration, WebRtcMode

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

# RTC Configuration for deployment (improved)
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [
        {"urls": ["stun:stun.l.google.com:19302"]},
        {"urls": ["stun:stun1.l.google.com:19302"]},
    ]}
)

class PostureProcessor(VideoProcessorBase):
    def __init__(self):
        self.sensitivity = 0.02
        self.grace_period = 5
        self.beep_interval = 3
        self.slouch_timer = None
        self.last_beep_time = 0
        self.posture_status = "GOOD"

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Process the image to find pose
        results = pose.process(image_rgb)
        
        # Draw pose landmarks
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                img,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
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
                    if self.slouch_timer is None:
                        self.slouch_timer = current_time
                    
                    elapsed_time = current_time - self.slouch_timer
                    if elapsed_time > self.grace_period:
                        self.posture_status = "SLOUCHING"
                        st.session_state.posture_status = "SLOUCHING"
                else:
                    self.slouch_timer = None
                    self.posture_status = "GOOD"
                    st.session_state.posture_status = "GOOD"

            except Exception as e:
                self.posture_status = "ERROR"
                st.session_state.posture_status = "ERROR"
        
        # Add status overlay
        status_color = (0, 0, 255) if self.posture_status == "SLOUCHING" else (0, 255, 0)
        cv2.rectangle(img, (0, 0), (400, 70), (245, 117, 16), -1)
        cv2.putText(img, 'POSTURE STATUS', (15, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(img, self.posture_status, (15, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, status_color, 2, cv2.LINE_AA)
        
        return av.VideoFrame.from_ndarray(img, format="bgr24")

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
    
    # Display current posture status
    status_placeholder = st.empty()
    if st.session_state.posture_status == "SLOUCHING":
        status_placeholder.error(f"⚠️ Current Status: {st.session_state.posture_status}")
    elif st.session_state.posture_status == "GOOD":
        status_placeholder.success(f"✅ Current Status: {st.session_state.posture_status}")
    else:
        status_placeholder.info(f"ℹ️ Current Status: {st.session_state.posture_status}")
    
    # WebRTC Streamer
    ctx = webrtc_streamer(
        key="posture-analysis",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        video_processor_factory=PostureProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    
    # Add troubleshooting section
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        **If the video doesn't start:**
        - Make sure you've allowed camera access in your browser
        - Try refreshing the page
        - Check if another application is using your camera
        - Try a different browser (Chrome/Edge work best)
        
        **WebRTC Issues:**
        - If you see connection errors, your network might be blocking WebRTC
        - Try disabling VPN or firewall temporarily
        - Some corporate networks block WebRTC
        
        **Alternative:** Use the simpler `app.py` version for snapshot-based analysis
        """)

if __name__ == "__main__":
    main()