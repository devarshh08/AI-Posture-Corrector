import streamlit as st
import cv2
import mediapipe as mp
from angle import calculate_angle
import numpy as np
import time
import threading
from PIL import Image

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

def play_browser_beep():
    """Play beep using JavaScript in browser"""
    st.markdown(
        """
        <script>
        var context = new (window.AudioContext || window.webkitAudioContext)();
        var oscillator = context.createOscillator();
        var gainNode = context.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(context.destination);
        
        oscillator.frequency.value = 1000;
        gainNode.gain.setValueAtTime(0.3, context.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, context.currentTime + 0.5);
        
        oscillator.start(context.currentTime);
        oscillator.stop(context.currentTime + 0.5);
        </script>
        """,
        unsafe_allow_html=True
    )

def process_frame(frame, mp_pose, pose, mp_drawing):
    # Convert BGR to RGB
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the image to find pose
    results = pose.process(image_rgb)
    
    posture_status = "GOOD"
    horizontal_distance = 0.0
    is_slouching = False
    
    # Draw pose landmarks
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame,
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
            
            # Forward threshold for sensitivity
            forward_threshold = 0.02
            
            # Calculate horizontal distance
            horizontal_distance = abs(nose.x - shoulder_midpoint_x)
            
            is_slouching = horizontal_distance < forward_threshold
            
            if is_slouching:
                posture_status = "SLOUCHING"
            else:
                posture_status = "GOOD"
                
        except:
            pass
    
    # Add status overlay
    cv2.rectangle(frame, (0, 0), (400, 70), (245, 117, 16), -1)
    cv2.putText(frame, 'POSTURE STATUS', (15, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(frame, posture_status, (15, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)
    
    cv2.putText(frame, f'DISTANCE: {round(horizontal_distance, 4)}', (15, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
    
    return frame, posture_status, horizontal_distance, is_slouching

def main():
    st.title("🏃‍♂️ AI Posture Corrector")
    st.markdown("**Real-time posture monitoring with AI-powered feedback**")
    
    # Sidebar controls
    st.sidebar.header("Settings")
    grace_period = st.sidebar.slider("Grace Period (seconds)", 1, 10, 5, 
                                    help="Time before alerting about slouching")
    beep_enabled = st.sidebar.checkbox("Enable Sound Alerts", value=True)
    sensitivity = st.sidebar.slider("Sensitivity", 0.01, 0.05, 0.02, 0.005,
                                   help="Lower values = more sensitive")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Instructions")
    st.sidebar.markdown("""
    1. Allow camera access when prompted
    2. Sit in front of your camera
    3. The app will monitor your posture
    4. You'll get alerts when slouching is detected
    """)
    
    # Load pose model
    mp_pose, pose, mp_drawing = load_pose_model()
    
    # Initialize session state
    if 'slouch_timer' not in st.session_state:
        st.session_state.slouch_timer = None
    if 'last_beep_time' not in st.session_state:
        st.session_state.last_beep_time = 0
    
    # Camera input
    camera_input = st.camera_input("Take a photo to analyze posture")
    
    if camera_input is not None:
        # Convert PIL Image to OpenCV format
        image = Image.open(camera_input)
        frame = np.array(image)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Process frame
        processed_frame, posture_status, horizontal_distance, is_slouching = process_frame(
            frame, mp_pose, pose, mp_drawing
        )
        
        # Convert back to RGB for display
        processed_frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        
        # Display results
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.image(processed_frame_rgb, caption="Posture Analysis", use_column_width=True)
        
        with col2:
            # Status display
            if posture_status == "GOOD":
                st.success("✅ Good Posture")
            else:
                st.error("⚠️ Slouching Detected")
            
            st.metric("Horizontal Distance", f"{horizontal_distance:.4f}")
            st.metric("Sensitivity Threshold", f"{sensitivity:.3f}")
            
            # Slouching timer logic
            current_time = time.time()
            
            if is_slouching:
                if st.session_state.slouch_timer is None:
                    st.session_state.slouch_timer = current_time
                
                elapsed_time = current_time - st.session_state.slouch_timer
                
                if elapsed_time > grace_period:
                    st.error(f"🔔 Slouching for {elapsed_time:.1f} seconds!")
                    
                    # Play beep if enabled and enough time has passed
                    if (beep_enabled and 
                        current_time - st.session_state.last_beep_time > 3):
                        play_browser_beep()
                        st.session_state.last_beep_time = current_time
                else:
                    remaining_time = grace_period - elapsed_time
                    st.warning(f"⏰ Grace period: {remaining_time:.1f}s remaining")
            else:
                st.session_state.slouch_timer = None
                st.info("👍 Keep up the good posture!")
    
    # Information section
    st.markdown("---")
    st.markdown("### How it works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**1. Pose Detection**")
        st.markdown("Uses MediaPipe AI to detect body landmarks")
    
    with col2:
        st.markdown("**2. Posture Analysis**")
        st.markdown("Calculates distance between nose and shoulder midpoint")
    
    with col3:
        st.markdown("**3. Smart Alerts**")
        st.markdown("Provides feedback with grace period to avoid false alarms")
    
    # Technical details in expander
    with st.expander("Technical Details"):
        st.markdown("""
        - **AI Model**: MediaPipe Pose Detection
        - **Detection Points**: 33 body landmarks
        - **Key Points**: Nose, Left Shoulder, Right Shoulder
        - **Algorithm**: Horizontal distance calculation
        - **Threshold**: Configurable sensitivity (default: 0.02)
        - **Grace Period**: Configurable delay before alerts (default: 5s)
        """)

if __name__ == "__main__":
    main()