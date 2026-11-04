CSS_HERO = r"""
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
"""
