import streamlit as st

import segno
import io


@st.dialog("Share Class Link")
def share_subject_dialog(subject_name, subject_code):
    app_domain = "https://velora-ai-auto-attendance.streamlit.app/"
    join_url = f"https://{app_domain}/?join-code={subject_code}"     # FIX: added https:// so it's clickable and scans as a link

    st.header(f"Join {subject_name}")     # FIX: was a duplicate "Scan to Join" heading

    qr = segno.make(join_url)

    out = io.BytesIO()

    # NEW: QR colors from the palette (Abyssal Anchorfish Blue on Palladian)
    qr.save(out, kind='png', scale=10, border=1, dark='#1B2632', light='#EEE9DF')

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('### Copy Link')
        st.code(join_url, language="text")
        st.markdown('**Subject code**')     # NEW: label so the second box isn't a mystery
        st.code(subject_code, language="text")
        st.info('Copy this link to share on Whatsapp or Email')

    with col2:
        st.markdown('### Scan to Join')
        st.image(out.getvalue(), caption='QRCODE for class joining')
