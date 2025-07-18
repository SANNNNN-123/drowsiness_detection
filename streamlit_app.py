import os
import cv2
import time
import streamlit as st
from drowsy_detection import VideoFrameHandler
from pygame import mixer
import pygame

# Initialize Pygame mixer with proper settings
try:
    pygame.init()
    mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
    alarm_sound = mixer.Sound("audio/wake_up.wav")
    st.success("Audio system initialized successfully!")
except Exception as e:
    st.error(f"Error initializing audio system: {str(e)}")
    alarm_sound = None

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

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Create a placeholder for the video feed
video_placeholder = st.empty()

# Create a stop button
stop_button = st.button("Stop")

# Add volume control
volume = st.slider("Alarm Volume", 0.0, 1.0, 0.5, 0.1)
if alarm_sound:
    alarm_sound.set_volume(volume)

while cap.isOpened() and not stop_button:
    ret, frame = cap.read()
    if not ret:
        st.error("Failed to capture video frame")
        break

    # Process frame for drowsiness detection
    frame, play_alarm = video_handler.process(frame, thresholds)

    # Play alarm if needed and if audio is available
    if play_alarm and alarm_sound:
        if not mixer.get_busy():  # Only play if not already playing
            try:
                alarm_sound.play()
            except Exception as e:
                st.error(f"Error playing alarm: {str(e)}")
    elif not play_alarm and alarm_sound:
        alarm_sound.stop()

    # Convert BGR to RGB for Streamlit
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Display the frame
    video_placeholder.image(frame, channels="RGB", use_container_width=True)

    # Add a small delay to control frame rate
    time.sleep(0.033)  # Approximately 30 FPS

# Release resources when stopped
cap.release()
if alarm_sound:
    alarm_sound.stop()
    mixer.quit()
pygame.quit()

st.write("Video capture stopped")

