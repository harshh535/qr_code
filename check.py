import streamlit as st
from PIL import Image
import numpy as np
import cv2
import hashlib
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

def decode_qr(pil_img: Image.Image):
    cv_img = cv2.cvtColor(np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2BGR)
    detector = cv2.QRCodeDetector()
    data, pts, _ = detector.detectAndDecode(cv_img)
    return data if pts is not None and data else None

st.set_page_config(page_title="Check QR", layout="wide")
st.title("🔍 Verify QR Code")

upload = st.file_uploader("Upload a QR code image", type=["png","jpg","jpeg"])
if upload:
    img = Image.open(upload)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    qr_content = decode_qr(img)
    if not qr_content:
        st.warning("⚠️ No QR code detected.")
    else:
        st.write("**QR content:**", qr_content)
        cs = checksum_of(qr_content)
        st.write("**Computed checksum:**", cs)

        # fetch all
        records = ref.get() or {}
        found = any(r.get("checksum")==cs for r in records.values())
        if found:
            st.success("✅ This QR is known & safe.")
        else:
            st.error("❌ QR not recognized.")


