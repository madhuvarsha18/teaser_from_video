import os
import torch
from dotenv import load_dotenv
# ------------------ Config ------------------
load_dotenv()
WHISPER_MODEL = "tiny"
IMAGE_CAPTION_MODEL = "Salesforce/blip-image-captioning-base"
# Automatically use the processor available on the current machine.
# NVIDIA/CUDA machine -> GPU processing with 2 workers.
# CPU-only machine   -> CPU processing with up to 6 workers.
if torch.cuda.is_available():
    DEVICE = "cuda"
    WHISPER_COMPUTE_TYPE = "float16"
    CLIP_ANALYSIS_WORKERS = 2
    print(f"⚡ Using GPU: {torch.cuda.get_device_name(0)} "
          f"({torch.cuda.get_device_properties(0).total_memory // (1024**2)} MB VRAM)")
else:
    DEVICE = "cpu"
    WHISPER_COMPUTE_TYPE = "int8"
    CLIP_ANALYSIS_WORKERS = 6
    print("🖥️ CUDA not available. Using CPU with 6 workers.")
MAX_TEASER_CLIP_LENGTH = 4.0
SCENE_THRESHOLD = 30.0
MIN_SCENE_LENGTH = 3.0
MAX_SCENE_LENGTH = 20.0
MAX_SCENES = 20
ENSURE_COVERAGE = True
MAX_OUTPUT_DIMENSION = 1280
BGM_PATH = None
LLM_CANDIDATE_POOL_SIZE = 20
TARGET_AUDIENCES = [
    "Customer",
    "Investor",
    "Developer",
    "Audience",
    "Student (Adult)",
    "General",
    "Employee",
]
EMOTIONAL_KEYWORDS = [
    "shocking", "reveal", "breaking", "final", "truth", "secret",
    "dramatic", "important", "exclusive", "unbelievable", "surprising"
]
YT_DLP_KNOWN_PLATFORMS = [
    "youtube.com", "youtu.be", "facebook.com", 
    "instagram.com","twitter.com",
]
YT_DLP_COOKIES_FILE = os.getenv("YT_DLP_COOKIES_FILE")  
