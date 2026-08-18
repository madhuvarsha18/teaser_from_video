import os
from faster_whisper import WhisperModel
from transformers import BlipProcessor, BlipForConditionalGeneration
from .config import DEVICE, WHISPER_MODEL, WHISPER_COMPUTE_TYPE, IMAGE_CAPTION_MODEL
print(f"Loading models on device='{DEVICE}' (whisper compute_type='{WHISPER_COMPUTE_TYPE}')...")
whisper_model = WhisperModel(WHISPER_MODEL, device=DEVICE, compute_type=WHISPER_COMPUTE_TYPE)
blip_processor = BlipProcessor.from_pretrained(IMAGE_CAPTION_MODEL)
blip_model = BlipForConditionalGeneration.from_pretrained(IMAGE_CAPTION_MODEL).to(DEVICE)
print("Models loaded.")
# ------------------ Groq LLM Integration ------------------
class GroqLLM:
    def __init__(self, model: str = "openai/gpt-oss-20b", temperature: float = 0.2, max_tokens: int = 800, api_key: str = None):
        from langchain_groq import ChatGroq
        groq_api_key = api_key or os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise RuntimeError("GROQ_API_KEY missing. Set it in env or pass as argument.")
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    def chat(self, system: str, user: str) -> str:
        from langchain_core.messages import SystemMessage, HumanMessage
        msgs = []
        if system:
            msgs.append(SystemMessage(content=system))
        msgs.append(HumanMessage(content=user))
        resp = self.llm.invoke(msgs)
        return str(resp.content).strip().replace("\n", " ")