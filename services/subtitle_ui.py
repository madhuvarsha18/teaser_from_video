import os
import subprocess

from config.settings import (
    MAX_TEASER_CLIP_LENGTH
)


def format_time(seconds):

    hours = int(seconds // 3600)

    minutes = int(
        (seconds % 3600) // 60
    )

    secs = int(seconds % 60)

    millis = int(
        (seconds - int(seconds))
        * 1000
    )

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d},"
        f"{millis:03d}"
    )


def generate_srt(
    selected_clips,
    output_file="subtitles/teaser.srt"
):

    os.makedirs(
        "subtitles",
        exist_ok=True
    )

    current_time = 0

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        for idx, clip in enumerate(
            selected_clips,
            start=1
        ):

            transcript = clip.get(
                "transcript",
                ""
            )

            duration = min(
                clip.get(
                    "duration",
                    3
                ),
                MAX_TEASER_CLIP_LENGTH
            )

            start = format_time(
                current_time
            )

            end = format_time(
                current_time + duration
            )

            f.write(
                f"{idx}\n"
            )

            f.write(
                f"{start} --> {end}\n"
            )

            f.write(
                transcript
                + "\n\n"
            )

            current_time += duration

    return output_file


def burn_subtitles(
    video_path,
    subtitle_file,
    output_file
):

    command = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vf",
        f"subtitles={subtitle_file}",
        output_file
    ]

    subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    return output_file
