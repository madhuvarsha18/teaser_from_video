import os
import cv2
from PIL import Image

from models.model_loader import (
    get_blip_model,
    get_blip_processor
)

blip_model = get_blip_model()
blip_processor = get_blip_processor()


def extract_frame(
    video_path,
    timestamp=None,
    output_dir="frames"
):
    """
    Extract frame from video.
    """

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    cap = cv2.VideoCapture(
        video_path
    )

    total_frames = int(
        cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    duration = (
        total_frames / fps
        if fps > 0
        else 0
    )

    if timestamp is None:
        timestamp = duration / 2

    frame_number = int(
        timestamp * fps
    )

    cap.set(
        cv2.CAP_PROP_POS_FRAMES,
        frame_number
    )

    success, frame = cap.read()

    if not success:
        cap.release()
        return None

    frame_path = os.path.join(
        output_dir,
        f"frame_{int(timestamp)}.jpg"
    )

    cv2.imwrite(
        frame_path,
        frame
    )

    cap.release()

    return frame_path


def generate_caption(
    image_path
):
    """
    BLIP image captioning.
    """

    try:

        image = Image.open(
            image_path
        ).convert("RGB")

        inputs = blip_processor(
            image,
            return_tensors="pt"
        )

        output = blip_model.generate(
            **inputs,
            max_new_tokens=50
        )

        caption = blip_processor.decode(
            output[0],
            skip_special_tokens=True
        )

        return caption

    except Exception as e:

        print(
            f"Caption error: {e}"
        )

        return "No visual description available"


def analyze_visual_context(
    video_path,
    timestamp=None
):
    """
    Complete visual analysis.
    """

    frame_path = extract_frame(
        video_path,
        timestamp
    )

    if frame_path is None:

        return {
            "frame_path": None,
            "caption": ""
        }

    caption = generate_caption(
        frame_path
    )

    return {
        "frame_path": frame_path,
        "caption": caption
    }


def analyze_multiple_clips(
    clips
):
    """
    Analyze many clips.
    """

    results = []

    for clip in clips:

        midpoint = (
            clip["start"]
            + clip["end"]
        ) / 2

        visual = analyze_visual_context(
            clip["clip_path"],
            midpoint
        )

        results.append(
            {
                **clip,
                **visual
            }
        )

    return results


def extract_key_frames(
    video_path,
    count=5,
    output_dir="frames"
):
    """
    Extract multiple frames.
    """

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    cap = cv2.VideoCapture(
        video_path
    )

    total_frames = int(
        cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    duration = (
        total_frames / fps
        if fps > 0
        else 0
    )

    frame_paths = []

    for i in range(count):

        timestamp = (
            duration
            * (i + 1)
            / (count + 1)
        )

        frame_path = extract_frame(
            video_path,
            timestamp,
            output_dir
        )

        if frame_path:
            frame_paths.append(
                frame_path
            )

    cap.release()

    return frame_paths


def build_visual_metadata(
    video_path
):
    """
    Create visual metadata.
    """

    frame_paths = extract_key_frames(
        video_path
    )

    captions = []

    for frame in frame_paths:

        caption = generate_caption(
            frame
        )

        captions.append(
            {
                "frame": frame,
                "caption": caption
            }
        )

    return captions
