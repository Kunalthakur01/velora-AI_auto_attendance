import base64
from functools import lru_cache
from pathlib import Path

import streamlit as st

# ---- EDIT THESE TO MAKE THE FOOTER YOURS ----
FOOTER_TEXT = "Created with ❤️ by"   # your own text
# Assumes this file is at <project root>/src/components/footer.py
# and your footer image is at <project root>/assets/footer.png (set to None for text only)
FOOTER_LOGO_PATH = Path(__file__).resolve().parents[2] / "assets" / "footer.png"
# ----------------------------------------------


@lru_cache(maxsize=1)
def get_footer_logo_src():
    """Return the footer image as a base64 data URI (browsers can't load local file paths)."""
    if not FOOTER_LOGO_PATH:
        return ""
    try:
        data = base64.b64encode(FOOTER_LOGO_PATH.read_bytes()).decode()
        return f"data:image/png;base64,{data}"
    except FileNotFoundError:
        return ""


def _render_footer(text_color):
    logo_src = get_footer_logo_src()
    logo_html = (
        f"<img src='{logo_src}' style='max-height:25px' />"
        if logo_src else ""
    )

    st.markdown(f"""
        <div style="margin-top:2rem; display:flex; flex-direction:column; gap:6px; justify-content:center; align-items:center">
        <p style="font-weight:bold; color:{text_color};">{FOOTER_TEXT}</p>
        {logo_html}
        </div>
                """, unsafe_allow_html=True)


def footer_home():
    # dark blue background -> light text (Palladian)
    _render_footer("#EEE9DF")


def footer_dashboard():
    # light background -> dark text (Blue Fantastic)
    _render_footer("#2C3B4D")