CSS_BASE = r"""
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
"""
