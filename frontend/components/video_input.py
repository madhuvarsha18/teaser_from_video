import tempfile
from pathlib import Path
import streamlit as st
from backend import TARGET_AUDIENCES
from ..config import SUPPORTED_VIDEO_FORMATS, MAX_FILE_SIZE_MB
from ..utils import validate_youtube_url
from .common import render_brand
def handle_video_input():
    render_brand()
    st.markdown("<div class='section-title'>1. Provide your video</div>", unsafe_allow_html=True)
    left, right = st.columns([1.25, .75])
    with left:
        method = st.radio("Input method", ["Upload video", "Video URL"], horizontal=True)
        if method == "Upload video":
            uploaded = st.file_uploader("Drop a video here", type=SUPPORTED_VIDEO_FORMATS, help=f"Maximum {MAX_FILE_SIZE_MB} MB")
            if uploaded:
                video_bytes = uploaded.getvalue()
                col1, col2 = st.columns([1, 1.5])
                with col1:
                    st.video(video_bytes)
                with col2:
                    st.markdown(f"**{uploaded.name}**")
                    st.caption(f"{len(video_bytes) / (1024 * 1024):.2f} MB")
                if uploaded.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                    st.error(f"File exceeds {MAX_FILE_SIZE_MB} MB.")
                else:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded.name).suffix) as tmp:
                        tmp.write(uploaded.getvalue())
                        st.session_state.video_path = tmp.name
                    st.success(f"Loaded: {uploaded.name}")
        else:
            url = st.text_input("Video URL", placeholder="https://www.youtube.com/watch?v=...")
            if url:
                if validate_youtube_url(url):
                    st.session_state.video_path = url
                    st.success("Your Video URL accepted")
                else:
                    st.error("Enter a valid http(s) video URL.")
    with right:
        st.markdown("<div class='card'><h3>Supported</h3><div class='muted'>MP4, MOV, AVI, MKV</div><br><h3>What happens next?</h3><div class='muted small'>The pipeline detects scenes, transcribes speech, analyzes a representative frame, mathematically scores each clip, then asks Groq LLM to refine the selection for your chosen tone and target audience before assembling the teaser.</div></div>", unsafe_allow_html=True)
    if st.session_state.video_path:
        st.markdown("<div class='section-title'>2. Teaser preferences</div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            duration = st.selectbox("Target duration", [30, 45, 60, 90], index=0, format_func=lambda x: f"{x} seconds")
            st.session_state.duration = duration
        with c2:
            st.session_state.tone = st.selectbox("Style / tone", ["Cinematic", "Exciting", "Professional", "Emotional", "Compelling"])
        with c3:
            st.session_state.target_audience = st.selectbox(
                "Target audience",
                TARGET_AUDIENCES,
                index=TARGET_AUDIENCES.index("General") if "General" in TARGET_AUDIENCES else 0,
                help="Groq LLM tailors clip selection to this audience (e.g. Investor favors results/impact, Developer favors technical detail).",
            )
        with c4:
            st.session_state.add_subtitles = st.checkbox("Burn subtitles", value=True)
        if st.button("⚡ Analyze & Generate Teaser", type="primary", use_container_width=True):
            st.session_state.current_step = "processing"
            st.rerun()