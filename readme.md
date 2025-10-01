# 🏃‍♂️ AI Posture Corrector

An intelligent posture monitoring system that uses AI-powered computer vision to detect slouching and provide real-time feedback with audio alerts. Available as both a desktop application and web interface.

## ✨ Features

- **Real-time Posture Detection**: Uses MediaPipe AI to analyze your posture through your webcam
- **Smart Alerts**: Audio beep notifications when slouching is detected
- **Grace Period**: Configurable delay before alerts to avoid false alarms
- **Web Interface**: Streamlit-based web application for easy access
- **Desktop Version**: Traditional OpenCV application with video recording
- **Adjustable Sensitivity**: Customize detection thresholds for your needs

## 🚀 Quick Start

### Option 1: Web Application (Recommended)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Streamlit App**:
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Access the App**: Open your browser to `http://localhost:8501`

### Option 2: Desktop Application

1. **Install Dependencies**:
   ```bash
   pip install opencv-python mediapipe numpy
   ```

2. **Run Desktop App**:
   ```bash
   python main.py
   ```

3. **Controls**: Press 'q' to quit

## 📋 Requirements

- Python 3.8+
- Webcam/Camera access
- Dependencies listed in `requirements.txt`

## 🔧 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/AI-Posture-Corrector.git
   cd AI-Posture-Corrector
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   # For web interface
   streamlit run streamlit_app.py
   
   # For desktop application
   python main.py
   ```

## 🌐 Deploy to Streamlit Cloud

1. **Fork this repository** to your GitHub account
2. **Visit** [share.streamlit.io](https://share.streamlit.io)
3. **Connect your GitHub** account
4. **Deploy** by selecting your forked repository
5. **Set the main file** to `streamlit_app.py`

## 📊 How It Works

### 1. Pose Detection
- Uses Google's MediaPipe framework
- Detects 33 body landmarks in real-time
- Focuses on nose, left shoulder, and right shoulder positions

### 2. Posture Analysis
- Calculates horizontal distance between nose and shoulder midpoint
- Compares against configurable threshold (default: 0.02)
- Determines if user is slouching based on forward head position

### 3. Smart Feedback System
- **Grace Period**: 5-second delay before alerts (configurable)
- **Audio Alerts**: Beep sound every 3 seconds while slouching
- **Visual Feedback**: Real-time posture status display
- **Distance Metrics**: Shows exact measurements for transparency

## 🎛️ Configuration

### Desktop Application (`main.py`)
- `grace_period`: Time before slouch alert (default: 5 seconds)
- `forward_threshold`: Sensitivity threshold (default: 0.02)
- `beep_interval`: Time between beeps (default: 3 seconds)

### Web Application (`streamlit_app.py`)
- Configurable through sidebar controls
- Real-time sensitivity adjustment
- Toggle sound alerts on/off
- Adjustable grace period

## 📁 Project Structure

```
AI-Posture-Corrector/
├── main.py              # Desktop application with beeping
├── streamlit_app.py     # Web application interface
├── angle.py             # Angle calculation utilities
├── requirements.txt     # Python dependencies
├── readme.md           # This file
├── image.png           # MediaPipe pose landmarks diagram
└── tempCodeRunnerFile.py # Temporary file
```

## 🔊 Audio Features

### Desktop Version
- Uses `winsound` library for Windows systems
- Fallback to system beep (`\a`) for other platforms
- Non-blocking audio with threading

### Web Version
- Browser-based audio using Web Audio API
- JavaScript implementation for cross-platform compatibility
- Configurable through UI controls

## 🎯 Technical Details

- **AI Model**: MediaPipe Pose Detection
- **Detection Points**: 33 body landmarks
- **Key Landmarks**: Nose, Left Shoulder, Right Shoulder
- **Algorithm**: Horizontal distance calculation
- **Default Threshold**: 0.02 (lower = more sensitive)
- **Grace Period**: 5 seconds (configurable)
- **Video Output**: Desktop version saves to `output.mp4`

## 🐛 Troubleshooting

### Common Issues

1. **Camera not detected**:
   - Ensure camera permissions are granted
   - Check if another application is using the camera
   - Try changing camera index in `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`

2. **Audio not working**:
   - On Windows: Ensure sound is not muted
   - On Web: Check browser audio permissions
   - Try enabling/disabling audio alerts in settings

3. **False slouch detection**:
   - Adjust sensitivity threshold
   - Ensure good lighting conditions
   - Position camera at eye level

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **MediaPipe**: Google's ML framework for pose detection
- **OpenCV**: Computer vision library
- **Streamlit**: Web application framework
- **Community**: Thanks to all contributors and users

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Open an issue on GitHub
3. Provide detailed information about your setup and the problem

---

**Happy posturing! 🏃‍♂️✨**

