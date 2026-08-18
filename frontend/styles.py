import streamlit as st
def inject_css():
    st.markdown(
        """
        <style>
        :root {
            --bg: #0a0d14;
            --panel: #111621;
            --panel-2: #171d2a;
            --line: #293244;
            --muted: #9aa6b8;
            --text: #f4f7fb;
            --accent: #7c5cff;
            --accent2: #27d7b3;
            --warning: #f6c453;
        }
        .stApp { background: var(--bg); color: var(--text); }
        [data-testid="stHeader"] { background: rgba(10,13,20,.85); }
        [data-testid="stSidebar"] { background: #0d111b; border-right: 1px solid var(--line); }
        .block-container { max-width: 1500px; padding-top: 1.3rem; padding-bottom: 4rem; }
        .hero { padding: 1.4rem 0 .8rem; }
        .eyebrow { color: #9e8cff; font-size: .78rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }
        .hero h1 { font-size: 2.55rem; line-height: 1.05; margin: .25rem 0 .45rem; }
        .hero p { color: var(--muted); font-size: 1rem; max-width: 760px; }
        .card { background: var(--panel); border: 1px solid var(--line); border-radius: 18px; padding: 1.15rem; margin-bottom: 1rem; }
        .card h3 { margin: 0 0 .35rem; }
        .muted { color: var(--muted); }
        .metric { background: var(--panel); border: 1px solid var(--line); border-radius: 15px; padding: .9rem 1rem; }
        .metric .value { font-size: 1.45rem; font-weight: 800; }
        .metric .label { color: var(--muted); font-size: .78rem; margin-top: .15rem; }
        .pill { display:inline-block; padding:.22rem .55rem; border-radius:999px; background:#20283a; color:#cdd6e7; font-size:.72rem; font-weight:700; }
        .pill.good { background: rgba(39,215,179,.12); color:#61e5c9; }
        .pill.warn { background: rgba(246,196,83,.12); color:#f6d37c; }
        .clip-card { background: var(--panel); border:1px solid var(--line); border-radius:16px; padding: .95rem; min-height: 190px; }
        .clip-title { display:flex; justify-content:space-between; align-items:center; gap:.5rem; margin-bottom:.65rem; }
        .score { font-size:1.3rem; font-weight:900; color:#8f7cff; }
        .bar { height:7px; background:#252d3d; border-radius:99px; overflow:hidden; margin:.45rem 0 .75rem; }
        .bar > div { height:100%; background:linear-gradient(90deg,#7c5cff,#27d7b3); border-radius:99px; }
        .timeline { display:flex; align-items:flex-start; gap:0; overflow-x:auto; padding: .4rem 0 1rem; }
        .timeline-step { min-width:150px; text-align:center; position:relative; }
        .timeline-step:not(:last-child):after { content:""; position:absolute; top:15px; left:50%; width:100%; height:2px; background:#30394b; z-index:0; }
        .dot { width:30px; height:30px; margin:0 auto .55rem; border-radius:50%; background:#263044; border:2px solid #46526b; display:flex; align-items:center; justify-content:center; position:relative; z-index:1; }
        .done .dot { background:#172f2c; border-color:#27d7b3; }
        .active .dot { background:#241c45; border-color:#7c5cff; box-shadow:0 0 0 5px rgba(124,92,255,.12); }
        .timeline-step strong { display:block; font-size:.8rem; }
        .timeline-step span { color:var(--muted); font-size:.7rem; }
        .chatbox { background:#0f141f; border:1px solid var(--line); border-radius:18px; padding:1rem; max-height:430px; overflow:auto; }
        .bubble-user { background:#282046; border:1px solid #493e72; padding:.7rem .85rem; border-radius:14px 14px 4px 14px; margin:.5rem 0 .5rem 12%; }
        .bubble-ai { background:#171e2b; border:1px solid var(--line); padding:.7rem .85rem; border-radius:14px 14px 14px 4px; margin:.5rem 12% .5rem 0; }
        .why { background:#151b28; border-left:3px solid #7c5cff; border-radius:10px; padding:.8rem; margin-top:.7rem; }
        .llm-why { background:#151b28; border-left:3px solid #27d7b3; border-radius:10px; padding:.9rem; }
        .section-title { margin: 1.2rem 0 .65rem; font-size:1.2rem; font-weight:800; }
        .small { font-size:.78rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )