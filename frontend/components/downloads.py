import os
from pathlib import Path
import streamlit as st
from backend import extract_audio
def show_downloads():
    st.markdown("<div class='section-title'>📦 Export</div>", unsafe_allow_html=True)
    if st.session_state.teaser_path and os.path.exists(str(st.session_state.teaser_path)):
        with open(st.session_state.teaser_path, "rb") as f:
            st.download_button("⬇️ Download teaser MP4", f, file_name="ai_teaser.mp4", mime="video/mp4", use_container_width=True)
        audio = extract_audio(st.session_state.teaser_path)
        if audio and os.path.exists(audio):
            with open(audio, "rb") as f:
                st.download_button("🎵 Download teaser audio", f, file_name="teaser_audio.mp3", mime="audio/mpeg", use_container_width=True)
    if Path("video_analysis.json").exists():
        with open("video_analysis.json", "rb") as f:
            st.download_button("📄 Download analysis JSON", f, file_name="video_analysis.json", mime="application/json", use_container_width=True)
    if Path("teaser.srt").exists():
        with open("teaser.srt", "rb") as f:
            st.download_button("📝 Download subtitles SRT", f, file_name="teaser.srt", mime="text/plain", use_container_width=True)