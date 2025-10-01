# 🏃‍♂️ AI Live Posture Corrector

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-orange?style=for-the-badge&logo=streamlit)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8-green?style=for-the-badge&logo=opencv)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

An intelligent posture monitoring system that uses your webcam to provide real-time, AI-powered feedback to help you correct your posture and reduce slouching.

---

## 📋 Table of Contents

- [Live Demo](#-live-demo)
- [Features](#-features)
- [Technologies Used](#-technologies-used)
- [Quick Start](#-quick-start)
- [How It Works](#-how-it-works)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## 🚀 Live Demo

**[Click here to see a preview!](https://posturizer.streamlit.app/)**

---

## ✨ Features

- **Live Posture Detection**: Utilizes your webcam to analyze your posture in real-time, frame by frame.
- **Instant Visual Feedback**: Your posture status—either "GOOD" or "SLOUCHING"—is displayed directly on the video feed for immediate correction.
- **Configurable Grace Period**: Customize the delay (in seconds) before the app alerts you to poor posture, preventing false alarms from momentary adjustments.
- **Adjustable Sensitivity**: Fine-tune the detection algorithm's sensitivity to match your specific body type, camera angle, and seating arrangement.
- **Cross-Platform Web Interface**: Built with Streamlit, the application is accessible from any modern web browser on any operating system.
- **Privacy-Focused**: All video processing happens in the browser; your camera feed is never stored or sent to a server.

---

## 🛠️ Technologies Used

- **Backend**: Python
- **Web Framework**: Streamlit
- **Computer Vision**: OpenCV for image processing.
- **Pose Estimation**: Google MediaPipe for detecting 33 distinct body landmarks.
- **Real-time Video Streaming**: `streamlit-webrtc` to handle live webcam feeds securely.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- A webcam connected to your device.

### Installation and Launch

1.  **Clone the repository**:
    ```bash
    git clone [https://github.com/your-username/AI-Posture-Corrector.git](https://github.com/your-username/AI-Posture-Corrector.git)
    cd AI-Posture-Corrector
    ```

2.  **Install Dependencies**:
    A `requirements.txt` file is included to manage all necessary packages.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Streamlit App**:
    ```bash
    streamlit run streamlit_app.py
    ```

4.  **Access the App**: Open your browser to the local URL provided (usually `http://localhost:8501`) and click **START** to begin the live feed.

---

## 📊 How It Works

The application follows a three-step process to deliver real-time feedback:

1.  **Live Video Stream**: The app uses the `streamlit-webrtc` library to securely access your webcam feed directly within the browser. The video is streamed to the backend for processing without ever leaving your local network.

2.  **Pose Detection**: Each frame of the video is passed to Google's MediaPipe framework. This powerful AI model identifies 33 key body landmarks (like shoulders, elbows, and nose) in real-time.

3.  **Posture Analysis**: The core logic calculates the horizontal distance between your nose and the midpoint of your shoulders. If this distance falls below the configured sensitivity threshold, the algorithm determines you are slouching. A configurable grace period ensures that you are only alerted after maintaining this posture for a set amount of time.

4.  **Real-time Feedback**: The resulting posture status is overlaid onto the video feed, providing an immediate and intuitive visual cue to help you adjust and maintain a healthy posture.

---

## 🌐 Deployment

You can deploy this application to the web for free using Streamlit Cloud.

1.  **Fork this repository** to your personal GitHub account.
2.  **Visit** [share.streamlit.io](https://share.streamlit.io) and sign in with your GitHub account.
3.  Click "New app" and select your forked repository.
4.  Ensure the main file path is set to `streamlit_app.py`.
5.  **Important**: For successful deployment, you must have a `runtime.txt` file in your repository specifying `python-3.11` and a `packages.txt` file for system-level dependencies.

---

## 🐛 Troubleshooting

1.  **Camera Not Detected**:
    * Ensure you have granted camera permissions in your browser when prompted.
    * Check if another application (like Zoom or Skype) is currently using your camera.
    * Try refreshing the page or restarting your browser.

2.  **Laggy or Slow Video**:
    * A stable internet connection is recommended for the best experience.
    * Try reducing the lighting in your room, as bright lights can increase processing load.
    * Close other browser tabs or applications that may be consuming significant resources.

3.  **Deployment Issues on Streamlit Cloud**:
    * Double-check that your repository contains a `runtime.txt` file with `python-3.11` and a `packages.txt` file.
    * If the build fails, review the logs on Streamlit Cloud for specific package installation errors.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/your-username/AI-Posture-Corrector/issues).

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---

## 📄 License

This project is open source and distributed under the **MIT License**. See the `LICENSE` file for more information.

**(Note: You should add a `LICENSE` file to your repository containing the full text of the MIT License to make it official.)**

---

## 🙏 Acknowledgments

-   **MediaPipe**: For providing the cutting-edge pose detection model.
-   **Streamlit**: For making it incredibly easy to build and share data apps.
-   **OpenCV**: The foundational library for computer vision tasks.