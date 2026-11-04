CSS_DASHBOARD_METRICS = r"""
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
"""
