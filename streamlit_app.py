import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import time
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="AI Posture Corrector",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .status-good {
        background-color: #d4edda;
        border: 2px solid #28a745;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        color: #155724;
    }
    .status-bad {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        color: #721c24;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize MediaPipe
@st.cache_resource
def load_pose_model():
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

mp_pose, pose, mp_drawing = load_pose_model()

def analyze_posture(image, sensitivity=0.02):
    """Analyze posture from a single image"""
    # Convert RGB to BGR for OpenCV
    image_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Convert to RGB for MediaPipe
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    
    # Process the image
    results = pose.process(image_rgb)
    
    if not results.pose_landmarks:
        return {
            'success': False,
            'message': 'No person detected. Please ensure you are visible in the frame.',
            'image': image_bgr
        }
    
    # Draw landmarks
    annotated_image = image_bgr.copy()
    mp_drawing.draw_landmarks(
        annotated_image,
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
        
        # Calculate shoulder midpoint
        shoulder_midpoint_x = (left_shoulder.x + right_shoulder.x) / 2
        
        # Calculate horizontal distance
        horizontal_distance = abs(nose.x - shoulder_midpoint_x)
        
        # Determine posture
        is_slouching = horizontal_distance < sensitivity
        
        # Add status overlay to image
        status_text = "SLOUCHING" if is_slouching else "GOOD POSTURE"
        status_color = (0, 0, 255) if is_slouching else (0, 255, 0)
        
        cv2.rectangle(annotated_image, (0, 0), (450, 80), (245, 117, 16), -1)
        cv2.putText(annotated_image, 'POSTURE STATUS', (15, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(annotated_image, status_text, (15, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, status_color, 3, cv2.LINE_AA)
        
        return {
            'success': True,
            'slouching': is_slouching,
            'distance': horizontal_distance,
            'threshold': sensitivity,
            'image': annotated_image,
            'message': 'Analysis complete'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error analyzing posture: {str(e)}',
            'image': image_bgr
        }

def main():
    # Header
    st.markdown('<div class="main-header">🏃‍♂️ AI Posture Corrector</div>', unsafe_allow_html=True)
    st.markdown("**Snapshot-based posture analysis using MediaPipe AI**")
    
    # Sidebar controls
    st.sidebar.header("⚙️ Settings")
    
    sensitivity = st.sidebar.slider(
        "Sensitivity", 
        0.01, 0.05, 0.02, 0.005,
        help="Lower values = more sensitive (will detect slouching more easily)"
    )
    
    auto_capture = st.sidebar.checkbox(
        "Auto-capture mode",
        value=False,
        help="Automatically analyze when you take a photo"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Instructions")
    st.sidebar.markdown("""
    1. **Position yourself**: Sit in your normal working position
    2. **Frame the shot**: Ensure your head and shoulders are visible
    3. **Take photo**: Click the camera button below
    4. **Get feedback**: Instant posture analysis
    5. **Adjust**: Follow recommendations if needed
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 Tips for Best Results")
    st.sidebar.markdown("""
    - Good lighting is essential
    - Keep camera at eye level
    - Show full head and shoulders
    - Maintain natural posture
    - Avoid extreme angles
    """)
    
    # Main content
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("### 📸 Capture Your Posture")
        camera_photo = st.camera_input("Take a photo to analyze your posture")
        
        if camera_photo is not None:
            # Load image
            image = Image.open(camera_photo)
            
            # Analyze posture
            with st.spinner("🔍 Analyzing your posture..."):
                result = analyze_posture(image, sensitivity)
            
            if result['success']:
                # Display annotated image
                display_image = cv2.cvtColor(result['image'], cv2.COLOR_BGR2RGB)
                st.image(display_image, caption="Posture Analysis with Landmarks", use_container_width=True)
                
                # Show results in col2
                with col2:
                    st.markdown("### 📊 Analysis Results")
                    
                    # Status card
                    if result['slouching']:
                        st.markdown("""
                        <div class="status-bad">
                            ⚠️ Poor Posture Detected
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Play audio alert
                        st.audio("data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgA", autoplay=True)
                        
                    else:
                        st.markdown("""
                        <div class="status-good">
                            ✅ Good Posture!
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Metrics
                    metric_col1, metric_col2 = st.columns(2)
                    with metric_col1:
                        st.metric(
                            "Distance", 
                            f"{result['distance']:.4f}",
                            help="Horizontal distance between nose and shoulder midpoint"
                        )
                    with metric_col2:
                        st.metric(
                            "Threshold", 
                            f"{result['threshold']:.4f}",
                            help="Sensitivity threshold for slouching detection"
                        )
                    
                    # Recommendations
                    if result['slouching']:
                        st.markdown("### 📝 Recommendations")
                        st.error("""
                        **Your head is too far forward. Try to:**
                        - Pull your shoulders back
                        - Align your head directly over your shoulders
                        - Adjust your monitor to eye level
                        - Check your chair height
                        - Take a 2-minute stretch break
                        """)
                        
                        st.markdown("### 🧘 Quick Exercises")
                        with st.expander("Chin Tucks (30 seconds)"):
                            st.markdown("""
                            1. Sit up straight
                            2. Keep your eyes forward
                            3. Pull your chin straight back (like making a double chin)
                            4. Hold for 5 seconds
                            5. Repeat 5 times
                            """)
                        
                        with st.expander("Shoulder Blade Squeeze (30 seconds)"):
                            st.markdown("""
                            1. Sit or stand up straight
                            2. Pull your shoulder blades together
                            3. Hold for 5 seconds
                            4. Relax
                            5. Repeat 5 times
                            """)
                    else:
                        st.success("""
                        **Great posture!** Keep it up by:
                        - Maintaining this position
                        - Taking regular breaks
                        - Doing stretches every hour
                        - Staying hydrated
                        """)
            else:
                st.error(result['message'])
                st.info("💡 **Tips:** Make sure you're clearly visible with good lighting and proper framing.")
    
    with col2:
        if camera_photo is None:
            st.markdown("### 👋 Welcome!")
            st.info("""
            This app uses **MediaPipe AI** to analyze your posture in real-time.
            
            **How it works:**
            1. Detects 33 body landmarks
            2. Measures nose-to-shoulder alignment
            3. Provides instant feedback
            4. Suggests corrective exercises
            
            **Ready?** Take a photo using the camera on the left!
            """)
            
            # Show example
            st.markdown("### 🖼️ Example Analysis")
            st.image("https://via.placeholder.com/400x300/28a745/ffffff?text=Good+Posture", 
                     caption="✅ Good: Head aligned over shoulders")
            st.image("https://via.placeholder.com/400x300/dc3545/ffffff?text=Poor+Posture", 
                     caption="⚠️ Poor: Head too far forward")
    
    # Footer information
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔬 Technology")
        st.markdown("""
        - **MediaPipe Pose**: Google's ML framework
        - **OpenCV**: Computer vision processing
        - **Streamlit**: Interactive web interface
        """)
    
    with col2:
        st.markdown("### ❓ Why Posture Matters")
        st.markdown("""
        - Reduces neck/back pain
        - Improves breathing
        - Increases energy levels
        - Boosts confidence
        - Prevents long-term damage
        """)
    
    with col3:
        st.markdown("### 🎯 Best Practices")
        st.markdown("""
        - Check posture every 30 mins
        - Take breaks every hour
        - Adjust workstation ergonomics
        - Do daily stretches
        - Stay active
        """)
    
    # Troubleshooting
    with st.expander("🔧 Troubleshooting & FAQ"):
        st.markdown("""
        **Q: Why isn't my posture being detected?**
        A: Make sure your full head and shoulders are visible in the frame with good lighting.
        
        **Q: The app says I'm slouching but I'm not?**
        A: Adjust the sensitivity slider in the settings. Higher values = less sensitive.
        
        **Q: Can I use this on mobile?**
        A: Yes! The app works on mobile browsers with camera access.
        
        **Q: How accurate is the detection?**
        A: MediaPipe has 95%+ accuracy for landmark detection in good conditions.
        
        **Q: Why use snapshot instead of live video?**
        A: Streamlit Cloud has limitations with WebRTC. Snapshots work reliably everywhere.
        
        **Q: How often should I check my posture?**
        A: Check every 30 minutes during work hours for best results.
        """)

if __name__ == "__main__":
    main()