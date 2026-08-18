import json
from pathlib import Path
import streamlit as st
def init_session_state():
    defaults = {
        "current_step": "welcome",
        "video_path": None,
        "duration": 30,
        "tone": "Cinematic",
        "target_audience": "General",
        "teaser_path": None,
        "caption": None,
        "add_subtitles": True,
        "add_music": False,
        "analysis": None,
        "selected": [],
        "selection_reasoning": "",
        "processing_log": [],
        "processing_started": None,
        "processing_finished": None,
        "chat_history": [],
        "last_query": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
def load_analysis():
    if st.session_state.analysis is not None:
        return st.session_state.analysis
    path = Path("video_analysis.json")
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                st.session_state.analysis = json.load(f)
            return st.session_state.analysis
        except Exception:
            return []
    return []
