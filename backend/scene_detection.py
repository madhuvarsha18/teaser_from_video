from pathlib import Path
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
from .config import SCENE_THRESHOLD, MIN_SCENE_LENGTH, MAX_SCENE_LENGTH, MAX_SCENES
def chunk_video(video_path: Path) -> list:
    video = open_video(str(video_path))
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=SCENE_THRESHOLD))
    scene_manager.detect_scenes(video)
    scenes = scene_manager.get_scene_list()
    chunks = []
    clip_id = 1
    for start, end in scenes:
        s, e = start.get_seconds(), end.get_seconds()
        if e - s < MIN_SCENE_LENGTH:
            if chunks:
                prev_id, prev_s, prev_e = chunks[-1]
                chunks[-1] = (prev_id, prev_s, e)
            continue
        while e - s > MAX_SCENE_LENGTH:
            chunks.append((clip_id, s, s + MAX_SCENE_LENGTH))
            clip_id += 1
            s += MAX_SCENE_LENGTH
        chunks.append((clip_id, s, e))
        clip_id += 1
    if len(chunks) > MAX_SCENES:
        head, tail = chunks[:10], chunks[-5:]
        middle = sorted(chunks[10:-5], key=lambda x: (x[2]-x[1]), reverse=True)[:MAX_SCENES-len(head)-len(tail)]
        chunks = head + middle + tail
    print(f"Video split into {len(chunks)} scene-based chunks.")
    return chunks