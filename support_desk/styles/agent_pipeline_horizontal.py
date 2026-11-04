CSS_AGENT_PIPELINE_HORIZONTAL = r"""
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
"""
