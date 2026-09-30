import streamlit as st
def subject_card(name, code, section, stats=None, footer_callback=None):
    # FIX: `border` now comes BEFORE `border-left`, so the 8px accent stripe is no longer overridden
    html = f"""
        <div style="background:#C9C1B1; border: 1px solid #1B2632; border-left: 8px solid #FFB162; padding:25px; border-radius: 20px; margin-bottom:20px;">
        <h3 style="margin:0; color: #1B2632; font-size: 1.5rem ">{name}</h3>
        <p style="color:#2C3B4D; margin:10px 0;">Code : <span style="background:#2C3B4D; color:#EEE9DF; padding:2px 8px; border-radius:5px;">{code} </span> | Section : {section}</p>
        
        """
    
    if stats:
        html+= """
        <div style="display:flex; gap:8px; flex-wrap:wrap;">
        """
        for icon, label, value in stats:
            html+= f'<div style="background: #A3513926; color:#1B2632; padding:5px 12px; border-radius:12px; font-size:0.9rem">{icon} <b>{value}</b> {label} </div>'
        
        html+= "</div>"

    st.markdown(html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()