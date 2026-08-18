import json
from .config import ENSURE_COVERAGE, LLM_CANDIDATE_POOL_SIZE, MAX_TEASER_CLIP_LENGTH
from .models import GroqLLM
# ---------------------- Mathematical Pre-Selection -----------------------
def select_clips_by_score(video_metadata, pool_size=LLM_CANDIDATE_POOL_SIZE):
    if not video_metadata:
        return []
    sorted_clips = sorted(video_metadata, key=lambda x: x["score_hint"], reverse=True)
    hook = sorted_clips[0]
    if not ENSURE_COVERAGE:
        picks = sorted_clips[:pool_size]
        return sorted(picks, key=lambda x: x["start_time"])
    dur = max(c["end_time"] for c in video_metadata)
    intro = [c for c in video_metadata if c["start_time"] < dur*0.33]
    middle = [c for c in video_metadata if dur*0.33 <= c["start_time"] < dur*0.66]
    end = [c for c in video_metadata if c["start_time"] >= dur*0.66]
    def best_clip(clips): return max(clips, key=lambda x: x["score_hint"]) if clips else None
    picks = [hook]
    for pool in (intro, middle, end):
        best = best_clip(pool)
        if best and best["clip_id"] != hook["clip_id"]:
            picks.append(best)
    for c in sorted_clips:
        if c not in picks and len(picks) < pool_size:
            picks.append(c)
    picks = [picks[0]] + sorted(picks[1:], key=lambda x: x["start_time"])
    return picks
# ---------------------- LLM-based Refinement (Tone + Audience) -----------
def _clean_llm_json(raw: str) -> str:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    # Guard against any stray text before/after the JSON object.
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start:end + 1]
    return cleaned.strip()
def llm_select_clips(candidate_clips, tone="Cinematic", target_audience="General", target_length=30):
    """
    Groq-LLM stage: takes the mathematically pre-scored candidate POOL and
    picks/refines the final clip set for the requested tone/style AND
    target_audience, so different tone/audience combinations produce
    different teasers instead of the same math-only result every time.

    Falls back gracefully (chronological math-ranked clips) if the LLM
    call fails or GROQ_API_KEY is missing, so the pipeline never breaks.

    Returns: (chosen_clips_sorted_by_start_time, reasoning_text)
    """
    if not candidate_clips:
        return [], "No candidate clips available."
    simplified = [
        {
            "clip_id": c["clip_id"],
            "start": round(c["start_time"], 1),
            "end": round(c["end_time"], 1),
            "duration": round(c["duration"], 1),
            "transcript": (c["transcript"] or "")[:220],
            "visual": c["visual_caption"],
            "math_score": round(c["score_hint"], 3),
        }
        for c in candidate_clips
    ]
    system_prompt = (
        "You are an expert video teaser editor and story strategist. "
        "You are given candidate video clips with a mathematical importance score "
        "(speech density, audio energy, emotional keywords), transcript and visual description. "
        f"Build a teaser for TONE/STYLE = '{tone}' and TARGET AUDIENCE = '{target_audience}'. "
        f"Target total teaser duration is about {target_length} seconds. "
        "Different audiences and tones must lead to genuinely different clip choices: "
        "e.g. an 'Investor' audience favors clips with results/numbers/impact/credibility, "
        "a 'Developer' audience favors clips with technical detail/how-it-works content, "
        "a 'Customer' audience favors benefit/value/usability moments, "
        "an 'Employee' audience favors culture/process/team moments, "
        "a 'Student (Adult)' audience favors clear explanatory/educational moments, "
        "and 'General'/'Audience' favor the most broadly engaging, high-emotion hook moments. "
        "Use math_score as a helpful signal but not an absolute rule — override it when a clip "
        "better fits the requested tone and audience. "
        "Reply with ONLY a raw JSON object, no markdown fences, no extra commentary, in this exact shape: "
        '{"selected_clip_ids": [int, int, ...], "reasoning": "1-3 sentence explanation"}'
    )
    user_prompt = (
        f"Candidate clips (chronological order not guaranteed here):\n{json.dumps(simplified, indent=2)}\n\n"
        f"Pick the subset of clip_id values (from the list above only) that best fits the tone "
        f"'{tone}' and audience '{target_audience}', keeping combined duration close to {target_length}s."
    )
    try:
        llm = GroqLLM(temperature=0.3, max_tokens=900)
        raw = llm.chat(system_prompt, user_prompt)
        cleaned = _clean_llm_json(raw)
        parsed = json.loads(cleaned)
        ids = parsed.get("selected_clip_ids", [])
        reasoning = parsed.get("reasoning", "")
        valid_ids = {c["clip_id"] for c in candidate_clips}
        ids = [i for i in ids if i in valid_ids]
        chosen = [c for c in candidate_clips if c["clip_id"] in ids]
        if not chosen:
            raise ValueError("LLM returned no valid clip_id matches from the candidate pool.")
        chosen.sort(key=lambda x: x["start_time"])
        return chosen, reasoning or f"Selected via Groq LLM for tone='{tone}', audience='{target_audience}'."
    except Exception as e:
        print("⚠️ Groq clip selection failed, falling back to mathematical ranking:", e)
        fallback_ids = sorted(
            candidate_clips, key=lambda x: x["score_hint"], reverse=True
        )
        running, kept = 0.0, []
        for c in fallback_ids:
            if running >= target_length and kept:
                break
            kept.append(c)
            running += min(c["duration"], MAX_TEASER_CLIP_LENGTH)
        kept.sort(key=lambda x: x["start_time"])
        return kept, f"Fallback to mathematical scoring only (LLM unavailable: {e})"
# ---------------------- Public Selection Entry Point ----------------------
def select_clips(video_metadata, tone="Cinematic", target_audience="General", target_length=30):
    """
    Two-stage selection:
      1) Mathematical scoring narrows the whole video down to a
         chronology-preserving, coverage-balanced candidate POOL.
      2) Groq LLM refines that pool into the final teaser clip set,
         tailored to the requested tone/style AND target_audience.

    Returns: (selected_clips_sorted_by_start_time, llm_reasoning_text)
    """
    pool = select_clips_by_score(video_metadata)
    chosen, reasoning = llm_select_clips(
        pool, tone=tone, target_audience=target_audience, target_length=target_length
    )
    if not chosen:
        chosen = pool
        reasoning = reasoning or "Fell back to the mathematical candidate pool."
    return chosen, reasoning