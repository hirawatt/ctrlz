import streamlit as st

class TranscriptDisplay:
    def __init__(self):
        self.transcript = []

    def add_to_transcript(self, text):
        self.transcript.append(text)

    def clear_transcript(self):
        self.transcript = []

    def display_transcript(self):
        if self.transcript:
            st.subheader("Live Call Transcript")
            for line in self.transcript:
                st.write(line)
        else:
            st.write("No transcript available.")