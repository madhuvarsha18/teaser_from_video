import json
import numpy as np
import soundfile as sf

from transformers import pipeline

from config.settings import (
    EMOTIONAL_KEYWORDS
)

# HuggingFace Sentiment Model
sentiment_pipeline = pipeline(
    "sentiment-analysis"
)


def calculate_audio_energy(
    audio_path
):
    """
    RMS Energy of audio.
    Higher energy often indicates
    excitement or emphasis.
    """

    try:

        data, sr = sf.read(audio_path)

        if len(data) == 0:
            return 0

        rms = np.sqrt(
            np.mean(
                np.square(data)
            )
        )

        return float(rms)

    except:
        return 0


def calculate_speech_density(
    transcript,
    duration
):
    """
    Words per second.
    """

    if duration <= 0:
        return 0

    word_count = len(
        transcript.split()
    )

    return round(
        word_count / duration,
        2
    )


def detect_emotional_keywords(
    transcript
):
    """
    Count teaser-worthy keywords.
    """

    transcript_lower = transcript.lower()

    found_keywords = []

    for keyword in EMOTIONAL_KEYWORDS:

        if keyword in transcript_lower:
            found_keywords.append(
                keyword
            )

    return found_keywords


def analyze_sentiment(
    transcript
):
    """
    Sentiment Analysis.
    """

    if not transcript:
        return {
            "label": "NEUTRAL",
            "score": 0
        }

    try:

        result = sentiment_pipeline(
            transcript[:512]
        )[0]

        return result

    except:

        return {
            "label": "NEUTRAL",
            "score": 0
        }


def calculate_score_hint(
    transcript,
    sentiment_score,
    audio_energy,
    keyword_count
):
    """
    Initial ranking score.
    """

    score = 0

    score += sentiment_score * 40

    score += min(
        audio_energy * 50,
        25
    )

    score += keyword_count * 5

    score += min(
        len(transcript.split()) / 5,
        20
    )

    return round(score, 2)


def build_metadata(
    clip,
    transcript,
    visual_caption,
    audio_path
):
    """
    Build clip metadata.
    """

    duration = clip["duration"]

    audio_energy = calculate_audio_energy(
        audio_path
    )

    speech_density = calculate_speech_density(
        transcript,
        duration
    )

    sentiment = analyze_sentiment(
        transcript
    )

    keywords = detect_emotional_keywords(
        transcript
    )

    score_hint = calculate_score_hint(
        transcript,
        sentiment["score"],
        audio_energy,
        len(keywords)
    )

    metadata = {
        "clip_path":
        clip["clip_path"],

        "start":
        clip["start"],

        "end":
        clip["end"],

        "duration":
        duration,

        "transcript":
        transcript,

        "visual_description":
        visual_caption,

        "audio_energy":
        audio_energy,

        "speech_density":
        speech_density,

        "sentiment":
        sentiment["label"],

        "sentiment_score":
        sentiment["score"],

        "keywords":
        keywords,

        "score_hint":
        score_hint
    }

    return metadata


def save_metadata(
    metadata,
    output_file=
    "metadata/video_analysis.json"
):
    """
    Save JSON metadata.
    """

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            metadata,
            f,
            indent=4,
            ensure_ascii=False
        )

    return output_file


def load_metadata(
    file_path=
    "metadata/video_analysis.json"
):
    """
    Load metadata.
    """

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)
