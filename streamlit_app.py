import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import time
from PIL import Image
import threading

# Set page configuration
st.set_page_config(
    page_title="AI Posture Corrector",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 20px;
    }
    </style>
""", unsafe_allow_html=True)

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

# Session state initialization
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False
if 'slouch_timer' not in st.session_state:
    st.session_state.slouch_timer = None
if 'posture_status' not in st.session_state:
    st.session_state.posture_status = "READY"
if 'last_distance' not in st.session_state:
    st.session_state.last_distance = 0.0
if 'frame_count' not in st.session_state:
    st.session_state.frame_count = 0

def analyze_frame(frame, sensitivity, grace_period):
    """Analyze a single frame for posture"""
    # Convert to RGB
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process with MediaPipe
    results = pose.process(image_rgb)
    
    if not results.pose_landmarks:
        return frame, "NO DETECTION", 0.0
    
    # Draw landmarks
    mp_drawing.draw_landmarks(
        frame,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
        mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
    )
    
    try:
        landmarks = results.pose_landmarks.landmark
        
        # Get key points
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
        
        # Calculate metrics
        shoulder_midpoint_x = (left_shoulder.x + right_shoulder.x) / 2
        horizontal_distance = abs(nose.x - shoulder_midpoint_x)
        
        # Determine posture
        is_slouching = horizontal_distance < sensitivity
        current_time = time.time()
        
        if is_slouching:
            if st.session_state.slouch_timer is None:
                st.session_state.slouch_timer = current_time
            
            elapsed = current_time - st.session_state.slouch_timer
            if elapsed > grace_period:
                status = "SLOUCHING"
            else:
                status = f"WARNING ({int(grace_period - elapsed)}s)"
        else:
            st.session_state.slouch_timer = None
            status = "GOOD POSTURE"
        
        st.session_state.last_distance = horizontal_distance
        
        # Add status overlay
        status_color = (0, 0, 255) if status == "SLOUCHING" else (0, 255, 0) if status == "GOOD POSTURE" else (255, 165, 0)
        
        cv2.rectangle(frame, (0, 0), (500, 90), (245, 117, 16), -1)
        cv2.putText(frame, 'POSTURE STATUS', (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, status, (15, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, status_color, 3, cv2.LINE_AA)
        
        # Add distance info
        cv2.putText(frame, f'Distance: {horizontal_distance:.4f}', (15, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
        
        return frame, status, horizontal_distance
        
    except Exception as e:
        return frame, f"ERROR: {str(e)}", 0.0

def main():
    st.markdown('<div class="main-header">🏃‍♂️ AI Posture Corrector - Live Mode</div>', unsafe_allow_html=True)
    st.markdown("**Continuous posture monitoring with auto-refresh**")
    
    # Sidebar
    st.sidebar.header("⚙️ Settings")
    
    sensitivity = st.sidebar.slider(
        "Sensitivity", 
        0.01, 0.05, 0.02, 0.005,
        help="Lower = more sensitive"
    )
    
    grace_period = st.sidebar.slider(
        "Grace Period (seconds)", 
        1, 10, 5,
        help="Time before alerting"
    )
    
    refresh_rate = st.sidebar.slider(
        "Refresh Rate (seconds)",
        0.5, 3.0, 1.0, 0.5,
        help="How often to update (lower = smoother but more CPU)"
    )
    
    enable_audio = st.sidebar.checkbox("Enable Audio Alerts", value=True)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 How to Use")
    st.sidebar.markdown("""
    1. Click **START MONITORING**
    2. Allow camera access
    3. Position yourself in frame
    4. App monitors continuously
    5. Click **STOP** when done
    """)
    
    # Main layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("### 📹 Live Feed")
        
        # Control buttons
        button_col1, button_col2 = st.columns(2)
        with button_col1:
            if st.button("▶️ START MONITORING", disabled=st.session_state.monitoring, use_container_width=True):
                st.session_state.monitoring = True
                st.session_state.frame_count = 0
                st.rerun()
        
        with button_col2:
            if st.button("⏹️ STOP MONITORING", disabled=not st.session_state.monitoring, use_container_width=True):
                st.session_state.monitoring = False
                st.session_state.posture_status = "STOPPED"
                st.rerun()
        
        # Video placeholder
        video_placeholder = st.empty()
        
        # Live monitoring
        if st.session_state.monitoring:
            # Use camera input with auto-refresh
            camera_photo = st.camera_input(
                "Live Feed", 
                key=f"camera_{st.session_state.frame_count}",
                label_visibility="collapsed"
            )
            
            if camera_photo is not None:
                # Load and process frame
                image = Image.open(camera_photo)
                frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # Analyze
                processed_frame, status, distance = analyze_frame(frame, sensitivity, grace_period)
                st.session_state.posture_status = status
                
                # Display
                display_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                video_placeholder.image(display_frame, use_container_width=True)
                
                # Auto-refresh
                time.sleep(refresh_rate)
                st.session_state.frame_count += 1
                st.rerun()
            else:
                video_placeholder.info("📸 Waiting for camera... Please allow camera access in your browser.")
        else:
            video_placeholder.info("👆 Click START MONITORING to begin")
    
    with col2:
        st.markdown("### 📊 Status Dashboard")
        
        # Status card
        status = st.session_state.posture_status
        
        if status == "SLOUCHING":
            st.error(f"⚠️ **{status}**")
            if enable_audio:
                st.markdown("""
                <audio autoplay>
                    <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgA" type="audio/wav">
                </audio>
                """, unsafe_allow_html=True)
        elif status == "GOOD POSTURE":
            st.success(f"✅ **{status}**")
        elif status.startswith("WARNING"):
            st.warning(f"⏰ **{status}**")
        elif status == "NO DETECTION":
            st.info("👤 **No person detected**")
        elif status == "READY":
            st.info("🎬 **Ready to start**")
        elif status == "STOPPED":
            st.info("⏹️ **Monitoring stopped**")
        else:
            st.error(f"❌ **{status}**")
        
        # Metrics
        st.markdown("---")
        st.markdown("### 📈 Metrics")
        
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric("Distance", f"{st.session_state.last_distance:.4f}")
        with metric_col2:
            st.metric("Threshold", f"{sensitivity:.4f}")
        
        if st.session_state.monitoring:
            st.metric("Frames Analyzed", st.session_state.frame_count)
        
        # Recommendations
        st.markdown("---")
        st.markdown("### 💡 Tips")
        
        if status == "SLOUCHING":
            st.error("""
            **Fix your posture:**
            - Pull shoulders back
            - Align head over shoulders
            - Adjust monitor height
            - Take a stretch break
            """)
        else:
            st.success("""
            **Keep it up:**
            - Maintain this position
            - Check posture regularly
            - Stay hydrated
            - Take breaks every hour
            """)
        
        # Quick exercises
        with st.expander("🧘 Quick Exercises"):
            st.markdown("""
            **Chin Tucks (30s)**
            1. Sit straight
            2. Pull chin back
            3. Hold 5 seconds
            4. Repeat 5x
            
            **Shoulder Rolls (30s)**
            1. Roll shoulders back
            2. 10 times slowly
            3. Repeat forward
            """)
    
    # Info footer
    st.markdown("---")
    st.info("""
    💡 **Note:** This uses periodic camera captures for live monitoring. 
    For true real-time video, you'll need to run the app locally using `main.py` which uses direct webcam access.
    
    **Refresh Rate:** Adjust in settings for smoother updates (higher CPU usage) or better performance (slower updates).
    """)
    
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        **Camera not working?**
        - Allow camera permissions in browser
        - Refresh the page
        - Try a different browser (Chrome/Edge recommended)
        
        **Slow/Laggy?**
        - Increase refresh rate in settings
        - Close other applications
        - Use better lighting for faster processing
        
        **Want true real-time?**
        - Download the code
        - Run `python main.py` locally
        - This bypasses Streamlit Cloud limitations
        """)

if __name__ == "__main__":
    main()