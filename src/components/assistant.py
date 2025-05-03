from streamlit import session_state as st_session
import streamlit as st

class Assistant:
    def __init__(self):
        self.suggestions = []
        self.relevant_info = ""

    def update_suggestions(self, new_suggestions):
        self.suggestions = new_suggestions

    def display_suggestions(self):
        if self.suggestions:
            st.sidebar.header("Suggestions")
            for suggestion in self.suggestions:
                st.sidebar.write(f"- {suggestion}")

    def update_relevant_info(self, info):
        self.relevant_info = info

    def display_relevant_info(self):
        if self.relevant_info:
            st.sidebar.header("Relevant Information")
            st.sidebar.write(self.relevant_info)

def initialize_assistant():
    if 'assistant' not in st_session:
        st_session.assistant = Assistant()

def render_assistant():
    initialize_assistant()
    assistant = st_session.assistant
    assistant.display_suggestions()
    assistant.display_relevant_info()