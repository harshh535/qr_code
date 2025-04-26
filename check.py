import streamlit as st
from PIL import Image
import numpy as np
import cv2
import hashlib
import requests

DB_URL = st.secrets["firebase"]["databaseURL"].rstrip("/")

def checksum_of(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def check_qr():
    st.header("🔍 Verify QR Code")
    upload = st.file_uploader("Upload a QR code image", type=["png", "jpg", "jpeg"])
    if not upload:
        return

    img = Image.open(upload)
    st.image(img, caption="Uploaded QR", use_column_width=True)

    # Decode using OpenCV
    cv_img = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
    detector = cv2.QRCodeDetector()
    data, pts, _ = detector.detectAndDecode(cv_img)
    if not data:
        st.warning("⚠️ No QR code detected.")
        return

    st.write("**QR content:**", data)
    cs = checksum_of(data)
    st.write("**Computed checksum:**", cs)

    # Fetch all saved checksums
    resp = requests.get(f"{DB_URL}/qr_checksums.json")
    if not resp.ok:
        st.error(f"Error fetching DB: {resp.status_code}")
        return
    records = resp.json() or {}

    # Look for a match
    found = any(rec.get("checksum") == cs for rec in records.values())
    if found:
        st.success("✅ This QR is known & safe.")
    else:
        st.error("❌ QR not recognized.")
