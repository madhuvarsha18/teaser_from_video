import os
import subprocess
from functools import lru_cache
from pathlib import Path
from .config import YT_DLP_KNOWN_PLATFORMS, YT_DLP_COOKIES_FILE
def _looks_like_url(video_source: str) -> bool:
    return video_source.strip().lower().startswith(("http://", "https://"))
@lru_cache(maxsize=8)
def _video_has_audio(video_path_str: str) -> bool:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a",
             "-show_entries", "stream=index", "-of", "csv=p=0", video_path_str],
            capture_output=True, text=True, check=True,
        )
        return bool(result.stdout.strip())
    except Exception as e:
        print(f"⚠️ Could not probe audio streams for {video_path_str} ({e}); assuming no audio.")
        return False
def _repair_seek_index(video_path: Path) -> None:
    repaired = video_path.with_name(video_path.stem + "_repaired.mp4")
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(video_path), "-c", "copy", "-movflags", "+faststart", str(repaired)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
        )
        if repaired.exists() and repaired.stat().st_size > 0:
            repaired.replace(video_path)
    except subprocess.CalledProcessError:
        if repaired.exists():
            repaired.unlink(missing_ok=True)
def download_video(video_source: str) -> Path:
    output_path = Path("input_video.mp4")
    if output_path.exists():
        return output_path
    if _looks_like_url(video_source):
        cmd = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/bestvideo+bestaudio/best",
            "--merge-output-format", "mp4",
            "-o", str(output_path),
            video_source,
        ]
        if YT_DLP_COOKIES_FILE and Path(YT_DLP_COOKIES_FILE).exists():
            cmd += ["--cookies", YT_DLP_COOKIES_FILE]
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            known = any(p in video_source for p in YT_DLP_KNOWN_PLATFORMS)
            hint = (
                "This looks like a recognized platform — the content may be private, "
                "age-restricted, or region-locked. Try setting YT_DLP_COOKIES_FILE to a "
                "logged-in browser cookies.txt export."
                if known else
                "yt-dlp may not have an extractor for this site, or the link requires login. "
                "See supported sites: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md"
            )
            raise RuntimeError(f"Failed to download video from '{video_source}'. {hint}") from e
        _repair_seek_index(output_path)
        return output_path
    local_path = Path(video_source)
    if not local_path.exists():
        raise FileNotFoundError(f"Video not found: {video_source}")
    return local_path
def extract_audio(video_path, audio_out=None):
    if not os.path.exists(video_path):
        return None
    if audio_out is None:
        base = os.path.splitext(video_path)[0]
        audio_out = f"{base}_audio.mp3"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", video_path, "-vn", "-acodec", "mp3", audio_out],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return audio_out
    except subprocess.CalledProcessError:
        return None