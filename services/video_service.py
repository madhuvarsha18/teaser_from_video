import os
import yt_dlp


def download_video(url, output_dir="downloads"):
    """
    Download a YouTube video and return local path.
    """

    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "merge_output_format": "mp4",
        "quiet": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            video_path = ydl.prepare_filename(info)

            base = os.path.splitext(video_path)[0]

            mp4_path = base + ".mp4"

            if os.path.exists(mp4_path):
                return mp4_path

            return video_path

    except Exception as e:
        raise Exception(f"Video download failed: {str(e)}")


def validate_video(video_path):
    """
    Check if video exists.
    """

    if not os.path.exists(video_path):
        raise FileNotFoundError(
            f"Video not found: {video_path}"
        )

    return True


def get_video_name(video_path):
    """
    Extract filename only.
    """

    return os.path.basename(video_path)


def create_project_folders():
    """
    Create required folders.
    """

    folders = [
        "downloads",
        "clips",
        "audio",
        "outputs",
        "metadata",
        "subtitles",
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    return folders


def cleanup_temp_files(folder):
    """
    Remove temporary files.
    """

    if not os.path.exists(folder):
        return

    for file in os.listdir(folder):
        try:
            os.remove(
                os.path.join(folder, file)
            )
        except:
            pass


def save_uploaded_video(uploaded_file):
    """
    Save Streamlit uploaded file.
    """

    create_project_folders()

    file_path = os.path.join(
        "downloads",
        uploaded_file.name
    )

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path
