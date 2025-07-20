import os
import av
import threading
import streamlit as st
import streamlit_nested_layout
from streamlit_webrtc import VideoHTMLAttributes, webrtc_streamer

from audio_handling import AudioFrameHandler
from drowsy_detection import VideoFrameHandler

# Initialize session state
if 'drowsiness_detection_state' not in st.session_state:
    st.session_state['drowsiness_detection_state'] = {
        'start_time': None,
        'drowsy_time': 0.0,
        'is_active': False
    }

# Define the audio file to use.
alarm_file_path = os.path.join("audio", "wake_up.wav")

# Streamlit Components
st.set_page_config(
    page_title="Drowsiness Detection | LearnOpenCV",
    page_icon="https://learnopencv.com/wp-content/uploads/2017/12/favicon.png",
    layout="wide",  # centered, wide
    initial_sidebar_state="expanded",
    menu_items={
        "About": "### Visit www.learnopencv.com for more exciting tutorials!!!",
    },
)

col1, col2 = st.columns(spec=[6, 2], gap="medium")

with col1:
    st.title("Drowsiness Detection!!!🥱😪😴")
    with st.container():
        c1, c2 = st.columns(spec=[1, 1])
        with c1:
            # The amount of time (in seconds) to wait before sounding the alarm.
            WAIT_TIME = st.slider("Seconds to wait before sounding alarm:", 0.0, 5.0, 1.0, 0.25)

        with c2:
            # Lowest valid value of Eye Aspect Ratio. Ideal values [0.15, 0.2].
            EAR_THRESH = st.slider("Eye Aspect Ratio threshold:", 0.0, 0.4, 0.18, 0.01)

thresholds = {
    "EAR_THRESH": EAR_THRESH,
    "WAIT_TIME": WAIT_TIME,
}

# For streamlit-webrtc
video_handler = VideoFrameHandler()
audio_handler = AudioFrameHandler(sound_file_path=alarm_file_path)

lock = threading.Lock()  # For thread-safe access & to prevent race-condition.
shared_state = {"play_alarm": False}

def video_frame_callback(frame: av.VideoFrame):
    frame = frame.to_ndarray(format="bgr24")  # Decode and convert frame to RGB

    frame, play_alarm = video_handler.process(frame, thresholds)  # Process frame
    with lock:
        shared_state["play_alarm"] = play_alarm  # Update shared state

    return av.VideoFrame.from_ndarray(frame, format="bgr24")  # Encode and return BGR frame

def audio_frame_callback(frame: av.AudioFrame):
    with lock:  # access the current "play_alarm" state
        play_alarm = shared_state["play_alarm"]

    new_frame: av.AudioFrame = audio_handler.process(frame, play_sound=play_alarm)
    return new_frame

with col1:
    try:
        ctx = webrtc_streamer(
            key="drowsiness-detection",
            video_frame_callback=video_frame_callback,
            audio_frame_callback=audio_frame_callback,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={"video": {"height": {"ideal": 480}}, "audio": True},
            video_html_attrs=VideoHTMLAttributes(autoPlay=True, controls=False, muted=False),
        )
        
        # Update session state based on WebRTC context
        if ctx.state.playing:
            st.session_state.drowsiness_detection_state['is_active'] = True
        else:
            st.session_state.drowsiness_detection_state['is_active'] = False
            
    except Exception as e:
        st.error(f"Error initializing video stream: {str(e)}")
        if ctx is not None and ctx.video_transformer:
            ctx.video_transformer.close()

