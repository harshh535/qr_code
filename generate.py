import streamlit as st
import qrcode, io, hashlib
from datetime import datetime
import pyrebase

st.set_page_config(page_title="Generate QR", layout="wide")
st.title("🔧 Generate QR Code")

# init pyrebase client from secrets
firebase = pyrebase.initialize_app(st.secrets["firebase"])
db = firebase.database()

def checksum_of(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def make_qr(text: str):
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(text)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

content = st.text_input("Enter text to embed in QR:")

if st.button("Generate"):
    if not content:
        st.error("Please enter some content.")
    else:
        cs      = checksum_of(content)
        qr_img  = make_qr(content)

        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        buf.seek(0)

        st.image(buf, caption="Generated QR", use_column_width=True)
        st.write("**Content:**", content)
        st.write("**Checksum:**", cs)

        # push to RTDB
        db.child("qr_checksums").push({
            "content":   content,
            "checksum":  cs,
            "timestamp": datetime.utcnow().isoformat()
        })

        st.success("✅ Stored to Firebase!")
        st.download_button(
            "📥 Download QR Code",
            data=buf,
            file_name="qr_code.png",
            mime="image/png"
        )

