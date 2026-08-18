import json
import time
import streamlit as st
from backend import (
    analyze_all_clips,
    chunk_video,
    create_final_teaser,
    download_video,
    select_clips,
)
from .common import render_brand
def processing_timeline(active=0):
    steps = [
        ("Upload", "Input ready"),
        ("Scene Detection", "Finding shots"),
        ("Whisper", "Transcribing speech"),
        ("Vision AI", "Reading visuals"),
        ("Math Scoring", "Ranking clips"),
        ("Groq LLM Refine", "Tone + audience fit"),
        ("Teaser", "Assembling output"),
    ]
    items = []
    for i, (name, detail) in enumerate(steps):
        cls = "done" if i < active else "active" if i == active else ""
        icon = "✓" if i < active else "•" if i == active else str(i + 1)
        items.append(f"<div class='timeline-step {cls}'><div class='dot'>{icon}</div><strong>{name}</strong><span>{detail}</span></div>")
    st.markdown("<div class='card'><div class='timeline'>" + "".join(items) + "</div></div>", unsafe_allow_html=True)
def process_video():
    render_brand()
    st.markdown("<div class='section-title'>AI processing pipeline</div>", unsafe_allow_html=True)
    processing_timeline(0)
    progress = st.progress(0)
    status = st.empty()
    started = time.perf_counter()
    st.session_state.processing_started = time.time()
    try:
        status.info("Preparing video input...")
        video_path = download_video(st.session_state.video_path)
        progress.progress(10)
        processing_timeline(1)
        status.info("Detecting scenes...")
        chunks = chunk_video(video_path)
        progress.progress(22)
        processing_timeline(2)
        status.info(f"Analyzing {len(chunks)} clips with Whisper and Vision AI...")
        metadata = analyze_all_clips(chunks, video_path)
        progress.progress(55)
        processing_timeline(4)
        with open("video_analysis.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        st.session_state.analysis = metadata
        status.info(
            f"Asking Groq LLM to tailor clips for tone='{st.session_state.tone}', "
            f"audience='{st.session_state.target_audience}'..."
        )
        selected, reasoning = select_clips(
            metadata,
            tone=st.session_state.tone,
            target_audience=st.session_state.target_audience,
            target_length=st.session_state.duration,
        ) if metadata else ([], "No clips detected.")
        st.session_state.selected = selected
        st.session_state.selection_reasoning = reasoning
        progress.progress(80)
        processing_timeline(6)
        status.info("Assembling the teaser...")
        teaser = create_final_teaser(
            video_path,
            selected or metadata[:2],
            add_subtitles=st.session_state.add_subtitles,
            target_length=st.session_state.duration,
            all_metadata=metadata,
        )
        st.session_state.teaser_path = str(teaser)
        st.session_state.analysis_path = "video_analysis.json"
        st.session_state.srt_path = "teaser.srt"
        progress.progress(100)
        processing_timeline(7)
        elapsed = time.perf_counter() - started
        st.session_state.processing_finished = time.time()
        st.session_state.processing_log = [
            f"{len(chunks)} scenes detected",
            f"{len(metadata)} clips analyzed",
            f"{len(selected)} clips selected ({st.session_state.tone} / {st.session_state.target_audience})",
            f"Completed in {elapsed:.1f}s",
        ]
        status.success(f"Teaser ready in {elapsed:.1f} seconds")
        time.sleep(.5)
        st.session_state.current_step = "output"
        st.rerun()
    except Exception as exc:
        status.error(f"Processing failed: {exc}")
        st.exception(exc)
        if st.button("Back to video input"):
            st.session_state.current_step = "video_input"
            st.rerun()