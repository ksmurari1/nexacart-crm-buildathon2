"""NexaCart Support Desk custom CSS."""
import streamlit as st

CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #C5CCE3;
    --card: #FFFFFF;
    --ink: #1E1B4B;
    --muted: #5F678C;
    --line: #AEB8DA;

    --primary: #4F46E5;
    --primary-2: #7C3AED;
    --lotus: #DB2777;
    --lotus-soft: #FDF2F8;
    --lotus-line: #FBCFE8;
    --sky: #0EA5E9;
    --sky-soft: #E0F2FE;
    --sky-line: #BAE6FD;
    --indigo-soft: #EEF2FF;
    --indigo-line: #C7D2FE;

    --ok-bg: #ECFDF5;
    --ok-line: #A7F3D0;
    --ok: #047857;

    --esc-bg: #FFF1F5;
    --esc-line: #FBCFE8;
    --esc: #BE123C;

    --shadow: 14px 14px 34px 22px rgba(249, 146, 129, .55);
}

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
    color: var(--ink);
}

.stApp {
    background:    #C5CCE3,
    background-attachment: fixed;
}
h1, h2, h3, h4 {
    font-family: 'Outfit', sans-serif !important;
    letter-spacing: -.02em;
    color: var(--ink);
}

.block-container {
    padding-top: 3.2rem;
    max-width: 1360px;
}

[data-testid="stHeader"] {
    background: transparent;
}

/* ------------------------------------------------------------------ Hero */
.hero {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1.5rem;
    padding: 1.4rem 1.8rem;
    border-radius: 22px;
    margin-bottom: 1rem;
    color: #FFFFFF;
    background:
        radial-gradient(circle at 94% 0%, rgba(56, 189, 248, .55), transparent 42%),
        radial-gradient(circle at 68% 130%, rgba(244, 114, 182, .55), transparent 46%),
        linear-gradient(115deg, #312E81 0%, #4F46E5 55%, #6D5BF0 100%);
    box-shadow: 0 20px 40px -22px rgba(79, 70, 229, .7);
}

.kicker {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: .2em;
    text-transform: uppercase;
    color: #C7D2FE;
}

.hero h1 {
    font-size: 2rem;
    margin: .25rem 0 .35rem 0;
    padding: 0;
    color: #FFFFFF !important;
}

.hero p {
    color: #E0E7FF !important;
    margin: 0 !important;
    max-width: 680px;
    font-size: .92rem;
}

/* Model and status pill */
.pill {
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    padding: .4rem .8rem;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    border: 1px solid var(--line);
    background: #FFFFFF;
    white-space: nowrap;
}

.hero .pill {
    background: rgba(255, 255, 255, .16);
    border-color: rgba(255, 255, 255, .4);
    color: #FFFFFF;
    backdrop-filter: blur(6px);
}

.dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}

/* --------------------------------------------------------- Dashboard metrics */
.stat {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: .9rem 1.1rem;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: .6rem;
    box-shadow: 0 8px 20px -16px rgba(49, 46, 129, .6);
}

.stat::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: var(--a);
}

.stat .v {
    font-family: 'Outfit';
    font-size: 1.8rem;
    font-weight: 600;
    line-height: 1;
}

.stat .l {
    font-size: 12px;
    color: var(--muted);
    margin-top: .35rem;
    font-weight: 500;
}

.stat .ic {
    width: 38px;
    height: 38px;
    border-radius: 12px;
    display: grid;
    place-items: center;
    font-size: 1.05rem;
    background: #EEF2FF;
    background: color-mix(in srgb, var(--a) 13%, white);
    color: var(--a);
    flex: none;
}

/* ----------------------------------------------------------- Section headings */
.panel-h {
    display: flex;
    align-items: center;
    gap: .55rem;
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    font-size: 1.12rem;
    color: var(--ink);
    margin: .2rem 0 .65rem 0;
}

.panel-h .bar {
    width: 6px;
    height: 1.15rem;
    border-radius: 4px;
    background: linear-gradient(180deg, #4F46E5, #EC4899);
}

.panel-h small {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 500;
    font-size: 12px;
    color: var(--muted);
    margin-left: .25rem;
}

/* ------------------------------------------------- Agent pipeline (horizontal) */
.agent-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: .85rem .95rem .9rem;
    position: relative;
    overflow: hidden;
    min-height: 140px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 8px 20px -16px rgba(49, 46, 129, .6);
    transition: border-color .25s, box-shadow .25s;
}

.agent-card::before {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    height: 4px;
    background: var(--a);
}

.agent-card .ac-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: .45rem;
}

.agent-card .ac-num {
    width: 30px;
    height: 30px;
    border-radius: 10px;
    display: grid;
    place-items: center;
    font-family: 'Outfit';
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--a);
    background: #EEF2FF;
    background: color-mix(in srgb, var(--a) 13%, white);
}

.agent-card .ac-step {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .12em;
    color: var(--muted);
}

.agent-card .ac-title {
    font-weight: 700;
    font-size: .92rem;
    line-height: 1.2;
}

.agent-card .ac-role {
    font-size: 11.5px;
    color: var(--muted);
    line-height: 1.35;
    margin-top: .2rem;
    flex: 1;
}

.agent-card .s {
    align-self: flex-start;
    margin-top: .6rem;
    font-size: 10.5px;
    font-weight: 700;
    padding: .22rem .6rem;
    border-radius: 999px;
    letter-spacing: .05em;
}

.agent-card.running {
    border-color: var(--a);
    animation: glow 1.4s infinite;
}

.agent-card.done {
    background: linear-gradient(180deg, #FFFFFF 0%, #F6F9FF 100%);
}

.s-waiting {
    background: #EEF2FF;
    color: #6B7299;
}

.s-running {
    background: #E0F2FE;
    color: #0369A1;
    animation: pulse 1.2s infinite;
}

.s-done {
    background: #DCFCE7;
    color: #166534;
}

.s-error {
    background: #FEF3C7;
    color: #92400E;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: .45; }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, .0); }
    50% { box-shadow: 0 0 0 5px rgba(99, 102, 241, .22); }
}

/* ----------------------------------------------------- Classification chips */
.chips span {
    display: inline-block;
    font-size: 12px;
    font-weight: 600;
    padding: .2rem .6rem;
    border-radius: 999px;
    background: var(--indigo-soft);
    color: #3730A3;
    border: 1px solid var(--indigo-line);
    margin: 0 .3rem .3rem 0;
}

/* ------------------------------------------------ Chat window (customer reply) */
.chat {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 20px;
    overflow: hidden;
    box-shadow: var(--shadow);
    min-height: 520px;
    display: flex;
    flex-direction: column;
}

.chat-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: .8rem;
    padding: .8rem 1.1rem;
    background: linear-gradient(100deg, #EEF2FF 0%, #FDF2F8 62%, #E0F2FE 100%);
    border-bottom: 1px solid var(--line);
}

.chat-who {
    display: flex;
    align-items: center;
    gap: .65rem;
}

.chat-who b {
    display: block;
    font-size: .92rem;
    line-height: 1.15;
}

.chat-who small {
    font-size: 11.5px;
    color: var(--muted);
}

.avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-size: 1rem;
    font-weight: 700;
    color: #FFFFFF;
    flex: none;
}

.avatar.ai {
    background: linear-gradient(135deg, #4F46E5, #EC4899);
}

.avatar.cu {
    background: linear-gradient(135deg, #38BDF8, #6366F1);
}

.chat-body {
    padding: 1.1rem 1.1rem .8rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    flex: 1;
    background: linear-gradient(180deg, #FFFFFF 0%, #FAFAFF 100%);
}

.msg {
    display: flex;
    gap: .6rem;
    align-items: flex-end;
    max-width: 94%;
}

.msg.cu {
    align-self: flex-start;
}

.msg.ai {
    align-self: flex-end;
    flex-direction: row-reverse;
}

.bubble {
    padding: .75rem .95rem;
    border-radius: 16px;
    font-size: .92rem;
    line-height: 1.6;
    border: 1px solid;
}

.bubble .who {
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: .25rem;
}

.msg.cu .bubble {
    background: var(--sky-soft);
    border-color: var(--sky-line);
    border-bottom-left-radius: 4px;
}

.msg.ai .bubble {
    background: var(--indigo-soft);
    border-color: var(--indigo-line);
    border-bottom-right-radius: 4px;
}

.chat.esc .msg.ai .bubble {
    background: var(--lotus-soft);
    border-color: var(--lotus-line);
}

.chat-foot {
    padding: .8rem 1.1rem 1rem;
    border-top: 1px dashed var(--line);
    background: #FBFBFF;
    display: flex;
    flex-direction: column;
    gap: .6rem;
}

.conf-row {
    display: flex;
    align-items: center;
    gap: .6rem;
    font-size: 12px;
    color: var(--muted);
    font-weight: 600;
}

.conf {
    flex: 1;
    height: 8px;
    border-radius: 99px;
    background: #E5E7FB;
    overflow: hidden;
}

.conf > i {
    display: block;
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, #38BDF8, #6366F1, #EC4899);
}

.src-row {
    font-size: 12px;
    color: var(--muted);
}

.src {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    padding: .15rem .5rem;
    border-radius: 7px;
    background: var(--sky-soft);
    color: #075985;
    border: 1px solid var(--sky-line);
    margin: 0 .3rem .25rem 0;
}

.reason {
    background: var(--esc-bg);
    border: 1px solid var(--esc-line);
    color: #9D174D;
    border-radius: 10px;
    padding: .5rem .75rem;
    font-size: 12.5px;
}

.badge {
    display: inline-block;
    font-weight: 800;
    font-size: 11.5px;
    letter-spacing: .08em;
    padding: .35rem .8rem;
    border-radius: 999px;
    white-space: nowrap;
}

.badge.ok {
    background: #059669;
    color: #FFFFFF;
}

.badge.esc {
    background: #BE185D;
    color: #FFFFFF;
}

.chat-empty {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    gap: .4rem;
    padding: 2.5rem 1.5rem;
    color: var(--muted);
    background:
        radial-gradient(circle at 50% 30%, rgba(99, 102, 241, .08), transparent 55%),
        linear-gradient(180deg, #FFFFFF 0%, #FAFAFF 100%);
}

.chat-empty .big {
    font-size: 2.6rem;
}

.chat-empty b {
    color: var(--ink);
    font-family: 'Outfit', sans-serif;
    font-size: 1.1rem;
}

.chat-empty span {
    font-size: 13px;
    max-width: 320px;
}

.chat-empty.working .big {
    animation: pulse 1.2s infinite;
}

/* -------------------------------------------------------- Knowledge evidence */
.passage {
    background: #F5F7FF;
    border: 1px solid var(--indigo-line);
    border-left: 4px solid var(--primary);
    border-radius: 12px;
    padding: .7rem .9rem;
    margin-bottom: .5rem;
    font-size: 13px;
}

.passage b {
    color: #3730A3;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
}

/* ------------------------------------------------------------ Complaint form */
div[data-testid="stForm"] {
    background: #FFFFFF;
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 1.2rem;
    box-shadow: var(--shadow);
}

.stTextInput [data-baseweb="input"],
.stTextArea [data-baseweb="textarea"] {
    background: #F8F9FF;
    border: 1px solid var(--line);
    border-radius: 10px;
}

.stTextInput [data-baseweb="input"]:focus-within,
.stTextArea [data-baseweb="textarea"]:focus-within {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(79, 70, 229, .15);
}

/* Sample complaint pills */
button[data-testid="stBaseButton-pills"] {
    border-radius: 999px;
    border: 1px solid var(--indigo-line);
    background: #FFFFFF;
    font-weight: 600;
}

button[data-testid="stBaseButton-pills"]:hover {
    border-color: var(--lotus);
    color: var(--lotus);
}

button[data-testid="stBaseButton-pillsActive"] {
    border-radius: 999px;
    border: 1px solid var(--primary);
    background: var(--indigo-soft);
    color: #3730A3;
    font-weight: 700;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    border-radius: 10px;
    font-weight: 600;
}

.stFormSubmitButton > button,
button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
    color: #FFFFFF;
    border: 0;
    height: 2.9rem;
    box-shadow: 0 10px 20px -12px rgba(79, 70, 229, .9);
}

.stFormSubmitButton > button p,
button[data-testid="stBaseButton-primary"] p {
    color: #FFFFFF;
}

.stFormSubmitButton > button:hover,
button[data-testid="stBaseButton-primary"]:hover {
    background: linear-gradient(90deg, #4338CA 0%, #DB2777 100%);
    color: #FFFFFF;
    border: 0;
}

/* ------------------------------------------------------- Navigation + sub tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: .3rem;
    background: rgba(255, 255, 255, .78);
    padding: .3rem;
    border-radius: 14px;
    border: 1px solid var(--line);
}

.stTabs [data-baseweb="tab"] {
    height: auto;
    padding: .5rem 1rem;
    border-radius: 10px;
    font-family: 'Outfit';
    font-size: 1rem;
    color: var(--muted);
    background: transparent;
}

.stTabs [data-baseweb="tab"] p {
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(100deg, #4F46E5, #7C3AED);
}

.stTabs [aria-selected="true"] p {
    color: #FFFFFF !important;
}

.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    display: none;
}

.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1rem;
}

/* Misc widgets */
[data-testid="stExpander"] details {
    border-radius: 12px;
    border: 1px solid var(--line);
    background: #FFFFFF;
}

[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: .8rem 1rem;
}

[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Force solid white cards so shapes stand out on the flat background */
.stat,
.agent-card,
.agent-card.done,
.chat,
div[data-testid="stForm"],
[data-testid="stExpander"] details,
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #AEB8DA !important;
    box-shadow: 0 6px 16px -8px rgba(30, 27, 75, .35) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF !important;
    border: 1px solid #AEB8DA !important;
}

.passage {
    background: #FFFFFF !important;
}

/* ---- Page background: flat, mid-tone, applied to every Streamlit layer ---- */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main,
.main {
    background: #B4BEDC !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

/* ---- Stronger borders so every card has a clear outline ---- */
:root {
    --line: #8592BD;
}

.stat,
.agent-card,
.agent-card.done,
.chat,
div[data-testid="stForm"],
[data-testid="stExpander"] details,
[data-testid="stMetric"],
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF !important;
    border: 1.5px solid #8592BD !important;
    box-shadow: 0 6px 16px -8px rgba(30, 27, 75, .4) !important;
}

/* ---- Input boxes: white instead of Streamlit's light blue ---- */
.stTextInput [data-baseweb="input"],
.stTextInput [data-baseweb="input"] > div,
.stTextInput input,
.stTextArea [data-baseweb="textarea"],
.stTextArea [data-baseweb="textarea"] > div,
.stTextArea textarea {
    background: #FFFFFF !important;
}

.stTextInput [data-baseweb="input"],
.stTextArea [data-baseweb="textarea"] {
    border: 1.5px solid #8592BD !important;
}

/* ---- Sample complaint pills ---- */
button[data-testid="stBaseButton-pills"] {
    background: #FFFFFF !important;
    border: 1.5px solid #8592BD !important;
}
/* ---- Page title above the hero ---- */
.block-container {
    padding-top: 1rem !important;
}

.block-container::before {
    content: "AI Customer Support Automation";
    display: block;
    text-align: center;
    font-family: 'Outfit', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -.01em;
    color: #4F46E5;
    margin: 0 0 1rem 0;
}
</style>
"""

def inject_styles():
    st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)
