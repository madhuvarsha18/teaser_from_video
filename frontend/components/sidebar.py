import streamlit as st
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🎬 SmartClip AI")
        st.divider()
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.current_step = "welcome"
            st.rerun()
        if st.button("🎞 Analyze / Generate", use_container_width=True):
            st.session_state.current_step = "video_input"
            st.rerun()
        if st.session_state.analysis:
            if st.button("🧠 Clip Intelligence", use_container_width=True):
                st.session_state.current_step = "output"
                st.rerun()
        st.divider()
        st.markdown("**Pipeline**")
        for label in ["Upload", "Scene Detection", "Whisper", "Vision AI", "Math Scoring", "Groq LLM Refine", "Teaser"]:
            st.markdown(f"<div class='small muted'>• {label}</div>", unsafe_allow_html=True)