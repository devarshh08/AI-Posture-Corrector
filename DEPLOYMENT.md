# 🚀 Streamlit Cloud Deployment Guide

## Quick Deployment Steps

### 1. Prerequisites
- Your code is already pushed to GitHub ✅
- You have a GitHub account ✅
- The repository is public or you have a Streamlit Cloud account that supports private repos

### 2. Deploy to Streamlit Cloud

1. **Visit Streamlit Cloud**: Go to [share.streamlit.io](https://share.streamlit.io)

2. **Sign in**: Sign in with your GitHub account

3. **New App**: Click "New app"

4. **Repository Selection**:
   - **Repository**: `devarshh08/AI-Posture-Corrector`
   - **Branch**: `main`
   - **Main file path**: `app.py` (recommended) or `streamlit_app.py`

5. **Deploy**: Click "Deploy!" and wait for the deployment to complete

### 3. Expected Deployment URL
Your app will be available at: `https://ai-posture-corrector-[random-id].streamlit.app`

## Configuration Files ✅

Multiple deployment options are available:

### Option 1: Minimal Version (Recommended)
- ✅ `app.py` - Simplified app with fallback analysis
- ✅ `requirements.txt` - Minimal dependencies (no MediaPipe)
- ✅ `angle.py` - Required utility module

### Option 2: Full MediaPipe Version
- ✅ `streamlit_app.py` - Full-featured app with MediaPipe
- ✅ `requirements-mediapipe.txt` - Full dependencies
- ✅ `angle.py` - Required utility module

## Dependencies Included

The `requirements.txt` includes all necessary packages:
```
streamlit>=1.28.0
opencv-python>=4.8.0
mediapipe>=0.10.0
numpy>=1.24.0
Pillow>=10.0.0
```

## App Features in Production

Once deployed, your Streamlit app will have:

- 🎥 **Camera Integration**: Users can take photos to analyze posture
- 🔊 **Browser Audio Alerts**: JavaScript-based beep notifications
- ⚙️ **Real-time Configuration**: Adjustable sensitivity and grace period
- 📊 **Live Metrics**: Distance measurements and posture status
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🎨 **Interactive UI**: Sidebar controls and status indicators

## Troubleshooting Deployment

### Common Issues

1. **MediaPipe Installation Fails**: 
   - Use `app.py` instead of `streamlit_app.py` for deployment
   - The minimal version works without MediaPipe
   - Falls back to basic computer vision analysis

2. **Build Fails**: 
   - Check that all files are committed and pushed
   - Try the minimal `requirements.txt` (without MediaPipe)
   - Verify Python version compatibility

3. **Import Errors**:
   - Switch to `app.py` which has graceful MediaPipe fallback
   - Use `requirements.txt` instead of `requirements-mediapipe.txt`
   - Check for version compatibility

4. **Camera Not Working**:
   - This is expected in the cloud version
   - Users will upload photos instead of live video
   - The app works with static image analysis

### Alternative Deployment Options

If Streamlit Cloud doesn't work:

1. **Heroku**: 
   - Add `setup.sh` and `Procfile`
   - Configure buildpacks for OpenCV

2. **Railway**:
   - Connect GitHub repository
   - Deploy with automatic builds

3. **Local Network**:
   ```bash
   streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=8501
   ```

## Post-Deployment Steps

After successful deployment:

1. **Test the App**: Visit the URL and verify all features work
2. **Update README**: Add the live deployment URL to your README
3. **Share**: Share the link with users
4. **Monitor**: Check Streamlit Cloud dashboard for usage stats

## App URL Management

Your app URL will be in the format:
- `https://[app-name]-[random-string].streamlit.app`

To get a custom URL:
- Use a custom domain (Streamlit Teams/Enterprise)
- Or use URL shorteners like bit.ly

## Success! 🎉

Your AI Posture Corrector is now live and accessible worldwide!

Users can:
- Access the app from any browser
- Monitor their posture in real-time
- Get audio feedback for slouching
- Adjust settings to their preference

---

**Need Help?** Check the [Streamlit Community Forum](https://discuss.streamlit.io) for deployment support.