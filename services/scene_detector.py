import os
import subprocess

from scenedetect import open_video
from scenedetect import SceneManager
from scenedetect.detectors import ContentDetector

from config.settings import (
    SCENE_THRESHOLD,
    MIN_SCENE_LENGTH,
    MAX_SCENE_LENGTH,
    MAX_SCENES
)


def detect_scenes(video_path):
    """
    Detect scene boundaries using PySceneDetect.
    """

    video = open_video(video_path)

    scene_manager = SceneManager()

    scene_manager.add_detector(
        ContentDetector(
            threshold=SCENE_THRESHOLD
        )
    )

    scene_manager.detect_scenes(video)

    scene_list = scene_manager.get_scene_list()

    return scene_list


def filter_scenes(scene_list):
    """
    Remove scenes that are too short or too long.
    """

    filtered = []

    for start_time, end_time in scene_list:

        start_sec = start_time.get_seconds()
        end_sec = end_time.get_seconds()

        duration = end_sec - start_sec

        if duration < MIN_SCENE_LENGTH:
            continue

        if duration > MAX_SCENE_LENGTH:
            continue

        filtered.append(
            (
                round(start_sec, 2),
                round(end_sec, 2)
            )
        )

    return filtered[:MAX_SCENES]


def split_video_into_clips(
    video_path,
    scenes,
    output_dir="clips"
):
    """
    Create scene clips using FFmpeg.
    """

    os.makedirs(output_dir, exist_ok=True)

    clip_paths = []

    for index, (start_sec, end_sec) in enumerate(scenes):

        clip_path = os.path.join(
            output_dir,
            f"clip_{index}.mp4"
        )

        duration = end_sec - start_sec

        command = [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-ss",
            str(start_sec),
            "-t",
            str(duration),
            "-c",
            "copy",
            clip_path
        ]

        subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        clip_paths.append(
            {
                "clip_path": clip_path,
                "start": start_sec,
                "end": end_sec,
                "duration": duration
            }
        )

    return clip_paths


def chunk_video(video_path):
    """
    Main scene detection pipeline.
    """

    print("Detecting scenes...")

    scenes = detect_scenes(video_path)

    scenes = filter_scenes(scenes)

    clips = split_video_into_clips(
        video_path,
        scenes
    )

    print(
        f"Created {len(clips)} clips"
    )

    return clips


def get_scene_summary(clips):
    """
    Build scene metadata.
    """

    summary = []

    for idx, clip in enumerate(clips):

        summary.append(
            {
                "scene_id": idx,
                "start": clip["start"],
                "end": clip["end"],
                "duration": clip["duration"]
            }
        )

    return summary
