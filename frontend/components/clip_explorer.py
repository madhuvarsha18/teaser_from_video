import html
import streamlit as st
from ..utils import fmt_time, normalized_scores, clip_reason
def render_clip_explorer(analysis, selected):
    st.markdown("<div class='section-title'>🔍 Clip intelligence</div>", unsafe_allow_html=True)
    if not analysis:
        st.info("No analysis available yet.")
        return
    ids = [c.get("clip_id") for c in analysis]
    chosen_id = st.selectbox("Choose a clip", ids, format_func=lambda x: f"Clip #{x}")
    clip = next(c for c in analysis if c.get("clip_id") == chosen_id)
    scores = normalized_scores(clip, analysis)
    is_selected = any(c.get("clip_id") == chosen_id for c in selected)
    left, right = st.columns([1.2, .8])
    with left:
        st.markdown("<div class='card'><h3>🎞 Clip overview</h3>", unsafe_allow_html=True)
        st.write(f"**Time:** {fmt_time(clip.get('start_time'))} → {fmt_time(clip.get('end_time'))}")
        st.write(f"**Duration:** {float(clip.get('duration', 0)):.1f}s")
        st.write(f"**Status:** {'⭐ Selected for teaser' if is_selected else 'Not selected'}")
        st.markdown("**🎙 Transcript**")
        st.info(str(clip.get("transcript", "No speech detected.")))
        st.markdown("**👁 Visual analysis**")
        st.write(str(clip.get("visual_caption", "No visual context")))
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='card'><h3>📊 Confidence breakdown</h3>", unsafe_allow_html=True)
        for label, key in [("Overall", "overall"), ("Hook strength", "hook"), ("Emotional impact", "emotion"), ("Visual clarity", "visual"), ("Narrative relevance", "relevance")]:
            value = scores[key]
            st.write(f"**{label}** — {value}%")
            st.progress(value / 100)
        st.markdown(f"<div class='why'><b>💡 Why this clip?</b><br>{html.escape(clip_reason(clip, scores))}<br><br><span class='muted small'>This is an explainability score derived from the current analysis signals; it is not a calibrated probability.</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)