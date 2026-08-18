import html
import json
import os
import streamlit as st
from ..utils import fmt_time
def answer_video_question(query, analysis):
    if not analysis:
        return "I don't have video analysis data yet. Please process a video first."
    terms = [t.lower() for t in query.split() if len(t) > 2]
    ranked = []
    for clip in analysis:
        text = f"{clip.get('transcript','')} {clip.get('visual_caption','')}".lower()
        overlap = sum(1 for term in terms if term in text)
        ranked.append((overlap, float(clip.get('score_hint', 0) or 0), clip))
    ranked.sort(key=lambda x: (x[0], x[1]), reverse=True)
    context = [x[2] for x in ranked[:5]]
    context_text = json.dumps(context, indent=2)
    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "RAG context retrieved successfully, but GROQ_API_KEY is not configured. Add it to your environment to enable the LLM response."
        llm = ChatGroq(groq_api_key=api_key, model_name="openai/gpt-oss-20b", temperature=0.2, max_tokens=700)
        system = "You are a video assistant. Answer only from the supplied video-analysis context. If the context is insufficient, say so. Mention clip IDs and timestamps when useful."
        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=f"Video context:\n{context_text}\n\nQuestion: {query}")])
        return str(response.content).strip()
    except Exception as exc:
        best = context[0] if context else None
        if best:
            return f"I retrieved Clip #{best.get('clip_id')} as the most relevant context ({fmt_time(best.get('start_time'))}–{fmt_time(best.get('end_time'))}). Transcript: {best.get('transcript')}. LLM response unavailable: {exc}"
        return f"I couldn't retrieve a relevant clip. LLM response unavailable: {exc}"
def render_chatbot(analysis):
    st.markdown("<div class='section-title'>🤖 AI Video Assistant</div>", unsafe_allow_html=True)
    st.caption("Ask questions about scenes, dialogue, characters, teaser choices, or why a clip was selected. The UI retrieves relevant clip context before calling the LLM.")
    suggestions = ["Summarize the video", "Which clip has the strongest emotional moment?", "Why was the top clip selected?", "Find the strongest dialogue"]
    cols = st.columns(4)
    for col, suggestion in zip(cols, suggestions):
        with col:
            if st.button(suggestion, key=f"suggest_{suggestion}"):
                st.session_state.last_query = suggestion
    query = st.text_input("Ask your video", value=st.session_state.last_query, placeholder="e.g. Which scene is best for the opening hook?")
    if st.button("Send to AI Assistant 🤖", type="primary", use_container_width=True) and query.strip():
        st.session_state.chat_history.append(("user", query.strip()))
        with st.spinner("Retrieving relevant clips and asking the LLM..."):
            answer = answer_video_question(query.strip(), analysis)
        st.session_state.chat_history.append(("assistant", answer))
        st.session_state.last_query = ""
        st.rerun()
    if st.session_state.chat_history:
        st.markdown("<div class='chatbox'>", unsafe_allow_html=True)
        for role, text in st.session_state.chat_history:
            safe = html.escape(text)
            if role == "user":
                st.markdown(f"<div class='bubble-user'><b>You</b><br>{safe}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='bubble-ai'><b>🤖 SmartClip AI</b><br>{safe}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)