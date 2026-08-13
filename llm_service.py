import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from config.settings import (
    GROQ_API_KEY
)
class GroqLLM:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name="llama-3.1-8b-instant",
            temperature=0.3
        )
    def generate_response(
        self,
        prompt
    ):
        """
        Generic LLM call.
        """
        try:
            response = self.llm.invoke(
                [
                    HumanMessage(
                        content=prompt
                    )
                ]
            )
            return response.content
        except Exception as e:
            print(
                f"LLM Error: {e}"
            )
            return ""
    def rank_clips(
        self,
        clips_metadata,
        target_length=30
    ):
        """
        Ask LLM to select
        teaser-worthy clips.
        """
        prompt = f"""You are an expert teaser generation assistant.Analyze the following video clips and identify the most engaging moments.Consider:1. Business impact 2. Strong hooks 3. Emotional intensity 4. Product benefits 5. Important announcements 6. Technical insights Target teaser length:{target_length} seconds Clip Metadata:{clips_metadata} Return only clip indices in ranked order.Example:[3,1,7,2]"""
        return self.generate_response(
            prompt
        )
    def explain_selection(
        self,
        metadata
    ):
        """
        Generate explanation
        for selected clips.
        """
        prompt = f"""Explain why these clips are suitable for teaser generation. Metadata:{metadata} Provide: - Business impact - Customer relevance - Hook strength - Emotional value"""
        return self.generate_response(
            prompt
        )
# Singleton instance
llm_service = GroqLLM()
def get_llm():
    return llm_service
