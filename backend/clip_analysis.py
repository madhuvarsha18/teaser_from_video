import os
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
import soundfile as sf
import numpy as np
from .config import DEVICE, CLIP_ANALYSIS_WORKERS, EMOTIONAL_KEYWORDS
from .models import whisper_model, blip_processor, blip_model
from .video_io import _video_has_audio
def analyze_all_clips(chunks, video_path):
    results = []
    max_workers = CLIP_ANALYSIS_WORKERS
    print(f"[Parallel] Using {max_workers} threads for clip analysis (device='{DEVICE}')...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(analyze_clip, cid, video_path, s, e) for cid, s, e in chunks]
        for fut in as_completed(futures):
            try:
                results.append(fut.result())
            except Exception as e:
                print("⚠️ Clip analysis failed:", e)
    results.sort(key=lambda x: x["start_time"])
    return results
def analyze_clip(clip_id, video_path, start, end):
    audio_path = f"temp_audio_{clip_id}.wav"
    audio_ok = False
    if not _video_has_audio(str(video_path)):
        transcript = ""
    else:
        audio_ok = True
        try:
            subprocess.run([
                "ffmpeg","-y","-ss",str(start),"-to",str(end),
                "-i",str(video_path),"-vn","-acodec","pcm_s16le",audio_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        except subprocess.CalledProcessError as e:
            # Source has audio overall, but extraction still failed for this
            # specific time range — could be a broken seek index on certain
            # ranges. Capture the real reason instead of failing silently.
            stderr_tail = (e.stderr or "").strip().splitlines()[-6:]
            print(f"⚠️ Clip {clip_id}: ffmpeg audio extraction failed (exit {e.returncode}). "
                  f"Last ffmpeg output lines:\n    " + "\n    ".join(stderr_tail))
            audio_ok = False
        if audio_ok and not Path(audio_path).exists():
            print(f"⚠️ Clip {clip_id}: ffmpeg reported success but produced no audio file — treating as failed.")
            audio_ok = False
        if audio_ok:
            segments, _ = whisper_model.transcribe(audio_path, beam_size=1)
            transcript = " ".join([seg.text for seg in segments]).strip()
        else:
            transcript = ""
    n_words = len(transcript.split())
    speech_density = n_words / max(1e-6, end - start)
    rms = 0.0
    if audio_ok:
        try:
            data, sr = sf.read(audio_path, dtype="float32")
            if data.ndim > 1: data = data.mean(axis=1)
            rms = float(np.sqrt((data**2).mean()))
        except Exception:
            rms = 0.0
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)
    mid_time = (start + end)/2
    frame_path = f"frame_{clip_id}.jpg"
    subprocess.run([
        "ffmpeg","-y","-ss",str(mid_time),"-i",str(video_path),
        "-vframes","1",frame_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    caption = "No visual context"
    if Path(frame_path).exists():
        frame = Image.open(frame_path)
        inputs = blip_processor(images=frame, return_tensors="pt").to(DEVICE)
        out = blip_model.generate(**inputs, max_new_tokens=30)
        caption = blip_processor.decode(out[0], skip_special_tokens=True)
        os.remove(frame_path)
    keyword_boost = sum(0.5 for kw in EMOTIONAL_KEYWORDS if kw in transcript.lower())
    pause_factor = 0.0
    if n_words < 5 and (end - start) > 5:
        pause_factor = 0.3
    score_hint = (
        0.5 * speech_density +
        0.4 * rms +
        0.1 * (len(caption.split())/10) +
        keyword_boost +
        pause_factor
    )
    return {
        "clip_id": clip_id,
        "start_time": start,
        "end_time": end,
        "duration": end - start,
        "transcript": transcript or "No speech detected.",
        "visual_caption": caption,
        "speech_density": speech_density,
        "audio_energy": rms,
        "score_hint": score_hint,
    }