import streamlit as st
from PIL import Image
import hashlib
import pyrebase
import cv2
import numpy as np
from pyzbar.pyzbar import decode

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
    """Generate checksum from QR content."""
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def extract_qr_content(pil_img):
    """Extract QR content and bounding box from image using pyzbar."""
    # Ensure image is in RGB mode to avoid OpenCV errors
    pil_img = pil_img.convert("RGB")

    # Convert to OpenCV format
    cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    # Decode QR code
    decoded_objs = decode(cv_img)

    if not decoded_objs:
        return None, None

    # Get first QR code's data and crop region
    data = decoded_objs[0].data.decode("utf-8")
    rect = decoded_objs[0].rect
    x, y, w, h = rect.left, rect.top, rect.width, rect.height
    cropped_qr = cv_img[y:y + h, x:x + w]
    cropped_pil = Image.fromarray(cv2.cvtColor(cropped_qr, cv2.COLOR_BGR2RGB))

    return data, cropped_pil

def check_qr():
    st.header("🧾 Scan QR Code from Camera or Upload")
    st.write("📷 Capture or upload an image containing a QR code. We'll extract and verify it.")

    captured_img = st.camera_input("📸 Capture Image")
    uploaded_img = st.file_uploader("📁 Or Upload QR Code Image", type=["png", "jpg", "jpeg"])

    if captured_img or uploaded_img:
        try:
            # Open image
            img = Image.open(captured_img if captured_img else uploaded_img)
            st.image(img, caption="🖼️ Original Image", use_column_width=True)

            # Process QR
            qr_content, qr_crop = extract_qr_content(img)

            if qr_content is None:
                st.warning("⚠️ No QR code detected in the image.")
                return

            # Show cropped QR code
            st.image(qr_crop, caption="🔍 Extracted QR Code")

            # Generate checksum from QR content
            checksum = get_content_checksum(qr_content)
            st.write("🔑 Checksum (from QR content):", checksum)

            # Fetch checksums from database
            records = db.child("qr_checksums").get().val()
            found = any(record.get("checksum") == checksum for record in records.values()) if records else False

            if found:
                st.success("✅ QR code is safe (checksum found in database).")
                st.info(f"📄 QR Content: {qr_content}")
            else:
                st.error("❌ QR code is unrecognized or unsafe.")

        except Exception as e:
            st.error(f"🚨 Error: {e}")

# Run the app
if __name__ == "__main__":
    check_qr()
