import html
import os
import streamlit as st
from ..state import load_analysis
from ..utils import fmt_time, normalized_scores
from .common import render_brand
from .clip_explorer import render_clip_explorer
from .chatbot import render_chatbot
from .downloads import show_downloads
def render_metrics(analysis, selected):
    total_duration = max([float(c.get("end_time", 0)) for c in analysis], default=0)
    scores = [normalized_scores(c, analysis)["overall"] for c in selected or analysis]
    avg_score = round(sum(scores) / len(scores)) if scores else 0
    metrics = [
        (fmt_time(total_duration), "Analyzed duration"),
        (str(len(analysis)), "Scenes / clips"),
        (str(len(selected)), "Selected clips"),
        (f"{avg_score}%", "Avg confidence"),
    ]
    cols = st.columns(4)
    for col, (value, label) in zip(cols, metrics):
        with col:
            st.markdown(f"<div class='metric'><div class='value'>{value}</div><div class='label'>{label}</div></div>", unsafe_allow_html=True)
def render_processing_summary():
    if not st.session_state.processing_log:
        return
    st.markdown("<div class='section-title'>Processing summary</div>", unsafe_allow_html=True)
    cols = st.columns(len(st.session_state.processing_log))
    for col, item in zip(cols, st.session_state.processing_log):
        with col:
            st.markdown(f"<div class='card small'>{html.escape(item)}</div>", unsafe_allow_html=True)
def render_llm_selection_reasoning():
    reasoning = st.session_state.get("selection_reasoning")
    if not reasoning:
        return
    st.markdown("<div class='section-title'>🧠 Why this teaser (Groq LLM)</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='card'><div class='llm-why'>"
        f"<b>Tone:</b> {html.escape(str(st.session_state.tone))} &nbsp;|&nbsp; "
        f"<b>Audience:</b> {html.escape(str(st.session_state.target_audience))}"
        f"<br><br>{html.escape(str(reasoning))}"
        f"<br><br><span class='muted small'>Clips are always kept in original chronological order regardless of tone/audience.</span>"
        f"</div></div>",
        unsafe_allow_html=True,
    )
def render_clip_grid(analysis, selected):
    st.markdown("<div class='section-title'>🏆 Top teaser clips</div>", unsafe_allow_html=True)
    clips = selected or sorted(analysis, key=lambda c: c.get("score_hint", 0), reverse=True)[:8]
    for start in range(0, len(clips), 4):
        row = clips[start:start + 4]
        cols = st.columns(len(row))
        for col, clip in zip(cols, row):
            scores = normalized_scores(clip, analysis)
            with col:
                st.markdown(
                    f"""<div class='clip-card'>
                    <div class='clip-title'><strong>Clip #{clip.get('clip_id')}</strong><span class='pill good'>SELECTED</span></div>
                    <div class='muted small'>{fmt_time(clip.get('start_time'))} → {fmt_time(clip.get('end_time'))}</div>
                    <div class='score'>{scores['overall']}%</div>
                    <div class='bar'><div style='width:{scores['overall']}%'></div></div>
                    <div class='small'><b>Hook</b> {scores['hook']}% &nbsp; <b>Emotion</b> {scores['emotion']}%</div>
                    <div class='muted small' style='margin-top:.55rem'>{html.escape(str(clip.get('transcript',''))[:130])}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
def show_dashboard():
    analysis = load_analysis()
    selected = st.session_state.selected or []
    render_brand()
    st.markdown("<div class='section-title'>📈 Video overview</div>", unsafe_allow_html=True)
    render_metrics(analysis, selected)
    if st.session_state.teaser_path and os.path.exists(str(st.session_state.teaser_path)):
        left, right = st.columns([1.25, .75])
        with left:
            st.markdown("<div class='card'><h3>🎬 Generated teaser</h3>", unsafe_allow_html=True)
            st.video(st.session_state.teaser_path)
            st.markdown("</div>", unsafe_allow_html=True)
        with right:
            st.markdown("<div class='card'><h3>🧾 AI summary</h3><div class='muted small'>Generated from the current video analysis.</div>", unsafe_allow_html=True)
            if analysis:
                top = max(analysis, key=lambda c: c.get("score_hint", 0))
                st.write(f"The analysis found **{len(analysis)} scene clips** and selected **{len(selected)} highlights** for tone **{st.session_state.tone}** / audience **{st.session_state.target_audience}**. The highest math-ranked clip is **#{top.get('clip_id')}** at {normalized_scores(top, analysis)['overall']}% confidence.")
                st.write(f"**Top visual:** {top.get('visual_caption', 'Not available')}")
                st.write(f"**Top dialogue:** {top.get('transcript', 'No speech detected.')}")
            st.markdown("</div>", unsafe_allow_html=True)
    render_llm_selection_reasoning()
    render_processing_summary()
    render_clip_grid(analysis, selected)
    tab1, tab2, tab3 = st.tabs(["🔍 Clip Intelligence", "🤖 AI Assistant", "📦 Downloads"])
    with tab1:
        render_clip_explorer(analysis, selected)
    with tab2:
        render_chatbot(analysis)
    with tab3:
        show_downloads()