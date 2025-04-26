import streamlit as st
from PIL import Image
import hashlib
import pyrebase
import numpy as np
import cv2

# Firebase Configuration
firebaseConfig = {
    "apiKey": "AIzaSyA49nGgrsHWyEheb1BHWZYVUIdvPoe1a_0",
    "authDomain": "attackprotectqr.firebaseapp.com",
    "projectId": "attackprotectqr",
    "storageBucket": "attackprotectqr.firebasestorage.app",
    "messagingSenderId": "176060142744",
    "appId": "1:176060142744:web:ef980a43ff760832422ced",
    "measurementId": "G-1YHE0ZV9KE",
    "databaseURL": "https://attackprotectqr-default-rtdb.firebaseio.com/"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

def get_content_checksum(content: str) -> str:
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def extract_qr_content_cv2(pil_img):
    open_cv_image = np.array(pil_img.convert('RGB')) 
    open_cv_image = open_cv_image[:, :, ::-1].copy()  # RGB to BGR

    detector = cv2.QRCodeDetector()
    data, vertices_array, _ = detector.detectAndDecode(open_cv_image)

    return data if vertices_array is not None else None

def check_qr():
    st.header("🧾 Upload QR Code Image")
    st.write("📁 Upload an image containing a QR code. We'll scan and verify it.")

    uploaded_img = st.file_uploader("Upload QR Code Image", type=["png", "jpg", "jpeg"])

    if uploaded_img:
        try:
            img = Image.open(uploaded_img)
            st.image(img, caption="🖼️ Uploaded Image", use_column_width=True)

            qr_content = extract_qr_content_cv2(img)

            if qr_content == "":
                st.warning("⚠️ No QR code detected in the image.")
                return

            st.write("📄 QR Content:", qr_content)

            checksum = get_content_checksum(qr_content)
            st.write("🔑 Checksum (from QR content):", checksum)

            records = db.child("qr_checksums").get().val()
            found = any(record.get("checksum") == checksum for record in records.values()) if records else False

            if found:
                st.success("✅ QR code is safe (checksum found in database).")
            else:
                st.error("❌ QR code is unrecognized or unsafe.")

        except Exception as e:
            st.error(f"🚨 Error: {e}")

# Run the app
if __name__ == "__main__":
    check_qr()

