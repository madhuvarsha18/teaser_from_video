import streamlit as st
from frontend.state import init_session_state
from frontend.styles import inject_css
from frontend.components.sidebar import render_sidebar
from frontend.components.welcome import show_welcome
from frontend.components.video_input import handle_video_input
from frontend.components.processing import process_video
from frontend.components.dashboard import show_dashboard
st.set_page_config(
    page_title="SmartClipAI — AI Video Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)
def main():
    init_session_state()
    inject_css()
    render_sidebar()
    if st.session_state.current_step == "welcome":
        show_welcome()
    elif st.session_state.current_step == "video_input":
        handle_video_input()
    elif st.session_state.current_step == "processing":
        process_video()
    elif st.session_state.current_step == "output":
        show_dashboard()
if __name__ == "__main__":
    main()
