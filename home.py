import streamlit as st
import importlib

st.set_page_config(page_title="QR Code Checker App", layout="wide")

# Sidebar navigation
page = st.sidebar.radio("Select Page", ["Home","About", "Generate", "Check"],index=0)

if page == "Home":
    st.header("Welcome to the QR Code Checker App")
    st.write("Please select a page from the sidebar.")


if page=="About":
    st.header("About This App")
    st.write("""
        This web application allows you to generate a QR code from any text, URL, or image link.
        The generated QR code’s checksum is saved in Firebase.

        On the Check page, you can upload a QR code image to verify if its checksum exists in Firebase.
        If found, it indicates that the link or photo is safe.
        """)

elif page == "Generate":
    generate = importlib.import_module("generate")
    generate.generate_qr_page()

elif page == "Check":
    check = importlib.import_module("check")
    check.check_qr()

