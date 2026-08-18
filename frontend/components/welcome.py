import os
import streamlit as st
from .common import render_brand
def show_welcome():
    render_brand()
    if st.session_state.teaser_path and os.path.exists(str(st.session_state.teaser_path)):
        from .dashboard import show_dashboard
        show_dashboard()
        return
    cols = st.columns(4)
    features = [
        ("🤖", "AI Scene Understanding", "Whisper + vision analysis"),
        ("📊", "Math Scoring", "Speech, audio, keyword signals"),
        ("🧠", "Groq LLM Refinement", "Tone + audience-aware teaser"),
        ("⚡", "Fast Teaser Pipeline", "Automated clip selection"),
    ]
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(f"<div class='card'><div style='font-size:1.8rem'>{icon}</div><h3>{title}</h3><div class='muted small'>{desc}</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>How it works</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class='card'>
        <div class='timeline'>
        <div class='timeline-step done'><div class='dot'>✓</div><strong>Upload</strong><span>Video input</span></div>
        <div class='timeline-step done'><div class='dot'>✓</div><strong>Detect</strong><span>Find scenes</span></div>
        <div class='timeline-step done'><div class='dot'>✓</div><strong>Understand</strong><span>Audio + vision</span></div>
        <div class='timeline-step done'><div class='dot'>✓</div><strong>Score</strong><span>Math ranking</span></div>
        <div class='timeline-step done'><div class='dot'>✓</div><strong>Refine</strong><span>Groq LLM: tone + audience</span></div>
        <div class='timeline-step active'><div class='dot'>🤖</div><strong>Generate</strong><span>Build teaser</span></div>
        </div></div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🚀 Start Video Analysis", type="primary", use_container_width=True):
        st.session_state.current_step = "video_input"
        st.rerun()