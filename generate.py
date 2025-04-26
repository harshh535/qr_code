import streamlit as st
import qrcode
import io
import hashlib
from datetime import datetime
import pyrebase

# Firebase Configuration
firebaseConfig = {
    "apiKey": "AIzaSyA49nGgrsHWyEheb1BHWZYVUIdvPoe1a_0",
    "authDomain": "attackprotectqr.firebaseapp.com",
    "projectId": "attackprotectqr",
    "storageBucket": "attackprotectqr.appspot.com",
    "messagingSenderId": "176060142744",
    "appId": "1:176060142744:web:ef980a43ff760832422ced",
    "measurementId": "G-1YHE0ZV9KE",
    "databaseURL": "https://attackprotectqr-default-rtdb.firebaseio.com/"
}

# Initialize Firebase once
@st.cache_resource
def init_firebase():
    return pyrebase.initialize_app(firebaseConfig)

firebase = init_firebase()
db = firebase.database()

def generate_qr_code(content: str):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def get_content_checksum(content: str) -> str:
    """Compute checksum directly from the original text content."""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def generate_qr_page():
    st.header("Generate QR Code")

    content = st.text_input("Enter content to encode in QR:")

    if st.button("Generate"):
        if not content.strip():
            st.error("Please enter some content.")
            return

        try:
            # 1. Generate checksum from content
            checksum = get_content_checksum(content)

            # 2. Generate QR code from content (not from checksum)
            qr_img = generate_qr_code(content)

            # 3. Save image to bytes
            img_bytes = io.BytesIO()
            qr_img.save(img_bytes, format="PNG")
            img_bytes.seek(0)

            # 4. Display QR and info
            st.image(img_bytes, caption="QR Code", use_column_width=True)
            st.write("Content:", content)
            st.write("Checksum (from content):", checksum)

            # 5. Store in Firebase
            db.child("qr_checksums").push({
                "checksum": checksum,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            })

            # 6. Download button
            st.download_button(
                label="Download QR Code",
                data=img_bytes.getvalue(),
                file_name="qr_code.png",
                mime="image/png"
            )

            st.success("QR code generated with content and checksum saved!")

        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    generate_qr_page()
