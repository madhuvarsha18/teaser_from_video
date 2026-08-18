import streamlit as st
def render_brand():
    st.markdown(
        '<div class="hero"><div class="eyebrow">AI VIDEO INTELLIGENCE</div>'
        '<h1>SmartClip AI 🎬</h1>'
        '<p>Analyze scenes, rank teaser-worthy moments with math scoring, then let Groq LLM tailor '
        'the final teaser to your chosen tone and target audience, chat with your video using LLM</p></div>',
        unsafe_allow_html=True,
    )