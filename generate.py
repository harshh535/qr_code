import streamlit as st
import qrcode
import io
import hashlib
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db

# ─ init Firebase once ─────────────────────────────────────────────────────────
@st.cache_resource
def init_db():
    sa = st.secrets["firebase"]
    cred_dict = {k: v for k, v in sa.items() if k != "databaseURL"}
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        "databaseURL": sa["databaseURL"]
    })
    return db.reference("qr_checksums")

ref = init_db()
# ──────────────────────────────────────────────────────────────────────────────

def checksum_of(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def make_qr(text: str):
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(text)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

st.set_page_config(page_title="Generate QR", layout="wide")
st.title("🔧 Generate QR Code")

content = st.text_input("Enter text/content for your QR code:")
if st.button("Generate"):
    if not content.strip():
        st.error("Please enter some content.")
    else:
        cs = checksum_of(content)
        img = make_qr(content)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        st.image(buf, caption="Generated QR", use_column_width=True)
        st.write("**Content:**", content)
        st.write("**Checksum:**", cs)

        # push to Firebase
        ref.push({
            "content": content,
            "checksum": cs,
            "timestamp": datetime.utcnow().isoformat()
        })

        st.success("✅ Stored to Firebase!")
        st.download_button(
            "📥 Download QR PNG",
            data=buf,
            file_name="qr_code.png",
            mime="image/png"
        )

