import base64
from functools import lru_cache
from pathlib import Path

import streamlit as st

# Assumes this file is at  <project root>/src/components/header.py
# and your logo is at      <project root>/assets/logo.png
LOGO_PATH = Path(__file__).resolve().parents[2] / "assets" / "logo.png"


@lru_cache(maxsize=1)
def get_logo_src():
    """Return the logo as a base64 data URI (browsers can't load local file paths)."""
    try:
        data = base64.b64encode(LOGO_PATH.read_bytes()).decode()
        return f"data:image/png;base64,{data}"
    except FileNotFoundError:
        return ""


def header_home():

    logo_url = get_logo_src()
    logo_html = f"<img src='{logo_url}' style='height:100px;' />" if logo_url else ""
    
    st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:30px; margin-top:30px">
            {logo_html}
            <h1 style='text-align:center; color:#EEE9DF'>Velora</h1>
        </div>   
                
                """, unsafe_allow_html=True)


def header_dashboard():

    logo_url = get_logo_src()
    logo_html = f"<img src='{logo_url}' style='height:85px;' />" if logo_url else ""
    
    st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:center; gap:10px">
            {logo_html}
            <h2 style='text-align:left; color:#2C3B4D'>SNAP<br/>CLASS</h2>
        </div>   
                
                """, unsafe_allow_html=True)