import streamlit as st

st.header("About This App")
st.write("""
This web application allows you to generate a QR code from any text, URL, or image link.
The generated QR code’s checksum is saved in Firebase.

On the Check page, you can upload a QR code image to verify if its checksum exists in Firebase.
If found, it indicates that the link or photo is safe.
""")
