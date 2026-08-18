"""
Headless CLI runner for the pipeline, independent of the Streamlit UI.

Usage:
    python -m backend.cli
"""
import json
from pathlib import Path
from .video_io import download_video
from .scene_detection import chunk_video
from .clip_analysis import analyze_all_clips
from .selection import select_clips
from .teaser_builder import create_final_teaser
def main(tone="Cinematic", target_audience="General", target_length=40):
    video_source = "https://youtu.be/Pv0iVoSZzN8?feature=shared"
    video_path = download_video(video_source)
    chunks = chunk_video(video_path)
    metadata = analyze_all_clips(chunks, video_path)
    with open("video_analysis.json","w") as f: json.dump(metadata,f,indent=2)
    selected, reasoning = select_clips(
        metadata, tone=tone, target_audience=target_audience, target_length=target_length
    )
    print("🧠 LLM selection reasoning:", reasoning)
    if not selected:
        print("⚠️ No clips selected. Falling back.")
        selected = metadata[:2]
    teaser = create_final_teaser(video_path, selected, target_length=target_length, all_metadata=metadata)
    print("✅ Teaser ready:", teaser)
    srt_path = Path("teaser.srt")
    analysis_path = Path("video_analysis.json")
    return {
        "teaser_path": str(teaser),
        "srt_path": str(srt_path),
        "analysis_path": str(analysis_path),
        "reasoning": reasoning,
    }
if __name__ == "__main__":
    main()