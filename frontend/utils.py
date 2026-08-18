def fmt_time(seconds):
    seconds = max(0, float(seconds or 0))
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
def validate_youtube_url(url):
    return url.strip().lower().startswith(("http://", "https://"))
def normalized_scores(clip, all_clips):
    score_values = [float(c.get("score_hint", 0) or 0) for c in all_clips]
    lo, hi = min(score_values or [0]), max(score_values or [1])
    raw = float(clip.get("score_hint", 0) or 0)
    if hi == lo:
        base = 0.75
    else:
        base = 0.55 + 0.45 * ((raw - lo) / (hi - lo))
    speech = min(1.0, float(clip.get("speech_density", 0) or 0) / 3.0)
    audio = min(1.0, float(clip.get("audio_energy", 0) or 0) / 0.18)
    visual = min(1.0, len(str(clip.get("visual_caption", "")).split()) / 14.0)
    hook = min(1.0, (0.55 * base + 0.25 * speech + 0.20 * visual))
    relevance = min(1.0, 0.65 * base + 0.35 * speech)
    return {
        "overall": round(base * 100),
        "hook": round(hook * 100),
        "emotion": round((0.55 * audio + 0.45 * base) * 100),
        "visual": round(visual * 100),
        "relevance": round(relevance * 100),
    }
def clip_reason(clip, scores):
    transcript = str(clip.get("transcript", ""))
    caption = str(clip.get("visual_caption", ""))
    reasons = []
    if scores["hook"] >= 80:
        reasons.append("strong hook potential")
    if scores["emotion"] >= 75:
        reasons.append("high audio/emotional intensity")
    if scores["visual"] >= 70:
        reasons.append("clear visual context")
    if len(transcript.split()) >= 10:
        reasons.append("useful dialogue")
    if not reasons:
        reasons.append("good overall ranking compared with other scenes")
    return "Selected for " + ", ".join(reasons) + ". " + (
        f'Visual context: {caption}.' if caption else ""
    )