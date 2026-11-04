CSS_NAVIGATION_SUB_TABS = r"""
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
"""
