import streamlit as st
import threading
import time
import numpy as np
from mic_capture import MicrophoneCapture
from transcriber import RealtimeTranscriber
import queue

if "recording" not in st.session_state:
    st.session_state.recording = False
if "full_transcript" not in st.session_state:
    st.session_state.full_transcript = ""
if "stop_signal_queue" not in st.session_state:
    st.session_state.stop_signal_queue = queue.Queue()
if "text_update_queue" not in st.session_state:
    st.session_state.text_update_queue = queue.Queue()

def start_recording(device_index, model_size, stop_signal_queue, text_update_queue):
    mic = None
    transcriber = None
    try:
        mic = MicrophoneCapture(device=device_index, chunk_size=1024)
        mic.start_stream()
        actual_sample_rate = mic.get_sample_rate()
        transcriber = RealtimeTranscriber(
            model_size=model_size,
            sample_rate=actual_sample_rate
        )
        transcriber.start()

        recording_active = True
        while recording_active:
            try:
                if not stop_signal_queue.empty():
                    stop_signal_queue.get(block=False)
                    recording_active = False
                    continue
            except queue.Empty:
                pass

            audio_chunk = mic.get_audio_chunk(timeout=0.1)
            if audio_chunk is not None and np.abs(audio_chunk).mean() > 10:
                transcriber.add_audio(audio_chunk)

            text = transcriber.get_transcription()
            if text:
                text_update_queue.put(text)

            time.sleep(0.05)

    except Exception as e:
        text_update_queue.put(f"Error: {e}")
    finally:
        if mic:
            mic.close()
        if transcriber:
            transcriber.stop()
        text_update_queue.put(None)

def main():
    st.title("Real-Time Voice Transcription")

    model_size = st.selectbox(
        "Select model size",
        options=["tiny", "base", "small"],
        index=1,
        key="model_select"
    )

    try:
        mic_lister = MicrophoneCapture()
        device_list = mic_lister.get_device_list()
        if not device_list:
            device_list = ["Default device"]
    except Exception as e:
        device_list = ["Default device"]

    selected_device_str = st.selectbox(
        "Select microphone device",
        options=device_list,
        index=0,
        key="device_select"
    )

    device_index = None
    if ":" in selected_device_str:
        try:
            device_index = int(selected_device_str.split(":")[0])
        except ValueError:
            device_index = None

    col1, col2 = st.columns(2)

    if col1.button("Start Recording", key="start_button", disabled=st.session_state.recording):
        st.session_state.recording = True
        st.session_state.full_transcript = ""

        while not st.session_state.stop_signal_queue.empty():
            st.session_state.stop_signal_queue.get()
        while not st.session_state.text_update_queue.empty():
            st.session_state.text_update_queue.get()

        threading.Thread(
            target=start_recording,
            args=(
                device_index,
                model_size,
                st.session_state.stop_signal_queue,
                st.session_state.text_update_queue,
            ),
            daemon=True
        ).start()
        st.rerun()

    if col2.button("Stop Recording", key="stop_button", disabled=not st.session_state.recording):
        st.session_state.stop_signal_queue.put(True)
        st.session_state.recording = False
        time.sleep(0.5)
        st.rerun()

    new_text_received = False
    while not st.session_state.text_update_queue.empty():
        try:
            text_item = st.session_state.text_update_queue.get(block=False)
            if text_item is None:
                if st.session_state.recording:
                     st.session_state.recording = False
                continue

            if isinstance(text_item, str):
                st.session_state.full_transcript += text_item + " "
                new_text_received = True

        except queue.Empty:
            break

    if st.session_state.recording:
        st.markdown("🔴 **Recording in progress...**")
    elif not st.session_state.recording and st.session_state.full_transcript:
         st.markdown("⚪ **Recording stopped.**")

    st.text_area(
        "Transcription",
        value=st.session_state.full_transcript,
        height=300,
        key="transcript_area"
    )

    if st.session_state.recording:
        time.sleep(0.2)
        st.rerun()

if __name__ == "__main__":
    main()