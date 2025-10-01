import streamlit as st
import cv2
import numpy as np
import time
from PIL import Image
import io

# Try to import mediapipe, fallback to basic analysis if not available
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    st.error("MediaPipe not available. Using basic analysis mode.")

# Page configuration
st.set_page_config(
    page_title="AI Posture Corrector",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_pose_model():
    """Load MediaPipe pose model if available"""
    if not MEDIAPIPE_AVAILABLE:
        return None, None, None
    
    try:
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        mp_drawing = mp.solutions.drawing_utils
        return mp_pose, pose, mp_drawing
    except Exception as e:
        st.error(f"Error loading MediaPipe: {str(e)}")
        return None, None, None

def analyze_posture_basic(image):
    """Basic posture analysis without MediaPipe"""
    # Convert to grayscale for basic analysis
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # Simple edge detection to find potential head/shoulder region
    edges = cv2.Canny(gray, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Basic analysis - this is a simplified approach
    height, width = gray.shape
    upper_region = gray[:height//3, :]  # Top third of image
    
    # Calculate intensity distribution in upper region
    intensity_profile = np.mean(upper_region, axis=0)
    center_deviation = np.std(intensity_profile)
    
    # Simple heuristic: higher deviation might indicate forward head posture
    is_slouching = center_deviation > 30  # Threshold determined experimentally
    confidence = min(center_deviation / 50.0, 1.0)
    
    return {
        'slouching': is_slouching,
        'confidence': confidence,
        'deviation': center_deviation,
        'method': 'basic_analysis'
    }

def analyze_posture_mediapipe(image, mp_pose, pose, mp_drawing):
    """MediaPipe-based posture analysis"""
    # Convert BGR to RGB for MediaPipe
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Process the image
    results = pose.process(image_rgb)
    
    if not results.pose_landmarks:
        return {
            'slouching': False,
            'confidence': 0.0,
            'distance': 0.0,
            'method': 'mediapipe',
            'landmarks_detected': False
        }
    
    # Extract landmarks
    landmarks = results.pose_landmarks.landmark
    
    # Get key points
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
    
    # Calculate shoulder midpoint
    shoulder_midpoint_x = (left_shoulder.x + right_shoulder.x) / 2
    
    # Calculate horizontal distance
    horizontal_distance = abs(nose.x - shoulder_midpoint_x)
    
    # Determine slouching (threshold: 0.02)
    threshold = 0.02
    is_slouching = horizontal_distance < threshold
    
    # Draw landmarks on image
    annotated_image = image.copy()
    mp_drawing.draw_landmarks(
        annotated_image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS
    )
    
    return {
        'slouching': is_slouching,
        'confidence': 1.0,
        'distance': horizontal_distance,
        'method': 'mediapipe',
        'landmarks_detected': True,
        'annotated_image': annotated_image
    }

def play_audio_alert():
    """Play audio alert using HTML audio"""
    audio_html = """
    <audio autoplay>
        <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+LtwmYeCD2T2O/Ifi0FLYLOm9mLP2s" type="audio/wav">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

def main():
    st.title("🏃‍♂️ AI Posture Corrector")
    st.markdown("**Real-time posture monitoring with AI-powered feedback**")
    
    # Sidebar controls
    st.sidebar.header("Settings")
    sensitivity = st.sidebar.slider("Sensitivity", 0.01, 0.05, 0.02, 0.005,
                                   help="Lower values = more sensitive (MediaPipe only)")
    enable_audio = st.sidebar.checkbox("Enable Audio Alerts", value=True)
    analysis_method = st.sidebar.radio(
        "Analysis Method",
        ["Auto (MediaPipe if available)", "Basic Analysis Only"],
        help="Choose analysis method based on your platform"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Instructions")
    st.sidebar.markdown("""
    1. Take a photo using the camera input below
    2. Ensure you're visible from head to shoulders
    3. The app will analyze your posture
    4. Get instant feedback on your posture
    """)
    
    # Load pose model
    mp_pose, pose, mp_drawing = load_pose_model()
    use_mediapipe = (MEDIAPIPE_AVAILABLE and 
                    mp_pose is not None and 
                    analysis_method == "Auto (MediaPipe if available)")
    
    # Display current analysis method
    method_color = "green" if use_mediapipe else "orange"
    method_text = "MediaPipe AI" if use_mediapipe else "Basic Analysis"
    st.markdown(f"**Current Method:** :{method_color}[{method_text}]")
    
    # Camera input
    camera_input = st.camera_input("📷 Take a photo to analyze your posture")
    
    if camera_input is not None:
        # Load and process image
        image = Image.open(camera_input)
        image_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Analyze posture
        with st.spinner("Analyzing posture..."):
            if use_mediapipe:
                result = analyze_posture_mediapipe(image_bgr, mp_pose, pose, mp_drawing)
            else:
                result = analyze_posture_basic(image_array)
        
        # Display results
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Show original or annotated image
            if 'annotated_image' in result:
                display_image = cv2.cvtColor(result['annotated_image'], cv2.COLOR_BGR2RGB)
                st.image(display_image, caption="Posture Analysis with Landmarks", use_column_width=True)
            else:
                st.image(image_array, caption="Posture Analysis", use_column_width=True)
        
        with col2:
            # Status display
            if result['slouching']:
                st.error("⚠️ Poor Posture Detected")
                if enable_audio:
                    play_audio_alert()
                    st.info("🔊 Audio alert played!")
            else:
                st.success("✅ Good Posture")
            
            # Metrics
            st.metric("Confidence", f"{result['confidence']:.2f}")
            
            if 'distance' in result:
                st.metric("Distance", f"{result['distance']:.4f}")
                st.metric("Threshold", f"{sensitivity:.3f}")
            elif 'deviation' in result:
                st.metric("Deviation", f"{result['deviation']:.1f}")
            
            st.info(f"Method: {result['method']}")
            
            # Recommendations
            if result['slouching']:
                st.markdown("### 📋 Recommendations")
                st.markdown("""
                - Sit up straight
                - Pull shoulders back
                - Align head over shoulders
                - Check your monitor height
                - Take regular breaks
                """)
    
    # Information section
    st.markdown("---")
    st.markdown("### How it works")
    
    if use_mediapipe:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**1. AI Detection**")
            st.markdown("Uses MediaPipe to detect 33 body landmarks")
        with col2:
            st.markdown("**2. Distance Analysis**")
            st.markdown("Measures nose-to-shoulder alignment")
        with col3:
            st.markdown("**3. Smart Feedback**")
            st.markdown("Provides instant posture recommendations")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**1. Image Analysis**")
            st.markdown("Analyzes image patterns and edges")
        with col2:
            st.markdown("**2. Posture Estimation**")
            st.markdown("Estimates posture based on visual cues")
    
    # Troubleshooting
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        **MediaPipe Issues:**
        - Try switching to "Basic Analysis Only" if MediaPipe fails
        - Ensure good lighting for better detection
        - Position camera at eye level
        
        **Camera Issues:**
        - Allow camera permissions in your browser
        - Try refreshing the page
        - Use a different device if camera doesn't work
        
        **Audio Issues:**
        - Check browser audio settings
        - Some browsers may block autoplay audio
        - Try clicking in the page area first
        """)
    
    # Credits
    st.markdown("---")
    st.markdown("### 🙏 Credits")
    st.markdown("""
    - **MediaPipe**: Google's ML framework for pose detection
    - **Streamlit**: Web application framework
    - **OpenCV**: Computer vision library
    """)

if __name__ == "__main__":
    main()