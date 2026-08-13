import os

from models.model_loader import get_whisper_model

whisper_model = get_whisper_model()


def transcribe_clip(audio_path):
    """
    Transcribe audio using Whisper.
    """

    try:
        segments, info = whisper_model.transcribe(
            audio_path,
            beam_size=5
        )

        transcript_parts = []

        segment_data = []

        for segment in segments:

            transcript_parts.append(
                segment.text.strip()
            )

            segment_data.append(
                {
                    "start": round(segment.start, 2),
                    "end": round(segment.end, 2),
                    "text": segment.text.strip()
                }
            )

        transcript = " ".join(
            transcript_parts
        )

        return {
            "transcript": transcript,
            "segments": segment_data,
            "language": info.language
        }

    except Exception as e:

        print(
            f"Transcription failed: {e}"
        )

        return {
            "transcript": "",
            "segments": [],
            "language": "unknown"
        }


def transcribe_multiple_clips(clips):
    """
    Transcribe multiple audio clips.
    """

    results = []

    for clip in clips:

        result = transcribe_clip(
            clip["audio_path"]
        )

        results.append(
            {
                **clip,
                **result
            }
        )

    return results


def get_word_count(transcript):
    """
    Count words.
    """

    if not transcript:
        return 0

    return len(
        transcript.split()
    )


def calculate_speech_density(
    transcript,
    duration
):
    """
    Words per second.
    """

    if duration <= 0:
        return 0

    word_count = get_word_count(
        transcript
    )

    return round(
        word_count / duration,
        2
    )


def extract_keywords(transcript):
    """
    Simple keyword extraction.
    """

    if not transcript:
        return []

    words = transcript.lower().split()

    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "to",
        "of",
        "for",
        "and",
        "or",
        "in",
        "on",
        "at",
        "with",
        "this",
        "that"
    }

    keywords = []

    for word in words:

        clean_word = word.strip(
            ".,!?;:"
        )

        if (
            len(clean_word) > 3
            and clean_word not in stop_words
        ):
            keywords.append(
                clean_word
            )

    return list(
        set(keywords)
    )[:15]


def build_transcript_metadata(
    transcript,
    duration
):
    """
    Metadata for ranking.
    """

    return {
        "word_count": get_word_count(
            transcript
        ),
        "speech_density":
        calculate_speech_density(
            transcript,
            duration
        ),
        "keywords":
        extract_keywords(
            transcript
        )
    }


def save_transcript(
    transcript,
    output_file
):
    """
    Save transcript text.
    """

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(transcript)

    return output_file
