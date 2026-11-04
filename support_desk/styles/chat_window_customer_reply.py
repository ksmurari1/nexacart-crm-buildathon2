CSS_CHAT_WINDOW_CUSTOMER_REPLY = r"""
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
"""
