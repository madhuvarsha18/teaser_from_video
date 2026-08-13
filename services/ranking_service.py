import re
import json
from services.llm_service import get_llm
llm = get_llm()
def normalize_score(value):
    """
    Convert score to safe float.
    """
    try:
        return float(value)
    except:
        return 0.0
def sort_by_score(metadata):
    """
    Sort clips by score_hint.
    """
    return sorted(
        metadata,
        key=lambda x: normalize_score(
            x.get("score_hint", 0)
        ),
        reverse=True
    )
def parse_llm_response(response):
    """
    Convert:
    [3,1,2]
    into
    [3,1,2]
    """
    try:
        numbers = re.findall(
            r"\d+",
            response
        )
        return [
            int(x)
            for x in numbers
        ]
    except:
        return []
def rank_with_llm(
    metadata,
    target_length=30
):
    """
    Ask LLM to rank clips.
    """
    try:
        compact_data = []
        for idx, clip in enumerate(metadata):
            compact_data.append(
                {
                    "index": idx,
                    "score_hint":
                    clip.get(
                        "score_hint",
                        0
                    ),
                    "transcript":
                    clip.get(
                        "transcript",
                        ""
                    ),
                    "visual":
                    clip.get(
                        "visual_description",
                        ""
                    ),
                    "sentiment":
                    clip.get(
                        "sentiment",
                        ""
                    )
                }
            )
        response = llm.rank_clips(
            compact_data,
            target_length
        )
        ranked_indices = (
            parse_llm_response(
                response
            )
        )
        return ranked_indices
    except Exception as e:
        print(
            f"LLM Ranking Error: {e}"
        )
        return []
def select_clips(
    metadata,
    target_length=30
):
    """
    Main clip selection logic.
    """
    if not metadata:
        return []
    # Step 1
    sorted_metadata = (
        sort_by_score(metadata)
    )
    # Step 2
    llm_ranked = rank_with_llm(
        sorted_metadata,
        target_length
    )
    # Step 3
    selected = []
    used_duration = 0
    if llm_ranked:
        for idx in llm_ranked:
            if idx >= len(
                sorted_metadata
            ):
                continue
            clip = sorted_metadata[idx]
            clip_duration = clip.get(
                "duration",
                0
            )
            if (
                used_duration
                + clip_duration
                > target_length
            ):
                continue
            selected.append(
                clip
            )
            used_duration += (
                clip_duration
            )
    # fallback
    if not selected:
        for clip in sorted_metadata:
            clip_duration = clip.get(
                "duration",
                0
            )
            if (
                used_duration
                + clip_duration
                > target_length
            ):
                continue
            selected.append(
                clip
            )
            used_duration += (
                clip_duration
            )
    return selected
def explain_selected_clips(
    selected_clips
):
    """
    Generate explanation
    for UI.
    """
    try:
        explanation = (
            llm.explain_selection(
                selected_clips
            )
        )
        return explanation
    except:
        return (
            "No explanation available"
        )
def build_selection_report(
    selected_clips
):
    """
    Create final report.
    """
    report = []
    for idx, clip in enumerate(
        selected_clips,
        start=1
    ):
        report.append(
            {
                "rank": idx,
                "start":
                clip.get(
                    "start"
                ),
                "end":
                clip.get(
                    "end"
                ),
                "score":
                clip.get(
                    "score_hint"
                ),
                "transcript":
                clip.get(
                    "transcript"
                )
            }
        )
    return report
def save_selection_report(
    selected_clips,
    output_file=
    "metadata/selection_report.json"
):
    """
    Save report.
    """
    report = build_selection_report(
        selected_clips
    )
    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            report,
            f,
            indent=4,
            ensure_ascii=False
        )
    return output_file
