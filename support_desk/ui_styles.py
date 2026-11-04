"""NexaCart Support Desk custom CSS (modularized; styling content preserved)."""
import streamlit as st

from support_desk.styles.base import CSS_BASE
from support_desk.styles.hero import CSS_HERO
from support_desk.styles.dashboard_metrics import CSS_DASHBOARD_METRICS
from support_desk.styles.section_headings import CSS_SECTION_HEADINGS
from support_desk.styles.agent_pipeline_horizontal import CSS_AGENT_PIPELINE_HORIZONTAL
from support_desk.styles.classification_chips import CSS_CLASSIFICATION_CHIPS
from support_desk.styles.chat_window_customer_reply import CSS_CHAT_WINDOW_CUSTOMER_REPLY
from support_desk.styles.knowledge_evidence import CSS_KNOWLEDGE_EVIDENCE
from support_desk.styles.complaint_form import CSS_COMPLAINT_FORM
from support_desk.styles.navigation_sub_tabs import CSS_NAVIGATION_SUB_TABS
from support_desk.styles.page_background_flat_mid_tone_applied_to_every_streamlit_layer import CSS_PAGE_BACKGROUND_FLAT_MID_TONE_APPLIED_TO_EVERY_STREAMLIT_LAYER
from support_desk.styles.stronger_borders_so_every_card_has_a_clear_outline import CSS_STRONGER_BORDERS_SO_EVERY_CARD_HAS_A_CLEAR_OUTLINE
from support_desk.styles.input_boxes_white_instead_of_streamlit_s_light_blue import CSS_INPUT_BOXES_WHITE_INSTEAD_OF_STREAMLIT_S_LIGHT_BLUE
from support_desk.styles.sample_complaint_pills import CSS_SAMPLE_COMPLAINT_PILLS
from support_desk.styles.page_title_above_the_hero import CSS_PAGE_TITLE_ABOVE_THE_HERO

CSS = (
    CSS_BASE
    + CSS_HERO
    + CSS_DASHBOARD_METRICS
    + CSS_SECTION_HEADINGS
    + CSS_AGENT_PIPELINE_HORIZONTAL
    + CSS_CLASSIFICATION_CHIPS
    + CSS_CHAT_WINDOW_CUSTOMER_REPLY
    + CSS_KNOWLEDGE_EVIDENCE
    + CSS_COMPLAINT_FORM
    + CSS_NAVIGATION_SUB_TABS
    + CSS_PAGE_BACKGROUND_FLAT_MID_TONE_APPLIED_TO_EVERY_STREAMLIT_LAYER
    + CSS_STRONGER_BORDERS_SO_EVERY_CARD_HAS_A_CLEAR_OUTLINE
    + CSS_INPUT_BOXES_WHITE_INSTEAD_OF_STREAMLIT_S_LIGHT_BLUE
    + CSS_SAMPLE_COMPLAINT_PILLS
    + CSS_PAGE_TITLE_ABOVE_THE_HERO
)


def inject_styles():
    st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)
