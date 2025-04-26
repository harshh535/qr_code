import streamlit as st
from PIL import Image
import numpy as np
import cv2
import hashlib
import requests
from datetime import datetime

DB_URL = st.secrets["firebase"]["databaseURL"].rstrip("/")

def checksum_of(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def report_as_malicious(content):
    payload = {
        "content": content,
        "reported_at": datetime.utcnow().isoformat()
    }
    resp = requests.post(f"{DB_URL}/malicious.json", json=payload)
    return resp.ok

def check_qr():
    st.header("🔍 Verify QR Code")
    upload = st.file_uploader("Upload a QR code image", type=["png", "jpg", "jpeg"])
    if not upload:
        return

    img = Image.open(upload)
    st.image(img, caption="Uploaded QR", use_column_width=True)

    cv_img = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
    detector = cv2.QRCodeDetector()
    data, pts, _ = detector.detectAndDecode(cv_img)

    if not data:
        st.warning("⚠️ No QR code detected.")
        return

    st.write("**QR content:**", data)
    cs = checksum_of(data)
    st.write("**Computed checksum:**", cs)

    resp = requests.get(f"{DB_URL}/qr_checksums.json")
    records = resp.json() if resp.ok else {}

    found = any(r.get("checksum") == cs for r in records.values()) if records else False

    if found:
        st.success("✅ This QR code is **safe**.")
    else:
        st.warning("⚠️ Suspicious QR code (not found in database).")
        if st.button("🚩 Report as Malicious"):
            if report_as_malicious(data):
                st.success("✅ Reported to Firebase as malicious.")
            else:
                st.error("❌ Failed to report.")

