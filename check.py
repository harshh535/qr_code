# check.py
import streamlit as st
from PIL import Image
import numpy as np
import cv2
import hashlib
import requests

st.title("🔍 Verify QR Code")

db_url = st.secrets["firebase"]["databaseURL"].rstrip("/")

def checksum_of(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def decode_qr(pil_img: Image.Image):
    cv_img = cv2.cvtColor(np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2BGR)
    detector = cv2.QRCodeDetector()
    data, pts, _ = detector.detectAndDecode(cv_img)
    return data if pts is not None and data else None

upload = st.file_uploader("Upload a QR code image", type=["png","jpg","jpeg"])
if upload:
    img = Image.open(upload)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    qr_content = decode_qr(img)
    if not qr_content:
        st.warning("⚠️ No QR code detected.")
    else:
        st.write("**QR Content:**", qr_content)
        cs = checksum_of(qr_content)
        st.write("**Computed Checksum:**", cs)

        # fetch all entries from RTDB
        resp = requests.get(f"{db_url}/qr_checksums.json")
        records = resp.json() or {}
        safe = any(rec.get("checksum") == cs for rec in records.values())

        if safe:
            st.success("✅ This QR is known & safe.")
        else:
            st.error("❌ QR not recognized or unsafe.")
