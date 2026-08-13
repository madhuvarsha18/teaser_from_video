import os
import subprocess

from config.settings import (
    MAX_TEASER_CLIP_LENGTH,
    UPSCALE
)


def trim_clip(
    input_clip,
    output_clip,
    max_duration=MAX_TEASER_CLIP_LENGTH
):

    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_clip,
        "-t",
        str(max_duration),
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        output_clip
    ]

    subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    return output_clip


def prepare_selected_clips(
    selected_clips,
    temp_dir="temp_clips"
):

    os.makedirs(
        temp_dir,
        exist_ok=True
    )

    prepared = []

    for idx, clip in enumerate(
        selected_clips
    ):

        output_clip = os.path.join(
            temp_dir,
            f"trimmed_{idx}.mp4"
        )

        trim_clip(
            clip["clip_path"],
            output_clip
        )

        prepared.append(
            output_clip
        )

    return prepared


def create_concat_file(
    clips,
    concat_file="concat.txt"
):

    with open(
        concat_file,
        "w",
        encoding="utf-8"
    ) as f:

        for clip in clips:

            f.write(
                f"file '{os.path.abspath(clip)}'\n"
            )

    return concat_file


def stitch_clips(
    clips,
    output_path="outputs/final_teaser.mp4"
):

    concat_file = create_concat_file(
        clips
    )

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        concat_file,
        "-c",
        "copy",
        output_path
    ]

    subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    return output_path


def upscale_video(
    input_video,
    output_video
):

    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_video,
        "-vf",
        f"scale={UPSCALE}",
        output_video
    ]

    subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    return output_video
