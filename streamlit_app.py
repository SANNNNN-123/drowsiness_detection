import os
import cv2
import time
import streamlit as st
from drowsy_detection import VideoFrameHandler

# Initialize VideoFrameHandler
video_handler = VideoFrameHandler()

# Create sliders for parameters
st.title("Drowsiness Detection 🥱😪😴")
with st.container():
    c1, c2 = st.columns(2)
    with c1:
        WAIT_TIME = st.slider("Seconds to wait before sounding alarm:", 0.0, 5.0, 1.0, 0.25)
    with c2:
        EAR_THRESH = st.slider("Eye Aspect Ratio threshold:", 0.0, 0.4, 0.18, 0.01)

thresholds = {
    "EAR_THRESH": EAR_THRESH,
    "WAIT_TIME": WAIT_TIME,
}

# Initialize webcam with error handling
try:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Could not access webcam. Please check your camera settings.")
        st.info("Note: This app requires camera access to work.")
        st.stop()
except Exception as e:
    st.error(f"Error accessing webcam: {str(e)}")
    st.info("Note: This app requires camera access to work.")
    st.stop()

# Set camera properties
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Create a placeholder for the video feed
video_placeholder = st.empty()

# Create status indicators
status_container = st.container()
with status_container:
    status_text = st.empty()
    alert_text = st.empty()

# Create a stop button
stop_button = st.button("Stop")

while cap.isOpened() and not stop_button:
    ret, frame = cap.read()
    if not ret:
        st.error("Failed to capture video frame")
        break

    # Process frame for drowsiness detection
    frame, play_alarm = video_handler.process(frame, thresholds)

    # Update status instead of playing sound
    if play_alarm:
        alert_text.warning("⚠️ WAKE UP! WAKE UP! ⚠️")
        status_text.error("Drowsiness Detected!")
    else:
        alert_text.empty()
        status_text.success("Alert and Monitoring...")

    # Convert BGR to RGB for Streamlit
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Display the frame
    video_placeholder.image(frame, channels="RGB", use_container_width=True)

    # Add a small delay to control frame rate
    time.sleep(0.033)  # Approximately 30 FPS

# Release resources when stopped
cap.release()

st.write("Video capture stopped")

# Add deployment note
st.markdown("""
---
### Note for Local Deployment
To enable audio alerts:
1. Download the code from the repository
2. Install the required dependencies
3. Run locally using `streamlit run streamlit_app.py`

The audio alerts are disabled in the cloud deployment due to hardware limitations.
""")

