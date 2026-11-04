CSS_STRONGER_BORDERS_SO_EVERY_CARD_HAS_A_CLEAR_OUTLINE = r"""
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
"""
