import os
from dotenv import load_dotenv
load_dotenv()
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_API_URL = os.getenv("SARVAM_API_URL")

import streamlit as st
from components.sidebar import sidebar
from components.assistant import render_assistant
from services.realtime import start_realtime_processing
from components.transcript import TranscriptDisplay

def main():
    st.title("Real-Time Call Centre Assistant")
    
    sidebar()
    
    if "transcript_display" not in st.session_state:
        st.session_state.transcript_display = TranscriptDisplay()
    
    st.subheader("Call Audio")
    audio_value = st.audio_input("Record a voice message", key="audio_recorder")
    
    if audio_value is not None:
        st.success("Audio captured! Processing...")
        if "transcript_display" in st.session_state:
            st.session_state.transcript_display.add_to_transcript("Processing new audio input...")
    
    if st.button("Start Call", key="start_call_button"):
        st.session_state.transcript_display.clear_transcript()
        start_realtime_processing()
    
    st.session_state.transcript_display.display_transcript()
    
    render_assistant()
    
if __name__ == "__main__":
    main()