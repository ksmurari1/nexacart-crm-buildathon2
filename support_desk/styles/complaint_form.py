CSS_COMPLAINT_FORM = r"""
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
"""
