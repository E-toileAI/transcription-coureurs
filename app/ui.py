import csv
import streamlit as st


def style_bubble(timestamp: str, text: str, tag: str = "None"):
    """Affiche une bulle de chat horodatée avec couleur et tag."""
    flag = f" 🚩 {tag}" if tag != "None" else ""
    st.markdown(
        f"""
        <div style="background-color:#1c1c1e;padding:12px;border-radius:12px;
                    margin-bottom:8px;color:white;max-width:75%;word-wrap:break-word;">
            <div style="color:gray;font-size:0.8em">🕒 {timestamp}{flag}</div>
            <div>{text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )