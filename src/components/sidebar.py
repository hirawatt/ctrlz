# sidebar.py

import streamlit as st

def sidebar():
    st.sidebar.title("Call Centre Assistant Settings")
    
    # User preferences
    st.sidebar.header("User Preferences")
    language = st.sidebar.selectbox("Select Language", ["English", "Spanish", "French"])
    st.sidebar.write("Selected Language:", language)

    # Audio settings
    st.sidebar.header("Audio Settings")
    audio_quality = st.sidebar.select_slider("Audio Quality", options=["Low", "Medium", "High"], value="Medium")
    st.sidebar.write("Selected Audio Quality:", audio_quality)

    # Action buttons
    if st.sidebar.button("Start Call"):
        st.sidebar.success("Call started!")
    
    if st.sidebar.button("End Call"):
        st.sidebar.warning("Call ended!")