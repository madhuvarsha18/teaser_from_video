import subprocess
from pathlib import Path
from .config import MAX_TEASER_CLIP_LENGTH, MAX_OUTPUT_DIMENSION, BGM_PATH
from .models import whisper_model
from .video_io import _video_has_audio
def format_srt_time(t: float) -> str:
    h = int(t//3600); m = int((t%3600)//60); s = int(t%60); ms = int((t-int(t))*1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
def _cap_and_fit(clip, remaining_budget):
    c = dict(clip)
    d = min(c["duration"], MAX_TEASER_CLIP_LENGTH, remaining_budget)
    c["end_time"] = c["start_time"] + d
    c["duration"] = d
    return c
def create_final_teaser(video_path: Path, selected_clips, target_length=30, add_subtitles=True, all_metadata=None):
    """
    Assemble the teaser so the FINAL duration matches target_length as
    closely as possible (previously it could fall noticeably short —
    see notes below). Two fixes vs. the old version:
      1. Instead of skipping a clip that doesn't fully fit in the
         remaining time budget, it is now TRIMMED to fill exactly
         what's left (still capped at MAX_TEASER_CLIP_LENGTH per clip),
         so the loop keeps using up the requested duration.
      2. If the selected clips still don't add up to target_length
         (e.g. the LLM/candidate pool picked too few short clips),
         additional un-used, highest-scoring clips from `all_metadata`
         are pulled in — chronologically — to pad the teaser back up
         to what the user asked for.
    """
    base_teaser = Path("teaser_raw.mp4")
    srt_path = Path("teaser.srt")
    final_output = Path("teaser_final.mp4")
    total, pruned = 0.0, []
    used_ids = set()
    for clip in selected_clips:
        if total >= target_length:
            break
        remaining = target_length - total
        fitted = _cap_and_fit(clip, remaining)
        if fitted["duration"] <= 0:
            continue
        pruned.append(fitted)
        used_ids.add(fitted["clip_id"])
        total += fitted["duration"]
    if all_metadata and total < target_length - 0.5:
        leftover = [c for c in all_metadata if c["clip_id"] not in used_ids]
        leftover.sort(key=lambda x: x["score_hint"], reverse=True)
        for clip in leftover:
            if total >= target_length - 0.5:
                break
            remaining = target_length - total
            fitted = _cap_and_fit(clip, remaining)
            if fitted["duration"] <= 0:
                continue
            pruned.append(fitted)
            used_ids.add(fitted["clip_id"])
            total += fitted["duration"]
    if not pruned:
        pruned = [_cap_and_fit(selected_clips[0], target_length)] if selected_clips else []
    if not pruned:
        raise RuntimeError(
            "No usable clips were available to build the teaser. This usually means "
            "clip analysis failed for every scene (e.g. the source video has no audio "
            "track and/or scene detection produced no valid chunks). Check the console "
            "log above for '⚠️ Clip analysis failed' or '⚠️ no usable audio track' messages."
        )
    pruned.sort(key=lambda x: x["start_time"])
    print(f"🎯 Teaser assembled: {total:.1f}s of {target_length}s requested across {len(pruned)} clips.")
    has_audio = _video_has_audio(str(video_path))
    ffmpeg_cmd = ["ffmpeg","-y"]
    filter_parts = []
    for i, clip in enumerate(pruned):
        ffmpeg_cmd += ["-ss",str(clip["start_time"]),"-to",str(clip["end_time"]),"-i",str(video_path)]
        filter_parts.append(f"[{i}:v:0][{i}:a:0]" if has_audio else f"[{i}:v:0]")
    if has_audio:
        filter_complex = "".join(filter_parts) + f"concat=n={len(pruned)}:v=1:a=1[outv][outa]"
        ffmpeg_cmd += ["-filter_complex",filter_complex,"-map","[outv]","-map","[outa]",
                       "-c:v","libx264","-preset","veryfast","-crf","23","-c:a","aac","-b:a","128k",str(base_teaser)]
    else:
        print(f"ℹ️ Source has no audio track — building a video-only teaser with a silent audio track (duration {total:.1f}s).")
        filter_complex = "".join(filter_parts) + f"concat=n={len(pruned)}:v=1:a=0[outv]"
        silent_input_index = len(pruned)
        ffmpeg_cmd += ["-f","lavfi","-t",str(max(total, 0.5)),"-i","anullsrc=channel_layout=stereo:sample_rate=44100"]
        ffmpeg_cmd += ["-filter_complex",filter_complex,"-map","[outv]","-map",f"{silent_input_index}:a",
                       "-c:v","libx264","-preset","veryfast","-crf","23","-c:a","aac","-b:a","128k",
                       "-shortest",str(base_teaser)]
    subprocess.run(ffmpeg_cmd, check=True)
    segments, _ = whisper_model.transcribe(str(base_teaser), beam_size=1)
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            f.write(f"{i}\n")
            f.write(f"{format_srt_time(seg.start)} --> {format_srt_time(seg.end)}\n")
            f.write(seg.text.strip() + "\n\n")
    scale_expr = (
        f"scale='min({MAX_OUTPUT_DIMENSION},iw)':'min({MAX_OUTPUT_DIMENSION},ih)'"
        f":force_original_aspect_ratio=decrease:flags=lanczos"
    )
    if add_subtitles:
        cmd = [
            "ffmpeg","-y","-i",str(base_teaser),
            "-vf",f"{scale_expr},subtitles={srt_path}"
        ]
    else:
        cmd = [
            "ffmpeg","-y","-i",str(base_teaser),
            "-vf",scale_expr
        ]
    if BGM_PATH and Path(BGM_PATH).exists():
        cmd += ["-i",BGM_PATH,"-filter_complex","[1:a]volume=0.15[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2[aout]","-map","0:v","-map","[aout]"]
    cmd += ["-c:v","libx264","-preset","veryfast","-crf","23","-c:a","aac","-b:a","128k","-shortest",str(final_output)]
    subprocess.run(cmd, check=True)
    print("🎬 Final teaser saved to", final_output)
    return final_output