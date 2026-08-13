import os
import subprocess
import soundfile as sf
import numpy as np


def extract_audio(video_path, output_dir="audio"):
    """
    Extract audio from video using FFmpeg.
    """

    os.makedirs(output_dir, exist_ok=True)

    audio_path = os.path.join(
        output_dir,
        "audio.wav"
    )

    command = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        audio_path
    ]

    subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    return audio_path


def load_audio(audio_path):
    """
    Read audio using SoundFile.
    Returns:
        audio_data
        sample_rate
    """

    audio_data, sample_rate = sf.read(audio_path)

    return audio_data, sample_rate


def get_audio_duration(audio_path):
    """
    Calculate audio duration.
    """

    audio_data, sample_rate = sf.read(audio_path)

    duration = len(audio_data) / sample_rate

    return duration


def calculate_audio_energy(audio_path):
    """
    RMS Energy Calculation.
    Used for excitement detection.
    """

    audio_data, sample_rate = sf.read(audio_path)

    if len(audio_data) == 0:
        return 0

    rms = np.sqrt(
        np.mean(
            np.square(audio_data)
        )
    )

    return float(rms)


def normalize_audio(audio_array):
    """
    Normalize between -1 and 1.
    """

    max_val = np.max(np.abs(audio_array))

    if max_val == 0:
        return audio_array

    return audio_array / max_val


def get_audio_statistics(audio_path):
    """
    Useful metadata.
    """

    audio_data, sample_rate = sf.read(audio_path)

    duration = len(audio_data) / sample_rate

    return {
        "sample_rate": sample_rate,
        "duration": duration,
        "samples": len(audio_data),
        "max_amplitude": float(np.max(audio_data)),
        "min_amplitude": float(np.min(audio_data)),
        "mean_amplitude": float(np.mean(audio_data))
    }


def save_audio_metadata(audio_path):
    """
    Build metadata object.
    """

    stats = get_audio_statistics(audio_path)

    return {
        "audio_file": audio_path,
        **stats
    }
